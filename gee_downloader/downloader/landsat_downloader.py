import ee
from .base_downloader import BaseDownloader


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
