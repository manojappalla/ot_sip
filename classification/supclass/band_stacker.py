import numpy as np
import rasterio


class BandStacker:
    def __init__(self, file_list):
        self.file_list = file_list

    def stack(self):
        bands = []
        for file in self.file_list:
            with rasterio.open(file) as src:
                bands.append(src.read(1))
        stacked = np.stack(bands, axis=-1)  # shape: (rows, cols, bands)
        return stacked
