"""Random forest classifier, reused from Lab 6 as complete foundation code.

The Extra-Trees forest in ``extra_trees.py`` subclasses this and overrides
only ``_new_tree`` so that the bagging loop itself does not change.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from advanced_ai.trees.decision_tree import DecisionTreeClassifier


@dataclass
class RandomForestClassifier:
    n_estimators: int = 50
    max_depth: int | None = None
    min_samples_leaf: int = 1
    max_features: int | None = None
    random_state: int | None = None

    def __post_init__(self) -> None:
        if self.n_estimators < 1:
            raise ValueError("n_estimators must be at least 1.")
        if self.min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be at least 1.")
        self._rng = np.random.default_rng(self.random_state)
        self.trees_: list[DecisionTreeClassifier] = []
        self.feature_subsets_: list[np.ndarray] = []
        self.oob_masks_: list[np.ndarray] = []
        self.classes_: np.ndarray | None = None

    def _bootstrap_sample(self, n: int) -> np.ndarray:
        return self._rng.integers(0, n, size=n)

    def _feature_subset(self, d: int) -> np.ndarray:
        m = self.max_features if self.max_features is not None else max(1, int(np.floor(np.sqrt(d))))
        m = min(m, d)
        return self._rng.choice(d, size=m, replace=False)

    def _new_tree(self) -> DecisionTreeClassifier:
        return DecisionTreeClassifier(max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestClassifier":
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        n, d = X.shape
        self.classes_ = np.unique(y)
        self.trees_ = []
        self.feature_subsets_ = []
        self.oob_masks_ = []

        for _ in range(self.n_estimators):
            boot_idx = self._bootstrap_sample(n)
            feat_idx = self._feature_subset(d)
            tree = self._new_tree()
            tree.fit(X[boot_idx][:, feat_idx], y[boot_idx])

            oob_mask = np.ones(n, dtype=bool)
            oob_mask[boot_idx] = False

            self.trees_.append(tree)
            self.feature_subsets_.append(feat_idx)
            self.oob_masks_.append(oob_mask)
        return self

    def _vote_matrix(self, X: np.ndarray) -> np.ndarray:
        if self.classes_ is None:
            raise RuntimeError("The forest is not fitted.")
        votes = np.zeros((X.shape[0], self.classes_.size), dtype=np.int64)
        for tree, feat_idx in zip(self.trees_, self.feature_subsets_):
            pred = tree.predict(X[:, feat_idx])
            for c, cls in enumerate(self.classes_):
                votes[:, c] += (pred == cls)
        return votes

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if self.classes_ is None:
            raise RuntimeError("The forest is not fitted.")
        votes = self._vote_matrix(X)
        return self.classes_[np.argmax(votes, axis=1)]

    def oob_error(self, X: np.ndarray, y: np.ndarray) -> float:
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        n = X.shape[0]
        if self.classes_ is None:
            raise RuntimeError("The forest is not fitted.")
        votes = np.zeros((n, self.classes_.size), dtype=np.int64)
        has_oob = np.zeros(n, dtype=bool)
        for tree, feat_idx, oob_mask in zip(self.trees_, self.feature_subsets_, self.oob_masks_):
            if not np.any(oob_mask):
                continue
            pred = tree.predict(X[oob_mask][:, feat_idx])
            for c, cls in enumerate(self.classes_):
                votes[oob_mask, c] += (pred == cls)
            has_oob |= oob_mask
        if not np.any(has_oob):
            return 0.0
        oob_pred = self.classes_[np.argmax(votes[has_oob], axis=1)]
        return float(np.mean(oob_pred != y[has_oob]))

    def feature_importances(self, n_features: int) -> np.ndarray:
        importances = np.zeros(n_features, dtype=np.float64)

        def _walk(node, feat_idx: np.ndarray, n_total: int) -> None:
            if node.is_leaf:
                return
            importances[feat_idx[node.feature_index]] += (node.n_samples / n_total) * (
                node.impurity
                - (node.left.n_samples / node.n_samples) * node.left.impurity
                - (node.right.n_samples / node.n_samples) * node.right.impurity
            )
            _walk(node.left, feat_idx, n_total)
            _walk(node.right, feat_idx, n_total)

        for tree, feat_idx in zip(self.trees_, self.feature_subsets_):
            if tree.root_ is None:
                continue
            n_total = tree.root_.n_samples
            _walk(tree.root_, feat_idx, n_total)

        importances /= max(len(self.trees_), 1)
        total = importances.sum()
        if total > 0:
            importances /= total
        return importances
