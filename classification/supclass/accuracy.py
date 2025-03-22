from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    cohen_kappa_score,
)
import numpy as np


class AccuracyAssessor:
    def __init__(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred

    def report(self):
        # Overall accuracy
        overall_accuracy = accuracy_score(self.y_true, self.y_pred)

        # Producer accuracy = recall per class
        producer_accuracy = recall_score(self.y_true, self.y_pred, average=None)

        # User accuracy = precision per class
        user_accuracy = precision_score(self.y_true, self.y_pred, average=None)

        # Kappa coefficient
        kappa = cohen_kappa_score(self.y_true, self.y_pred)

        return {
            "overall_accuracy": overall_accuracy,
            "producer_accuracy": producer_accuracy,
            "user_accuracy": user_accuracy,
            "kappa": kappa,
        }
