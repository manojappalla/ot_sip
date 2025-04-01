from typing import Dict
import numpy as np
import rasterio
from satimgproc.utils import load_bands


# ------------------------------------------
# Base Class: Provides shared _save_index method
# ------------------------------------------
class Indices:
    """
    Base class for saving computed index arrays as GeoTIFFs.

    All subclasses should compute a specific remote sensing index and use `save_index`.
    """

    def __init__(self, output_path: str):
        """
        Initializes the base class.

        Parameters:
        - output_path (str): Directory to save the output index files.
        """
        self.output_path = output_path

    def save_index(self, data: np.ndarray, meta: Dict, name: str) -> None:
        """
        Saves a single-band index as a GeoTIFF file.

        Parameters:
        - data (np.ndarray): Computed index array.
        - meta (dict): Metadata (usually from one of the input bands).
        - name (str): Name of the output file (without extension).
        """
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
    """
    Computes common vegetation indices: NDVI, MSAVI, and VARI.
    """

    def __init__(self, band_paths: Dict[str, str], output_path: str):
        """
        Initializes the vegetation index calculator.

        Parameters:
        - band_paths (dict): Dictionary of band names to file paths.
        - output_path (str): Directory to save output files.
        """
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def ndvi(self) -> None:
        """
        Computes the Normalized Difference Vegetation Index (NDVI):
        NDVI = (NIR - Red) / (NIR + Red)
        """
        ndvi = (self.bands["nir"][0] - self.bands["red"][0]) / (
            self.bands["nir"][0] + self.bands["red"][0]
        )
        self.save_index(ndvi, self.bands["nir"][1], "ndvi")

    def msavi(self) -> None:
        """
        Computes the Modified Soil Adjusted Vegetation Index (MSAVI):
        MSAVI = (2 * NIR + 1 - sqrt((2 * NIR + 1)^2 - 8 * (NIR - Red))) / 2
        """
        msavi = (
            2 * self.bands["nir"][0]
            + 1
            - np.sqrt(
                (2 * self.bands["nir"][0] + 1) ** 2
                - 8 * (self.bands["nir"][0] - self.bands["red"][0])
            )
        ) / 2
        self.save_index(msavi, self.bands["nir"][1], "msavi")

    def vari(self) -> None:
        """
        Computes the Visible Atmospherically Resistant Index (VARI):
        VARI = (Green - Red) / (Green + Red - Blue)
        """
        vari = (self.bands["green"][0] - self.bands["red"][0]) / (
            self.bands["green"][0] + self.bands["red"][0] - self.bands["blue"][0]
        )
        self.save_index(vari, self.bands["green"][1], "vari")


# ------------------------------------------
# Land Indices: NDBI, NBR, BAI
# ------------------------------------------
class LandIndices(Indices):
    """
    Computes land-based indices: NDBI, NBR, and BAI.
    """

    def __init__(self, band_paths: Dict[str, str], output_path: str):
        """
        Initializes the land index calculator.

        Parameters:
        - band_paths (dict): Dictionary of band names to file paths.
        - output_path (str): Directory to save output files.
        """
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def ndbi(self) -> None:
        """
        Computes the Normalized Difference Built-up Index (NDBI):
        NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
        """
        ndbi = (self.bands["swir1"][0] - self.bands["nir"][0]) / (
            self.bands["swir1"][0] + self.bands["nir"][0]
        )
        self.save_index(ndbi, self.bands["swir1"][1], "ndbi")

    def nbr(self) -> None:
        """
        Computes the Normalized Burn Ratio (NBR):
        NBR = (NIR - SWIR1) / (NIR + SWIR1)
        """
        nbr = (self.bands["nir"][0] - self.bands["swir1"][0]) / (
            self.bands["nir"][0] + self.bands["swir1"][0]
        )
        self.save_index(nbr, self.bands["nir"][1], "nbr")

    def bai(self) -> None:
        """
        Computes the Burned Area Index (BAI):
        BAI = 1 / [(0.1 - NIR)^2 + (0.06 - Red)^2]
        """
        bai = 1 / (
            (0.1 - self.bands["nir"][0]) ** 2 + (0.06 - self.bands["red"][0]) ** 2
        )
        self.save_index(bai, self.bands["nir"][1], "bai")


# ------------------------------------------
# Water Indices: MNDWI, NDMI
# ------------------------------------------
class WaterIndices(Indices):
    """
    Computes water-related indices: MNDWI and NDMI.
    """

    def __init__(self, band_paths: Dict[str, str], output_path: str):
        """
        Initializes the water index calculator.

        Parameters:
        - band_paths (dict): Dictionary of band names to file paths.
        - output_path (str): Directory to save output files.
        """
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def mndwi(self) -> None:
        """
        Computes the Modified Normalized Difference Water Index (MNDWI):
        MNDWI = (Green - SWIR1) / (Green + SWIR1)
        """
        mndwi = (self.bands["green"][0] - self.bands["swir1"][0]) / (
            self.bands["green"][0] + self.bands["swir1"][0]
        )
        self.save_index(mndwi, self.bands["green"][1], "mndwi")

    def ndmi(self) -> None:
        """
        Computes the Normalized Difference Moisture Index (NDMI):
        NDMI = (NIR - SWIR1) / (NIR + SWIR1)
        """
        ndmi = (self.bands["nir"][0] - self.bands["swir1"][0]) / (
            self.bands["nir"][0] + self.bands["swir1"][0]
        )
        self.save_index(ndmi, self.bands["nir"][1], "ndmi")


# ------------------------------------------
# Geology Indices: Clay, Ferrous, Iron Oxide
# ------------------------------------------
class GeologyIndices(Indices):
    """
    Computes geology-related indices: Clay, Ferrous, and Iron Oxide.
    """

    def __init__(self, band_paths: Dict[str, str], output_path: str):
        """
        Initializes the geology index calculator.

        Parameters:
        - band_paths (dict): Dictionary of band names to file paths.
        - output_path (str): Directory to save output files.
        """
        super().__init__(output_path)
        self.bands = load_bands(band_paths)

    def clay(self) -> None:
        """
        Computes a simple clay mineral ratio:
        Clay Index = SWIR1 / SWIR2
        """
        clay = self.bands["swir1"][0] / self.bands["swir2"][0]
        self.save_index(clay, self.bands["swir1"][1], "clay")

    def ferrous(self) -> None:
        """
        Computes a Ferrous Mineral Index:
        Ferrous Index = SWIR1 / NIR
        """
        ferrous = self.bands["swir1"][0] / self.bands["nir"][0]
        self.save_index(ferrous, self.bands["swir1"][1], "ferrous")

    def iron_oxide(self) -> None:
        """
        Computes an Iron Oxide Index:
        Iron Oxide = Red / Blue
        """
        iron_oxide = self.bands["red"][0] / self.bands["blue"][0]
        self.save_index(iron_oxide, self.bands["red"][1], "iron_oxide")
