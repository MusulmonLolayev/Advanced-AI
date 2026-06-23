"""Isolation Forest starter implementation for Assignment 7."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class IsolationTreeNode:
    depth: int
    n_samples: int
    feature_index: int | None = None
    threshold: float | None = None
    left: "IsolationTreeNode | None" = None
    right: "IsolationTreeNode | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


@dataclass
class IsolationTree:
    height_limit: int
    random_state: int | None = None

    def __post_init__(self) -> None:
        if self.height_limit < 0:
            raise ValueError("height_limit must be nonnegative.")
        self._rng = np.random.default_rng(self.random_state)
        self.root_: IsolationTreeNode | None = None

    def _feasible_features(self, X: np.ndarray) -> np.ndarray:
        ranges = X.max(axis=0) - X.min(axis=0)
        return np.flatnonzero(ranges > 0.0)

    def _build_node(self, X: np.ndarray, depth: int) -> IsolationTreeNode:
        # TODO T1: grow one isolation tree node.
        #
        # Stop and return a leaf (IsolationTreeNode with no children) when:
        #   - X has one sample left, or
        #   - depth has reached self.height_limit, or
        #   - every feature is constant at this node (use
        #     self._feasible_features(X); if it is empty, no split is
        #     possible).
        #
        # Otherwise:
        #   1. Pick a feature index j uniformly at random from the feasible
        #      features (use self._rng.choice).
        #   2. Pick a threshold t uniformly at random between the min and
        #      max of feature j at this node (use self._rng.uniform).
        #   3. Partition X into left (x[j] <= t) and right (x[j] > t).
        #   4. Recurse on each side at depth + 1 and attach the children.
        raise NotImplementedError("TODO T1: implement isolation tree growth.")

    def fit(self, X: np.ndarray) -> "IsolationTree":
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError("X must be a 2D array.")
        if X.shape[0] == 0:
            raise ValueError("Cannot fit on an empty dataset.")
        self.root_ = self._build_node(X, depth=0)
        return self

    def path_length(self, x: np.ndarray) -> int:
        # TODO T2: route x from the root to its leaf and return the number
        # of edges traversed (0 if the root is already a leaf).
        raise NotImplementedError("TODO T2: implement path length routing.")


@dataclass
class IsolationForest:
    n_estimators: int = 100
    subsample_size: int = 256
    random_state: int | None = None

    def __post_init__(self) -> None:
        if self.n_estimators < 1:
            raise ValueError("n_estimators must be at least 1.")
        if self.subsample_size < 2:
            raise ValueError("subsample_size must be at least 2.")
        self._rng = np.random.default_rng(self.random_state)
        self.trees_: list[IsolationTree] = []
        self.psi_: int | None = None
        self.height_limit_: int | None = None

    def fit(self, X: np.ndarray) -> "IsolationForest":
        X = np.asarray(X, dtype=np.float64)
        n = X.shape[0]
        psi = min(self.subsample_size, n)
        self.psi_ = psi
        self.height_limit_ = int(np.ceil(np.log2(max(psi, 2))))
        self.trees_ = []
        for _ in range(self.n_estimators):
            idx = self._rng.choice(n, size=psi, replace=False)
            seed = int(self._rng.integers(0, 2**31 - 1))
            tree = IsolationTree(height_limit=self.height_limit_, random_state=seed)
            tree.fit(X[idx])
            self.trees_.append(tree)
        return self

    def _harmonic_number(self, i: int) -> float:
        if i <= 0:
            return 0.0
        return float(np.log(i) + 0.5772)

    def _avg_path_length(self, psi: int) -> float:
        # TODO T3a: implement c(psi) = 2 H(psi - 1) - 2 (psi - 1) / psi,
        # using self._harmonic_number for H(i). Handle psi <= 1 by
        # returning 0.0 (a subsample of size <= 1 cannot be split).
        raise NotImplementedError("TODO T3: implement the path length normalizer c(psi).")

    def anomaly_score(self, x: np.ndarray) -> float:
        # TODO T3b: average path_length(x) over self.trees_ to get E[h(x)],
        # then return s(x, psi) = 2 ** (-E[h(x)] / c(psi)) using
        # self._avg_path_length(self.psi_).
        raise NotImplementedError("TODO T3: implement the anomaly score.")

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        return np.asarray([self.anomaly_score(row) for row in X], dtype=np.float64)
