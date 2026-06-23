"""Forest variants for Assignment 7."""

from .random_forest import RandomForestClassifier
from .regression_forest import RandomForestRegressor
from .isolation_forest import IsolationForest, IsolationTree
from .extra_trees import ExtraTreeClassifier, ExtraTreesClassifier
from .quantile_forest import QuantileRegressionForest

__all__ = [
    "RandomForestClassifier",
    "RandomForestRegressor",
    "IsolationForest",
    "IsolationTree",
    "ExtraTreeClassifier",
    "ExtraTreesClassifier",
    "QuantileRegressionForest",
]
