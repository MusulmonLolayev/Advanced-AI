"""Regression forest, reused from Lab 6 as complete foundation code.

The quantile regression forest in ``quantile_forest.py`` subclasses this so
that the bagging loop and point predictions are already available; the new
work for Lab 7 is reading the per-leaf distributions instead of only the
leaf mean.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from advanced_ai.trees.regression_tree import RegressionTree


@dataclass
class RandomForestRegressor:
    n_estimators: int = 50
    max_depth: int | None = None
    min_samples_leaf: int = 5
    max_features: int | None = None
    random_state: int | None = None

    def __post_init__(self) -> None:
        if self.n_estimators < 1:
            raise ValueError("n_estimators must be at least 1.")
        if self.min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be at least 1.")
        self._rng = np.random.default_rng(self.random_state)
        self.trees_: list[RegressionTree] = []
        self.feature_subsets_: list[np.ndarray] = []

    def _bootstrap_sample(self, n: int) -> np.ndarray:
        return self._rng.integers(0, n, size=n)

    def _feature_subset(self, d: int) -> np.ndarray:
        m = self.max_features if self.max_features is not None else d
        m = min(m, d)
        if m == d:
            return np.arange(d)
        return self._rng.choice(d, size=m, replace=False)

    def _new_tree(self) -> RegressionTree:
        return RegressionTree(max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestRegressor":
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n, d = X.shape
        self.trees_ = []
        self.feature_subsets_ = []

        for _ in range(self.n_estimators):
            boot_idx = self._bootstrap_sample(n)
            feat_idx = self._feature_subset(d)
            tree = self._new_tree()
            tree.fit(X[boot_idx][:, feat_idx], y[boot_idx])
            self.trees_.append(tree)
            self.feature_subsets_.append(feat_idx)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if not self.trees_:
            raise RuntimeError("The forest is not fitted.")
        preds = np.stack(
            [tree.predict(X[:, feat_idx]) for tree, feat_idx in zip(self.trees_, self.feature_subsets_)],
            axis=0,
        )
        return preds.mean(axis=0)
