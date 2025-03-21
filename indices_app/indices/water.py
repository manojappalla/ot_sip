import numpy as np
import rasterio
from indices_app.utils.file_loader import load_bands


class WaterIndices:
    """Handles Water Indices: MNDWI, NDMI"""

    def __init__(self, band_paths, output_path):
        self.bands = load_bands(band_paths)
        self.output_path = output_path

    def mndwi(self):
        mndwi = (self.bands["green"][0] - self.bands["swir1"][0]) / (
            self.bands["green"][0] + self.bands["swir1"][0]
        )
        meta = self.bands["green"][1]  # Use stored metadata
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
        with rasterio.open(f"{self.output_path}/mndwi.tif", "w", **meta) as dst:
            dst.write(mndwi.astype(np.float32), 1)

    def ndmi(self):
        ndmi = (self.bands["nir"][0] - self.bands["swir1"][0]) / (
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
        with rasterio.open(f"{self.output_path}/ndmi.tif", "w", **meta) as dst:
            dst.write(ndmi.astype(np.float32), 1)
