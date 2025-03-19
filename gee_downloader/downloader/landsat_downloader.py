import ee
from .base_downloader import BaseDownloader

class LandsatDownloader(BaseDownloader):
    def __init__(self, geometry, start_date, end_date, scale, output_path, bands=['PAN']):
        super().__init__(geometry, start_date, end_date, scale, output_path)
        self.bands = bands  # Default to Panchromatic band for high-resolution

    def filter_collection(self):
        """Filters the Landsat 8 image collection"""
        l8raw = ee.ImageCollection('LANDSAT/LC08/C02/T1')\
            .filterBounds(self.geometry)\
            .filterDate(self.start_date, self.end_date)

        cloud_free = ee.Algorithms.Landsat.simpleComposite(
            collection=l8raw, asFloat=True
        )
        return cloud_free
