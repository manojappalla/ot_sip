import ee
import geemap
import dask
from dask import delayed


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
