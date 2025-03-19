import ee
from .base_downloader import BaseDownloader

class SentinelDownloader(BaseDownloader):
    def __init__(self, geometry, start_date, end_date, scale, output_path, bands=['B4', 'B3', 'B2']):
        super().__init__(geometry, start_date, end_date, scale, output_path)
        self.bands = bands  # Default: Red, Green, Blue

    def filter_collection(self):
        """Filters the Sentinel-2 image collection"""
        s2raw = ee.ImageCollection('COPERNICUS/S2')\
            .filterBounds(self.geometry)\
            .filterDate(self.start_date, self.end_date)\
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))  # Less than 20% cloud cover

        median_image = s2raw.median()  # Take the median composite
        return median_image
