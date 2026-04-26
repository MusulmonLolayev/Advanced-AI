"""k-means starter scaffold used by the Assignment 3 task runners."""

from __future__ import annotations

import numpy as np


class KMeansClustering:
    """Simple NumPy k-means model with restart support."""

    EPS = 1e-12

    def __init__(
        self,
        n_clusters: int,
        max_iter: int = 100,
        tol: float = 1e-6,
        n_init: int = 10,
        random_state: int = 231,
    ) -> None:
        self.n_clusters = int(n_clusters)
        self.max_iter = int(max_iter)
        self.tol = float(tol)
        self.n_init = int(n_init)
        self.random_state = int(random_state)

        self.cluster_centers_: np.ndarray | None = None
        self.labels_: np.ndarray | None = None
        self.inertia_: float | None = None
        self.n_iter_: int | None = None

    def fit(self, X: np.ndarray) -> "KMeansClustering":
        """TODO K1: fit k-means with repeated random restarts."""
        # TODO: run k-means n_init times and keep the run with smallest inertia.
        raise NotImplementedError("TODO K1: implement fit.")

    def fit_once(self, X: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, float, int]:
        """TODO K1/K4: run one k-means solve from one random initialization."""
        # TODO: initialize centroids, alternate assignment/update, and return one full run.
        raise NotImplementedError("TODO K1: implement fit_once.")

    def initialize_centroids(self, X: np.ndarray, seed: int) -> np.ndarray:
        """TODO K1: sample initial centroids from the training examples."""
        # TODO: choose n_clusters distinct examples as initial centroids.
        raise NotImplementedError("TODO K1: implement initialize_centroids.")

    def assign_labels(self, X: np.ndarray, centroids: np.ndarray) -> np.ndarray:
        """TODO K1: assign each example to its nearest centroid."""
        # TODO: compute squared Euclidean distances and return argmin labels.
        raise NotImplementedError("TODO K1: implement assign_labels.")

    def update_centroids(self, X: np.ndarray, labels: np.ndarray, old_centroids: np.ndarray) -> np.ndarray:
        """TODO K1: recompute cluster means with empty-cluster handling."""
        # TODO: replace each centroid by the mean of its assigned examples.
        raise NotImplementedError("TODO K1: implement update_centroids.")

    def compute_inertia(self, X: np.ndarray, labels: np.ndarray, centroids: np.ndarray) -> float:
        """TODO K1: compute the within-cluster sum of squares."""
        # TODO: sum squared distances to the assigned centroids.
        raise NotImplementedError("TODO K1: implement compute_inertia.")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """TODO K1: assign new examples to learned centroids."""
        # TODO: call assign_labels with the fitted cluster centers.
        raise NotImplementedError("TODO K1: implement predict.")

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """Fit the model and return the training assignments."""
        self.fit(X)
        self._check_is_fitted()
        return self.labels_

    def _check_is_fitted(self) -> None:
        if self.cluster_centers_ is None or self.labels_ is None or self.inertia_ is None:
            raise ValueError("Call fit before using the k-means model.")
