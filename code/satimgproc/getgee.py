import ee
import geemap
import dask
from dask import delayed
from satimgproc.utils import load_geometry_from_geojson


class BaseDownloader:
    def __init__(self, geometry, start_date, end_date, output_path):
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

    def export_single_band(self, image, band, band_info, geometry):
        """Exports a single band to a local file asynchronously using given scale and output path."""
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

    def export_image_parallel(self, image, band_dict, geometry):
        """Exports multiple bands in parallel using Dask, with scale & path per band."""
        tasks = [
            delayed(self.export_single_band)(image, band, band_info, geometry)
            for band, band_info in band_dict.items()
        ]
        results = dask.compute(*tasks)  # Executes all tasks in parallel
        return results


class LandsatDownloader(BaseDownloader):
    def __init__(self, geometry, start_date, end_date, cloud_cover=None):
        super().__init__(geometry, start_date, end_date, output_path=None)
        self.cloud_cover = cloud_cover  # Store cloud cover threshold

    def filter_collection(self):
        """Filters the Landsat 8 image collection and applies cloud filtering if needed."""
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

    def download(self):
        """Main function to filter images and export them in parallel."""

        image = self.filter_collection()  # Get the filtered Landsat image

        # Export all bands in parallel using Dask
        self.export_image_parallel(
            image, self.landsat_Band_folder_path_and_scale, self.geometry
        )


class SentinelDownloader(BaseDownloader):
    def __init__(self, geometry, start_date, end_date, cloud_cover=None):
        super().__init__(geometry, start_date, end_date, output_path=None)
        self.cloud_cover = (
            cloud_cover if cloud_cover is not None else 20
        )  # Default: 20% cloud cover

    def filter_collection(self):
        """Filters the Sentinel-2 image collection and applies cloud cover filtering."""
        s2raw = (
            ee.ImageCollection("COPERNICUS/S2")
            .filterBounds(self.geometry)
            .filterDate(self.start_date, self.end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", self.cloud_cover))
        )  # Apply cloud cover filter

        median_image = s2raw.median()  # Take the median composite
        return median_image

    def download(self):
        """Main function to filter images and export them in parallel."""

        image = self.filter_collection()  # Get the filtered Sentinel-2 image

        # Export all bands in parallel using Dask
        self.export_image_parallel(image, self.sentinel_Band_folder_path, self.geometry)


# ---------------------------
# DownloaderManager (with factory + run)
# ---------------------------
class DownloaderManager:
    """Manages downloader selection and execution for Landsat or Sentinel."""

    def __init__(self, dataset, geojson_path, start_date, end_date, cloud_cover=None):
        self.dataset = dataset.lower()
        self.geojson_path = geojson_path
        self.start_date = start_date
        self.end_date = end_date
        self.cloud_cover = cloud_cover
        self.geometry = load_geometry_from_geojson(geojson_path)

    def get_downloader(self):
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

    def run(self):
        downloader = self.get_downloader()
        downloader.download()
