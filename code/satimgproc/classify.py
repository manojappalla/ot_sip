import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import mapping
from rasterio.features import geometry_mask
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    cohen_kappa_score,
)
from sklearn.tree import DecisionTreeClassifier as SKDecisionTree
from sklearn.ensemble import RandomForestClassifier as SKRandomForest
from sklearn.svm import SVC
from sklearn.cluster import KMeans as SKKMeans


# ------------------------------------------
# Data Preprocessor
# ------------------------------------------
class DataPreprocessor:
    def __init__(self, band_paths, shapefile_path=None, class_attribute=None):
        self.band_paths = band_paths
        self.shapefile_path = shapefile_path
        self.class_attr = class_attribute
        self.image_array = None
        self.meta = None

    def stack_bands(self):
        bands = []
        for file in self.band_paths:
            with rasterio.open(file) as src:
                bands.append(src.read(1))
        self.image_array = np.stack(bands, axis=-1)
        self.meta = src.meta
        return self.image_array, self.meta

    def extract_training_data(self):
        if self.image_array is None or self.meta is None:
            raise ValueError("Call stack_bands() before extracting training data.")

        gdf = gpd.read_file(self.shapefile_path)
        X, y = [], []

        for _, row in gdf.iterrows():
            geom = [mapping(row.geometry)]
            label = row[self.class_attr]

            mask = geometry_mask(
                geometries=geom,
                out_shape=(self.image_array.shape[0], self.image_array.shape[1]),
                transform=self.meta["transform"],
                invert=True,
            )

            samples = self.image_array[mask]
            samples = samples[~np.isnan(samples).any(axis=1)]

            X.append(samples)
            y.append(np.full(samples.shape[0], label))

        X_all = np.vstack(X)
        y_all = np.concatenate(y)
        return train_test_split(X_all, y_all, test_size=0.2, random_state=42)


# ------------------------------------------
# Accuracy Assessor
# ------------------------------------------
class AccuracyAssessor:
    def __init__(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred

    def report(self):
        return {
            "overall_accuracy": accuracy_score(self.y_true, self.y_pred),
            "producer_accuracy": recall_score(self.y_true, self.y_pred, average=None),
            "user_accuracy": precision_score(self.y_true, self.y_pred, average=None),
            "kappa": cohen_kappa_score(self.y_true, self.y_pred),
        }


# ------------------------------------------
# Classification Base Classes
# ------------------------------------------
class Supervised:
    def train(self, X, y):
        raise NotImplementedError

    def predict(self, X):
        raise NotImplementedError


class Unsupervised:
    def fit(self, X):
        raise NotImplementedError

    def classify(self, X):
        raise NotImplementedError


# ------------------------------------------
# Supervised Algorithms
# ------------------------------------------
class DecisionTree(Supervised):
    def __init__(self, **kwargs):
        self.model = SKDecisionTree(**kwargs)

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)


# ------------------------------------------
# Unsupervised Algorithms
# ------------------------------------------
class KMeans(Unsupervised):
    def __init__(self, n_clusters=5, **kwargs):
        self.model = SKKMeans(n_clusters=n_clusters, **kwargs)

    def fit(self, X):
        self.model.fit(X)

    def classify(self, X):
        return self.model.predict(X)
