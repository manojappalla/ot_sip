import numpy as np
import rasterio
from indices_app.utils.file_loader import load_bands


class VegetationIndices:
    """Handles Vegetation Indices: NDVI, MSAVI, VARI"""

    def __init__(self, band_paths, output_path):
        self.bands = load_bands(band_paths)
        self.output_path = output_path

    def ndvi(self):
        ndvi = (self.bands["nir"][0] - self.bands["red"][0]) / (
            self.bands["nir"][0] + self.bands["red"][0]
        )
        meta = self.bands["nir"][1]  # Use stored metadata
        # Update metadata for single-band output
        meta.update(
            {
                "driver": "GTiff",
                "count": 1,  # Single band output
                "dtype": rasterio.float32,  # Data type for NDVI
                "compress": "lzw",  # Compression for smaller file size
            }
        )
        # Save NDVI result as a GeoTIFF
        with rasterio.open(f"{self.output_path}/ndvi.tif", "w", **meta) as dst:
            dst.write(ndvi.astype(np.float32), 1)  # Write NDVI as band 1

    def msavi(self):
        msavi = (
            2 * self.bands["nir"][0]
            + 1
            - np.sqrt(
                (2 * self.bands["nir"][0] + 1) ** 2
                - 8 * (self.bands["nir"][0] - self.bands["red"][0])
            )
        ) / 2
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
        with rasterio.open(f"{self.output_path}/msavi.tif", "w", **meta) as dst:
            dst.write(msavi.astype(np.float32), 1)

    def vari(self):
        vari = (self.bands["green"][0] - self.bands["red"][0]) / (
            self.bands["green"][0] + self.bands["red"][0] - self.bands["blue"][0]
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
        with rasterio.open(f"{self.output_path}/vari.tif", "w", **meta) as dst:
            dst.write(vari.astype(np.float32), 1)
