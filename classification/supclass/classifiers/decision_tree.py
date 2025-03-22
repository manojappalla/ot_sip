from sklearn.tree import DecisionTreeClassifier as SKDecisionTree
from .base import Classifier


class DecisionTreeClassifierStrategy(Classifier):
    def __init__(self, **kwargs):
        self.model = SKDecisionTree(**kwargs)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        return self.model.predict(X_test)