from typing import Dict, List, Optional
import ee
import geemap
import dask
from dask import delayed
from satimgproc.utils import load_geometry_from_geojson


class BaseDownloader:
    """
    Abstract base class for satellite image downloaders.

    Handles exporting individual bands or multiple bands in parallel using Dask.
    """

    def __init__(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
        output_path: Optional[str],
    ):
        """
        Initializes the BaseDownloader.

        Parameters:
        - geometry (ee.Geometry): The area of interest.
        - start_date (str): Start date in 'YYYY-MM-DD' format.
        - end_date (str): End date in 'YYYY-MM-DD' format.
        - output_path (str): Output directory for saving images.
        """
        self.geometry = geometry
        self.start_date = start_date
        self.end_date = end_date
        self.output_path = output_path
        self.landsat_Band_folder_path_and_scale = {
            "B2": ["data/landsat/blue.tif", 30],
            "B3": ["data/landsat/green.tif", 30],
            "B4": ["data/landsat/red.tif", 30],
            "B5": ["data/landsat/nir.tif", 30],
            "B6": ["data/landsat/swir1.tif", 30],
            "B7": ["data/landsat/swir2.tif", 30],
            "B8": ["data/landsat/pan.tif", 15],
        }
        self.sentinel_Band_folder_path = {
            "B2": ["data/sentinel/blue.tif", 10],
            "B3": ["data/sentinel/green.tif", 10],
            "B4": ["data/sentinel/red.tif", 10],
            "B8": ["data/sentinel/nir.tif", 10],
        }

    def export_single_band(
        self,
        image: ee.Image,
        band: str,
        band_info: List,
        geometry: ee.Geometry,
    ) -> None:
        """
        Exports a single band image to disk using geemap.

        Parameters:
        - image (ee.Image): Earth Engine image to export.
        - band (str): Band name to extract.
        - band_info (list): List containing [output_path, scale].
        - geometry (ee.Geometry): Clipping geometry.
        """
        output_path, scale = band_info  # Extract output path & scale
        band_image = image.select([band]).clip(geometry)  # Clip to AOI
        geemap.ee_export_image(
            band_image,
            scale=scale,
            filename=output_path,
            region=geometry,
            file_per_band=False,
        )
        print(f"{band} exported")

    def export_image_parallel(
        self,
        image: ee.Image,
        band_dict: Dict[str, List],
        geometry: ee.Geometry,
    ) -> List:
        """
        Exports all specified bands in parallel using Dask.

        Parameters:
        - image (ee.Image): Earth Engine image to export.
        - band_dict (dict): Dictionary with band names and [path, scale] info.
        - geometry (ee.Geometry): Clipping geometry.

        Returns:
        - results (list): Results of Dask compute (mostly None).
        """
        tasks = [
            delayed(self.export_single_band)(image, band, band_info, geometry)
            for band, band_info in band_dict.items()
        ]
        results = dask.compute(*tasks)  # Executes all tasks in parallel
        return results


class LandsatDownloader(BaseDownloader):
    """
    Downloader for Landsat 8 images using Earth Engine.

    Uses simpleComposite() for cloud-free compositing.
    """

    def __init__(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
        cloud_cover: Optional[int] = None,
    ):
        """
        Initializes the LandsatDownloader.

        Parameters:
        - geometry (ee.Geometry): Area of interest.
        - start_date (str): Start date.
        - end_date (str): End date.
        - cloud_cover (float or None): Unused but accepted for interface compatibility.
        """
        super().__init__(geometry, start_date, end_date, output_path=None)
        self.cloud_cover = cloud_cover  # Store cloud cover threshold

    def filter_collection(self) -> ee.Image:
        """
        Filters Landsat 8 Collection 2 Tier 1 images by date and region.

        Returns:
        - ee.Image: Cloud-free composite image.
        """
        l8raw = (
            ee.ImageCollection("LANDSAT/LC08/C02/T1")
            .filterBounds(self.geometry)
            .filterDate(self.start_date, self.end_date)
        )

        # Landsat does not have direct cloud cover metadata, so we use simpleComposite()
        cloud_free = ee.Algorithms.Landsat.simpleComposite(
            collection=l8raw, asFloat=True
        )
        return cloud_free

    def download(self) -> None:
        """
        Downloads all defined Landsat bands in parallel.
        """
        image = self.filter_collection()  # Get the filtered Landsat image

        # Export all bands in parallel using Dask
        self.export_image_parallel(
            image, self.landsat_Band_folder_path_and_scale, self.geometry
        )


class SentinelDownloader(BaseDownloader):
    """
    Downloader for Sentinel-2 images using Earth Engine.

    Filters based on CLOUDY_PIXEL_PERCENTAGE and returns a median composite.
    """

    def __init__(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
        cloud_cover: Optional[int] = None,
    ):
        """
        Initializes the SentinelDownloader.

        Parameters:
        - geometry (ee.Geometry): Area of interest.
        - start_date (str): Start date.
        - end_date (str): End date.
        - cloud_cover (float or None): Maximum allowed cloud cover percentage.
        """
        super().__init__(geometry, start_date, end_date, output_path=None)
        self.cloud_cover = (
            cloud_cover if cloud_cover is not None else 20
        )  # Default: 20% cloud cover

    def filter_collection(self) -> ee.Image:
        """
        Filters Sentinel-2 images by date, region, and cloud cover.

        Returns:
        - ee.Image: Median composite image.
        """
        s2raw = (
            ee.ImageCollection("COPERNICUS/S2")
            .filterBounds(self.geometry)
            .filterDate(self.start_date, self.end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", self.cloud_cover))
        )  # Apply cloud cover filter

        median_image = s2raw.median()  # Take the median composite
        return median_image

    def download(self) -> None:
        """
        Downloads all defined Sentinel-2 bands in parallel.
        """
        image = self.filter_collection()  # Get the filtered Sentinel-2 image

        # Export all bands in parallel using Dask
        self.export_image_parallel(image, self.sentinel_Band_folder_path, self.geometry)


# ---------------------------
# DownloaderManager (with factory + run)
# ---------------------------
class DownloaderManager:
    """
    Factory and controller class for managing Landsat/Sentinel downloads.
    """

    def __init__(
        self,
        dataset: str,
        geojson_path: str,
        start_date: str,
        end_date: str,
        cloud_cover: Optional[int] = None,
    ):
        """
        Initializes the DownloaderManager.

        Parameters:
        - dataset (str): 'landsat' or 'sentinel'.
        - geojson_path (str): Path to GeoJSON file defining area of interest.
        - start_date (str): Start date (YYYY-MM-DD).
        - end_date (str): End date (YYYY-MM-DD).
        - cloud_cover (float or None): Cloud cover threshold for filtering (if applicable).
        """
        self.dataset = dataset.lower()
        self.geojson_path = geojson_path
        self.start_date = start_date
        self.end_date = end_date
        self.cloud_cover = cloud_cover
        self.geometry = load_geometry_from_geojson(geojson_path)

    def get_downloader(self) -> BaseDownloader:
        """
        Returns the appropriate downloader based on the dataset.

        Returns:
        - BaseDownloader subclass instance (LandsatDownloader or SentinelDownloader).
        """
        if self.dataset == "landsat":
            return LandsatDownloader(
                self.geometry, self.start_date, self.end_date, self.cloud_cover
            )
        elif self.dataset == "sentinel":
            return SentinelDownloader(
                self.geometry, self.start_date, self.end_date, self.cloud_cover
            )
        else:
            raise ValueError("Dataset not supported! Choose 'landsat' or 'sentinel'.")

    def run(self) -> None:
        """
        Runs the download process using the selected downloader.
        """
        downloader = self.get_downloader()
        downloader.download()
