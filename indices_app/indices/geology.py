import numpy as np
import rasterio
from indices_app.utils.file_loader import load_bands


class GeologyIndices:
    """Handles Geology Indices: Clay, Ferrous, Iron Oxide"""

    def __init__(self, band_paths, output_path):
        self.bands = load_bands(band_paths)
        self.output_path = output_path

    def clay(self):
        clay = self.bands["swir1"][0] / self.bands["swir2"][0]
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
        with rasterio.open(f"{self.output_path}/clay.tif", "w", **meta) as dst:
            dst.write(clay.astype(np.float32), 1)

    def ferrous(self):
        ferrous = self.bands["swir1"][0] / self.bands["nir"][0]
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
        with rasterio.open(f"{self.output_path}/ferrous.tif", "w", **meta) as dst:
            dst.write(ferrous.astype(np.float32), 1)

    def iron_oxide(self):
        iron_oxide = self.bands["red"][0] / self.bands["blue"][0]
        meta = self.bands["red"][1]  # Use stored metadata
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
        with rasterio.open(f"{self.output_path}/iron_oxide.tif", "w", **meta) as dst:
            dst.write(iron_oxide.astype(np.float32), 1)
