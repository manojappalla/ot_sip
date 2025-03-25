import numpy as np
import rasterio
from satimgproc.utils import load_bands


# ------------------------------------------
# Base Class: Provides shared _save_index method
# ------------------------------------------
class Indices:
    def __init__(self, output_path):
        self.output_path = output_path

    def save_index(self, data, meta, name):
        meta.update(
            {
                "driver": "GTiff",
                "count": 1,
                "dtype": rasterio.float32,
                "compress": "lzw",
            }
        )
        with rasterio.open(f"{self.output_path}/{name}.tif", "w", **meta) as dst:
            dst.write(data.astype(np.float32), 1)


# ------------------------------------------
# Vegetation Indices: NDVI, MSAVI, VARI
# ------------------------------------------
class VegetationIndices(Indices):
    """Handles Vegetation Indices: NDVI, MSAVI, VARI"""

    def __init__(self, band_paths, output_path):
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def ndvi(self):
        ndvi = (self.bands["nir"][0] - self.bands["red"][0]) / (
            self.bands["nir"][0] + self.bands["red"][0]
        )
        self.save_index(ndvi, self.bands["nir"][1], "ndvi")

    def msavi(self):
        msavi = (
            2 * self.bands["nir"][0]
            + 1
            - np.sqrt(
                (2 * self.bands["nir"][0] + 1) ** 2
                - 8 * (self.bands["nir"][0] - self.bands["red"][0])
            )
        ) / 2
        self.save_index(msavi, self.bands["nir"][1], "msavi")

    def vari(self):
        vari = (self.bands["green"][0] - self.bands["red"][0]) / (
            self.bands["green"][0] + self.bands["red"][0] - self.bands["blue"][0]
        )
        self.save_index(vari, self.bands["green"][1], "vari")


# ------------------------------------------
# Land Indices: NDBI, NBR, BAI
# ------------------------------------------
class LandIndices(Indices):
    """Handles Land Indices: NDBI, NBR, BAI"""

    def __init__(self, band_paths, output_path):
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def ndbi(self):
        ndbi = (self.bands["swir1"][0] - self.bands["nir"][0]) / (
            self.bands["swir1"][0] + self.bands["nir"][0]
        )
        self.save_index(ndbi, self.bands["swir1"][1], "ndbi")

    def nbr(self):
        nbr = (self.bands["nir"][0] - self.bands["swir1"][0]) / (
            self.bands["nir"][0] + self.bands["swir1"][0]
        )
        self.save_index(nbr, self.bands["nir"][1], "nbr")

    def bai(self):
        bai = 1 / (
            (0.1 - self.bands["nir"][0]) ** 2 + (0.06 - self.bands["red"][0]) ** 2
        )
        self.save_index(bai, self.bands["nir"][1], "bai")


# ------------------------------------------
# Water Indices: MNDWI, NDMI
# ------------------------------------------
class WaterIndices(Indices):
    """Handles Water Indices: MNDWI, NDMI"""

    def __init__(self, band_paths, output_path):
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def mndwi(self):
        mndwi = (self.bands["green"][0] - self.bands["swir1"][0]) / (
            self.bands["green"][0] + self.bands["swir1"][0]
        )
        self.save_index(mndwi, self.bands["green"][1], "mndwi")

    def ndmi(self):
        ndmi = (self.bands["nir"][0] - self.bands["swir1"][0]) / (
            self.bands["nir"][0] + self.bands["swir1"][0]
        )
        self.save_index(ndmi, self.bands["nir"][1], "ndmi")


# ------------------------------------------
# Geology Indices: Clay, Ferrous, Iron Oxide
# ------------------------------------------
class GeologyIndices(Indices):
    """Handles Geology Indices: Clay, Ferrous, Iron Oxide"""

    def __init__(self, band_paths, output_path):
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def clay(self):
        clay = self.bands["swir1"][0] / self.bands["swir2"][0]
        self.save_index(clay, self.bands["swir1"][1], "clay")

    def ferrous(self):
        ferrous = self.bands["swir1"][0] / self.bands["nir"][0]
        self.save_index(ferrous, self.bands["swir1"][1], "ferrous")

    def iron_oxide(self):
        iron_oxide = self.bands["red"][0] / self.bands["blue"][0]
        self.save_index(iron_oxide, self.bands["red"][1], "iron_oxide")
