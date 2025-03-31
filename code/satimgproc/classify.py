from typing import List, Tuple, Dict, Optional
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
    """
    Preprocesses remote sensing data for classification tasks.

    This class handles stacking raster bands into a single array
    and extracting training data using a shapefile containing labeled regions.
    """

    def __init__(
        self,
        band_paths: List[str],
        shapefile_path: Optional[str] = None,
        class_attribute: Optional[str] = None,
    ):
        """
        Initializes the DataPreprocessor.

        Parameters:
        - band_paths (list of str): Paths to individual raster band files.
        - shapefile_path (str): Path to the training shapefile (optional).
        - class_attribute (str): Column in shapefile containing class labels.
        """
        self.band_paths = band_paths
        self.shapefile_path = shapefile_path
        self.class_attr = class_attribute
        self.image_array = None
        self.meta = None

    def stack_bands(self) -> Tuple[np.ndarray, dict]:
        """
        Reads and stacks individual raster bands into a 3D numpy array.

        Returns:
        - image_array (np.ndarray): Stacked array of shape (height, width, bands).
        - meta (dict): Metadata from the last read raster band.
        """
        bands = []
        for file in self.band_paths:
            with rasterio.open(file) as src:
                bands.append(src.read(1))
        self.image_array = np.stack(bands, axis=-1)
        self.meta = src.meta
        return self.image_array, self.meta

    def extract_training_data(
        self,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Extracts training samples and labels using vector geometries.

        Requires stacked bands and a labeled shapefile. Pixels inside the labeled
        regions are extracted and matched with their corresponding labels.

        Returns:
        - X_train, X_test, y_train, y_test: Split training and testing datasets.
        """
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
    """
    Computes accuracy metrics for classification results.
    """

    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray):
        """
        Initializes the AccuracyAssessor.

        Parameters:
        - y_true (np.ndarray): Ground truth labels.
        - y_pred (np.ndarray): Predicted labels.
        """
        self.y_true = y_true
        self.y_pred = y_pred

    def report(self) -> Dict[str, object]:
        """
        Calculates standard accuracy metrics.

        Returns:
        - dict: Dictionary containing overall accuracy, producer accuracy,
                user accuracy, and Cohen's kappa score.
        """
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
    """
    Abstract base class for supervised classification algorithms.
    """

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Trains the model on labeled data.

        Parameters:
        - X (np.ndarray): Feature array.
        - y (np.ndarray): Label array.
        """
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predicts class labels for given data.

        Parameters:
        - X (np.ndarray): Feature array.

        Returns:
        - np.ndarray: Predicted class labels.
        """
        raise NotImplementedError


class Unsupervised:
    """
    Abstract base class for unsupervised classification algorithms.
    """

    def fit(self, X: np.ndarray) -> None:
        """
        Fits the model to unlabeled data.

        Parameters:
        - X (np.ndarray): Feature array.
        """
        raise NotImplementedError

    def classify(self, X: np.ndarray) -> np.ndarray:
        """
        Assigns cluster/class labels to input data.

        Parameters:
        - X (np.ndarray): Feature array.

        Returns:
        - np.ndarray: Assigned cluster labels.
        """
        raise NotImplementedError


# ------------------------------------------
# Supervised Algorithms
# ------------------------------------------
class DecisionTree(Supervised):
    """
    Decision Tree classifier using scikit-learn.
    """

    def __init__(self, **kwargs):
        """
        Initializes the DecisionTree classifier.

        Parameters:
        - kwargs: Optional parameters passed to sklearn.tree.DecisionTreeClassifier.
        """
        self.model = SKDecisionTree(**kwargs)

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Trains the Decision Tree classifier.

        Parameters:
        - X (np.ndarray): Feature array.
        - y (np.ndarray): Label array.
        """
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predicts class labels using the trained Decision Tree model.

        Parameters:
        - X (np.ndarray): Feature array.

        Returns:
        - np.ndarray: Predicted class labels.
        """
        return self.model.predict(X)


# ------------------------------------------
# Unsupervised Algorithms
# ------------------------------------------
class KMeans(Unsupervised):
    """
    KMeans clustering algorithm using scikit-learn.
    """

    def __init__(self, n_clusters: int = 5, **kwargs):
        """
        Initializes the KMeans model.

        Parameters:
        - n_clusters (int): Number of clusters to form.
        - kwargs: Additional parameters passed to sklearn.cluster.KMeans.
        """
        self.model = SKKMeans(n_clusters=n_clusters, **kwargs)

    def fit(self, X: np.ndarray) -> None:
        """
        Fits the KMeans model on unlabeled data.

        Parameters:
        - X (np.ndarray): Feature array.
        """
        self.model.fit(X)

    def classify(self, X: np.ndarray) -> np.ndarray:
        """
        Assigns each sample in X to the nearest cluster.

        Parameters:
        - X (np.ndarray): Feature array.

        Returns:
        - np.ndarray: Cluster labels.
        """
        return self.model.predict(X)
