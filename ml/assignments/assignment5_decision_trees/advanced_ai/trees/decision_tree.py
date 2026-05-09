"""Decision tree starter implementation for Assignment 5."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TreeNode:
    prediction: int
    impurity: float
    n_samples: int
    depth: int
    feature_index: int | None = None
    threshold: float | None = None
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


@dataclass
class DecisionTreeClassifier:
    max_depth: int | None = 3
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    min_impurity_decrease: float = 0.0

    def __post_init__(self) -> None:
        if self.max_depth is not None and self.max_depth < 0:
            raise ValueError("max_depth must be nonnegative or None.")
        if self.min_samples_split < 2:
            raise ValueError("min_samples_split must be at least 2.")
        if self.min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be at least 1.")
        if self.min_impurity_decrease < 0:
            raise ValueError("min_impurity_decrease must be nonnegative.")
        self.root_: TreeNode | None = None
        self.classes_: np.ndarray | None = None
        self.n_features_in_: int | None = None

    def _class_counts(self, y: np.ndarray) -> np.ndarray:
        if self.classes_ is None:
            raise RuntimeError("classes_ is not set.")
        return np.asarray([np.sum(y == cls) for cls in self.classes_], dtype=np.int64)

    def _majority_class(self, y: np.ndarray) -> int:
        counts = self._class_counts(y)
        return int(self.classes_[int(np.argmax(counts))])

    def _gini(self, y: np.ndarray) -> float:
        raise NotImplementedError("TODO T1: implement Gini impurity.")

    def _candidate_thresholds(self, values: np.ndarray) -> np.ndarray:
        values = np.asarray(values, dtype=np.float64)
        unique = np.unique(values)
        if unique.size <= 1:
            return np.array([], dtype=np.float64)
        return (unique[:-1] + unique[1:]) / 2.0

    def _split_gain(self, y: np.ndarray, left_mask: np.ndarray) -> float:
        # TODO T2: split y into left and right using left_mask, then compute
        # parent impurity minus weighted child impurity.
        raise NotImplementedError("TODO T2: implement weighted impurity decrease.")

    def _best_split(self, X: np.ndarray, y: np.ndarray) -> tuple[int | None, float | None, float]:
        # TODO T3: try every feature and every midpoint threshold returned by
        # _candidate_thresholds. Keep the valid split with the largest gain.
        raise NotImplementedError("TODO T3: search all features and candidate thresholds.")

    def _build_node(self, X: np.ndarray, y: np.ndarray, depth: int) -> TreeNode:
        # TODO T4: create a leaf if a stopping condition holds; otherwise split
        # the data and recursively build left and right children.
        raise NotImplementedError("TODO T4: implement recursive tree growth.")

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DecisionTreeClassifier":
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")
        if y.ndim != 1:
            raise ValueError("y must be a 1D array.")
        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y must contain the same number of examples.")
        if X.shape[0] == 0:
            raise ValueError("Cannot fit on an empty dataset.")

        self.classes_ = np.unique(y)
        self.n_features_in_ = X.shape[1]
        self.root_ = self._build_node(X, y, depth=0)
        return self

    def _predict_one(self, x: np.ndarray) -> int:
        if self.root_ is None:
            raise RuntimeError("The tree is not fitted.")
        node = self.root_
        while not node.is_leaf:
            if node.feature_index is None or node.threshold is None:
                raise RuntimeError("Internal node is missing split information.")
            if x[node.feature_index] <= node.threshold:
                if node.left is None:
                    raise RuntimeError("Internal node is missing left child.")
                node = node.left
            else:
                if node.right is None:
                    raise RuntimeError("Internal node is missing right child.")
                node = node.right
        return node.prediction

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")
        return np.asarray([self._predict_one(row) for row in X], dtype=np.int64)

    def depth(self) -> int:
        if self.root_ is None:
            return 0

        def _depth(node: TreeNode) -> int:
            if node.is_leaf:
                return node.depth
            children = [child for child in [node.left, node.right] if child is not None]
            return max(_depth(child) for child in children)

        return _depth(self.root_)

    def n_leaves(self) -> int:
        if self.root_ is None:
            return 0

        def _count(node: TreeNode) -> int:
            if node.is_leaf:
                return 1
            return sum(_count(child) for child in [node.left, node.right] if child is not None)

        return _count(self.root_)

    def explain_one_path(self, x: np.ndarray) -> list[str]:
        if self.root_ is None:
            raise RuntimeError("The tree is not fitted.")
        x = np.asarray(x, dtype=np.float64)
        node = self.root_
        path: list[str] = []
        while not node.is_leaf:
            if node.feature_index is None or node.threshold is None:
                raise RuntimeError("Internal node is missing split information.")
            feature = node.feature_index
            threshold = node.threshold
            if x[feature] <= threshold:
                path.append(f"x[{feature}] <= {threshold:.6g}")
                if node.left is None:
                    raise RuntimeError("Internal node is missing left child.")
                node = node.left
            else:
                path.append(f"x[{feature}] > {threshold:.6g}")
                if node.right is None:
                    raise RuntimeError("Internal node is missing right child.")
                node = node.right
        path.append(f"predict {node.prediction}")
        return path
