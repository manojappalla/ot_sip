import cv2
import rasterio
import numpy as np
from abc import ABC, abstractmethod


# === Abstract base class ===
class MorphOperation(ABC):
    @abstractmethod
    def apply(
        self, image: np.ndarray, kernel: np.ndarray, iterations: int
    ) -> np.ndarray:
        pass

    def save_as_tif(
        self, array: np.ndarray, output_path: str, reference_meta: dict, operation
    ):
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
    def apply(
        self, image: np.ndarray, kernel: np.ndarray, iterations: int
    ) -> np.ndarray:
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.erode(image, kernel, iterations=iterations)


# === Strategy: Dilation ===
class DilateOperation(MorphOperation):
    def apply(
        self, image: np.ndarray, kernel: np.ndarray, iterations: int
    ) -> np.ndarray:
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.dilate(image, kernel, iterations=iterations)


# === Strategy: Opening ===
class OpenOperation(MorphOperation):
    def apply(
        self, image: np.ndarray, kernel: np.ndarray, iterations: int
    ) -> np.ndarray:
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)


# === Strategy: Closing ===
class CloseOperation(MorphOperation):
    def apply(
        self, image: np.ndarray, kernel: np.ndarray, iterations: int
    ) -> np.ndarray:
        kernel = np.ones((kernel, kernel), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
