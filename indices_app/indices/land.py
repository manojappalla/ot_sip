import numpy as np
import rasterio
from indices_app.utils.file_loader import load_bands


class LandIndices:
    """Handles Land Indices: NDBI, NBR, BAI"""

    def __init__(self, band_paths, output_path):
        self.bands = load_bands(band_paths)
        self.output_path = output_path

    def ndbi(self):
        ndbi = (self.bands["swir1"][0] - self.bands["nir"][0]) / (
            self.bands["swir1"][0] + self.bands["nir"][0]
        )
        meta = self.bands["swir1"][1]  # Use stored metadata
        # Update metadata for single-band output
        meta.update(
            {
                "driver": "GTiff",
                "count": 1,  # Single band output
                "dtype": rasterio.float32,
                "compress": "lzw",  # Compression for smaller file size
            }
        )
        # Save NDVI result as a GeoTIFF
        with rasterio.open(f"{self.output_path}/ndbi.tif", "w", **meta) as dst:
            dst.write(ndbi.astype(np.float32), 1)

    def nbr(self):
        nbr = (self.bands["nir"][0] - self.bands["swir1"][0]) / (
            self.bands["nir"][0] + self.bands["swir1"][0]
        )
        meta = self.bands["nir"][1]  # Use stored metadata
        # Update metadata for single-band output
        meta.update(
            {
                "driver": "GTiff",
                "count": 1,  # Single band output
                "dtype": rasterio.float32,
                "compress": "lzw",  # Compression for smaller file size
            }
        )
        # Save NDVI result as a GeoTIFF
        with rasterio.open(f"{self.output_path}/nbr.tif", "w", **meta) as dst:
            dst.write(nbr.astype(np.float32), 1)

    def bai(self):
        bai = 1 / (
            (0.1 - self.bands["nir"][0]) ** 2 + (0.06 - self.bands["red"][0]) ** 2
        )
        meta = self.bands["nir"][1]  # Use stored metadata
        # Update metadata for single-band output
        meta.update(
            {
                "driver": "GTiff",
                "count": 1,  # Single band output
                "dtype": rasterio.float32,
                "compress": "lzw",  # Compression for smaller file size
            }
        )
        # Save NDVI result as a GeoTIFF
        with rasterio.open(f"{self.output_path}/bai.tif", "w", **meta) as dst:
            dst.write(bai.astype(np.float32), 1)
