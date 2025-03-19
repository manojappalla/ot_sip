import ee
import geemap

class BaseDownloader:
    def __init__(self, geometry, start_date, end_date, scale, output_path):
        self.geometry = geometry
        self.start_date = start_date
        self.end_date = end_date
        self.scale = scale
        self.output_path = output_path

    def filter_collection(self):
        """Abstract method to filter image collection"""
        raise NotImplementedError

    def export_image(self, image, bands):
        """Exports an image to a local file"""
        geemap.ee_export_image(
            image.select(bands).clip(self.geometry),
            scale=self.scale,
            filename=self.output_path,
            region=self.geometry,
            file_per_band=False
        )
        print(f"Image saved: {self.output_path}")

    def download(self):
        """Main function to filter images and export them"""
        image = self.filter_collection()
        self.export_image(image, self.bands)
