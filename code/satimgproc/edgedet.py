from typing import Dict
import cv2
import numpy as np
from abc import ABC, abstractmethod
import rasterio


# === Base class for all edge detectors ===
class EdgeDetector(ABC):
    """
    Abstract base class for edge detection algorithms.

    Provides utility methods for grayscale conversion, normalization,
    and saving results as GeoTIFFs using reference raster metadata.
    """

    @abstractmethod
    def detect(self, image: np.ndarray) -> np.ndarray:
        pass

    def _normalize(self, img: np.ndarray) -> np.ndarray:
        """
        Normalizes the input image to 8-bit using percentile clipping.

        Parameters:
        - img (np.ndarray): Input grayscale image.

        Returns:
        - np.ndarray: Normalized 8-bit image.
        """
        img = np.clip(img, 0, np.percentile(img, 98))
        img = (img - img.min()) / (img.max() - img.min()) * 255
        return img.astype(np.uint8)

    def convert_to_gray(self, image: np.ndarray) -> np.ndarray:
        """
        Converts a BGR image to grayscale and normalizes it.

        Parameters:
        - image (np.ndarray): Input image in BGR format.

        Returns:
        - np.ndarray: Grayscale and normalized image.
        """
        rgb_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(rgb_image_rgb, cv2.COLOR_RGB2GRAY)
        gray_norm = self._normalize(gray)
        return gray_norm

    def save_as_tif(
        self,
        array: np.ndarray,
        output_path: str,
        reference_meta: Dict,
    ) -> None:
        """
        Saves the given array as a GeoTIFF file using raster metadata.

        Parameters:
        - array (np.ndarray): 2D array to be saved.
        - output_path (str): Folder path to save the 'edges.tif' file.
        - reference_meta (dict): Metadata from a reference raster to retain geolocation and projection.
        """
        # Update metadata to match output
        meta = reference_meta.copy()
        meta.update({"count": 1, "dtype": array.dtype, "compress": "lzw"})

        # If the array is 2D, reshape to (1, H, W) for writing
        if array.ndim == 2:
            array = array[np.newaxis, :, :]

        with rasterio.open(f"{output_path}/edges.tif", "w", **meta) as dst:
            dst.write(array)


# === Canny Detector ===
class CannyEdgeDetector(EdgeDetector):
    """
    Edge detection using the Canny method.

    Applies the Canny algorithm on a grayscale-normalized version of the input image.
    """

    def __init__(self, threshold1: int = 100, threshold2: int = 200):
        """
        Initializes the CannyEdgeDetector.

        Parameters:
        - threshold1 (int): Lower threshold for the hysteresis procedure.
        - threshold2 (int): Upper threshold for the hysteresis procedure.
        """
        self.threshold1 = threshold1
        self.threshold2 = threshold2

    def detect(self, image: np.ndarray) -> np.ndarray:
        """
        Applies the Canny edge detector on the input image.

        Parameters:
        - image (np.ndarray): Input image in BGR format.

        Returns:
        - np.ndarray: Binary image with edges.
        """
        gray_norm = self.convert_to_gray(image)
        return cv2.Canny(gray_norm, self.threshold1, self.threshold2)
