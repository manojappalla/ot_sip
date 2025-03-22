import geopandas as gpd
import numpy as np
from shapely.geometry import mapping
from rasterio.features import geometry_mask
from sklearn.model_selection import train_test_split


class TrainingDataExtractor:
    def __init__(self, image_array, image_meta, shapefile_path, class_attribute):
        self.image_array = image_array  # shape: (rows, cols, bands)
        self.meta = image_meta
        self.shapefile = shapefile_path
        self.class_attr = class_attribute

    def extract(self):
        gdf = gpd.read_file(self.shapefile)
        X, y = [], []

        for _, row in gdf.iterrows():
            geom = [mapping(row.geometry)]
            label = row[self.class_attr]

            # Create mask from geometry (shape: (rows, cols))
            mask = geometry_mask(
                geometries=geom,
                out_shape=(self.image_array.shape[0], self.image_array.shape[1]),
                transform=self.meta["transform"],
                invert=True  # True = keep pixels inside the polygon
            )

            # Apply mask to get all band values per pixel
            samples = self.image_array[mask]  # shape: (num_pixels, num_bands)

            # Remove NaNs if needed
            samples = samples[~np.isnan(samples).any(axis=1)]

            X.append(samples)
            y.append(np.full(samples.shape[0], label))

        # Stack all into arrays
        X_all = np.vstack(X)
        y_all = np.concatenate(y)

        # Split into train and test
        return train_test_split(X_all, y_all, test_size=0.2, random_state=42)
