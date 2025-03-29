import cv2
import numpy as np
from abc import ABC, abstractmethod
import rasterio


# === Base class for all edge detectors ===
class EdgeDetector(ABC):
    @abstractmethod
    def detect(self, image: np.ndarray) -> np.ndarray:
        pass

    def _normalize(self, img):
        img = np.clip(img, 0, np.percentile(img, 98))
        img = (img - img.min()) / (img.max() - img.min()) * 255
        return img.astype(np.uint8)

    def convert_to_gray(self, image):
        rgb_image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(rgb_image_rgb, cv2.COLOR_RGB2GRAY)
        gray_norm = self._normalize(gray)
        return gray_norm

    def save_as_tif(self, array: np.ndarray, output_path: str, reference_meta: dict):
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
    def __init__(self, threshold1=100, threshold2=200):
        self.threshold1 = threshold1
        self.threshold2 = threshold2

    def detect(self, image: np.ndarray) -> np.ndarray:
        gray_norm = self.convert_to_gray(image)
        return cv2.Canny(gray_norm, self.threshold1, self.threshold2)
