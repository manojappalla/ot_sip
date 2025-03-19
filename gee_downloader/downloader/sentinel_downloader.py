import ee
from .base_downloader import BaseDownloader

class SentinelDownloader(BaseDownloader):
    def __init__(self, geometry, start_date, end_date, cloud_cover=None):
        super().__init__(geometry, start_date, end_date, output_path=None)
        self.cloud_cover = cloud_cover if cloud_cover is not None else 20  # Default: 20% cloud cover

    def filter_collection(self):
        """Filters the Sentinel-2 image collection and applies cloud cover filtering."""
        s2raw = ee.ImageCollection('COPERNICUS/S2')\
            .filterBounds(self.geometry)\
            .filterDate(self.start_date, self.end_date)\
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.cloud_cover))  # Apply cloud cover filter

        median_image = s2raw.median()  # Take the median composite
        return median_image

    def download(self):
        """Main function to filter images and export them in parallel."""

        image = self.filter_collection()  # Get the filtered Sentinel-2 image

        # Export all bands in parallel using Dask
        self.export_image_parallel(image, self.sentinel_Band_folder_path, self.geometry)
