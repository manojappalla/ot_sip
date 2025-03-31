from typing import Dict
import cv2
import rasterio
import numpy as np
from abc import ABC, abstractmethod


# === Abstract base class ===
class MorphOperation(ABC):
    """
    Abstract base class for morphological operations.

    Defines the interface and common utilities like saving the output
    as a GeoTIFF file with reference metadata.
    """

    @abstractmethod
    def apply(self, image: np.ndarray, kernel: int, iterations: int) -> np.ndarray:
        pass

    def save_as_tif(
        self, array: np.ndarray, output_path: str, reference_meta: Dict, operation: str
    ) -> None:
        """
        Saves the processed image as a GeoTIFF file.

        Parameters:
        - array (np.ndarray): Processed image array.
        - output_path (str): Folder path to save the TIFF.
        - reference_meta (dict): Metadata from a reference raster for spatial info.
        - operation (str): Name of the operation (used in filename).
        """
        # Update metadata to match output
        meta = reference_meta.copy()
        meta.update({"count": 1, "dtype": array.dtype, "compress": "lzw"})

        # If the array is 2D, reshape to (1, H, W) for writing
        if array.ndim == 2:
            array = array[np.newaxis, :, :]

        with rasterio.open(
            f"{output_path}/morphology_{operation}.tif", "w", **meta
        ) as dst:
            dst.write(array)


# === Strategy: Erosion ===
class ErodeOperation(MorphOperation):
    """
    Morphological erosion operation.

    Shrinks foreground objects by eroding boundaries using a structuring element.
    """

    def apply(self, image: np.ndarray, kernel: int, iterations: int) -> np.ndarray:
        """
        Applies erosion using a square kernel.

        Returns:
        - np.ndarray: Eroded image.
        """
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.erode(image, kernel, iterations=iterations)


# === Strategy: Dilation ===
class DilateOperation(MorphOperation):
    """
    Morphological dilation operation.

    Expands foreground objects by growing boundaries using a structuring element.
    """

    def apply(self, image: np.ndarray, kernel: int, iterations: int) -> np.ndarray:
        """
        Applies dilation using a square kernel.

        Returns:
        - np.ndarray: Dilated image.
        """
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.dilate(image, kernel, iterations=iterations)


# === Strategy: Opening ===
class OpenOperation(MorphOperation):
    """
    Morphological opening operation.

    Removes small objects (noise) from foreground using erosion followed by dilation.
    """

    def apply(self, image: np.ndarray, kernel: int, iterations: int) -> np.ndarray:
        """
        Applies opening operation (erosion -> dilation).

        Returns:
        - np.ndarray: Opened image.
        """
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)


# === Strategy: Closing ===
class CloseOperation(MorphOperation):
    """
    Morphological closing operation.

    Fills small holes in foreground objects using dilation followed by erosion.
    """

    def apply(self, image: np.ndarray, kernel: int, iterations: int) -> np.ndarray:
        """
        Applies closing operation (dilation -> erosion).

        Returns:
        - np.ndarray: Closed image.
        """
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
