"""k-NN starter.

Students are expected to complete the TODO blocks in this file only.
All task scripts, metrics, and experiment loops are already provided.
"""

from __future__ import annotations

import numpy as np


class KNearestNeighbor:
    """A k-NN model that supports classification, regression, and scoring."""

    def __init__(self) -> None:
        self.X_train: np.ndarray | None = None
        self.y_train: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> None:
        """Store training features and optional labels."""
        self.X_train = np.asarray(X, dtype=np.float64)
        self.y_train = None if y is None else np.asarray(y)

    def compute_distances_two_loops(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """Compute pairwise distances using a very explicit double loop."""
        self._check_is_fitted()
        X = np.asarray(X, dtype=np.float64)
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train), dtype=np.float64)

        ############################################################################
        # TODO: Compute the full pairwise distance matrix using two loops.         #
        #                                                                          #
        # Requirements:                                                            #
        # - support metric="l2"                                                    #
        # - support metric="l1"                                                    #
        # - support metric="cosine" where distance = 1 - cosine similarity        #
        # - do not use any external ML libraries                                   #
        ############################################################################
        raise NotImplementedError("TODO: implement compute_distances_two_loops")
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return dists

    def compute_distances_one_loop(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """Compute pairwise distances using a single loop over test points."""
        self._check_is_fitted()
        X = np.asarray(X, dtype=np.float64)
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train), dtype=np.float64)

        ############################################################################
        # TODO: Compute the full pairwise distance matrix using one loop.          #
        #                                                                          #
        # Requirements:                                                            #
        # - support metric="l2"                                                    #
        # - support metric="l1"                                                    #
        # - support metric="cosine"                                                #
        # - avoid the inner loop over training examples                            #
        ############################################################################
        raise NotImplementedError("TODO: implement compute_distances_one_loop")
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return dists

    def compute_distances_no_loops(self, X: np.ndarray, metric: str = "l2") -> np.ndarray:
        """Compute pairwise distances using fully vectorized NumPy."""
        self._check_is_fitted()
        X = np.asarray(X, dtype=np.float64)
        dists = np.zeros((X.shape[0], self.X_train.shape[0]), dtype=np.float64)

        ############################################################################
        # TODO: Compute the full pairwise distance matrix with no explicit loops.  #
        #                                                                          #
        # Requirements:                                                            #
        # - support metric="l2"                                                    #
        # - support metric="l1"                                                    #
        # - support metric="cosine"                                                #
        # - use NumPy broadcasting / linear algebra                                #
        ############################################################################
        raise NotImplementedError("TODO: implement compute_distances_no_loops")
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return dists

    def kneighbors(
        self,
        X: np.ndarray,
        k: int = 1,
        metric: str = "l2",
        num_loops: int = 0,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return distances and indices of the nearest neighbors."""
        dists = self._compute_distances(X, metric=metric, num_loops=num_loops)
        neighbor_idx = np.argsort(dists, axis=1)[:, :k]
        neighbor_dists = np.take_along_axis(dists, neighbor_idx, axis=1)
        return neighbor_dists, neighbor_idx

    def predict(
        self,
        X: np.ndarray,
        k: int = 1,
        metric: str = "l2",
        task: str = "classification",
        weighting: str = "uniform",
        num_loops: int = 0,
    ) -> np.ndarray:
        """Dispatch to classification or regression prediction."""
        neighbor_dists, neighbor_idx = self.kneighbors(X, k=k, metric=metric, num_loops=num_loops)
        if task == "classification":
            return self.predict_labels(neighbor_dists, neighbor_idx, weighting=weighting)
        if task == "regression":
            return self.predict_values(neighbor_dists, neighbor_idx, weighting=weighting)
        raise ValueError(f"Unsupported task: {task}")

    def predict_labels(
        self,
        neighbor_dists: np.ndarray,
        neighbor_idx: np.ndarray,
        weighting: str = "uniform",
    ) -> np.ndarray:
        """Predict class labels from nearest neighbors."""
        self._check_has_labels()
        y_pred = np.zeros(neighbor_idx.shape[0], dtype=self.y_train.dtype)

        ############################################################################
        # TODO: Predict one class label per row.                                   #
        #                                                                          #
        # Requirements:                                                            #
        # - support weighting="uniform"                                            #
        # - support weighting="distance" with weights = 1 / (d + 1e-12)           #
        # - break ties by choosing the smaller class label                         #
        ############################################################################
        raise NotImplementedError("TODO: implement predict_labels")
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return y_pred

    def predict_values(
        self,
        neighbor_dists: np.ndarray,
        neighbor_idx: np.ndarray,
        weighting: str = "uniform",
    ) -> np.ndarray:
        """Predict continuous targets from nearest neighbors."""
        self._check_has_labels()
        y_pred = np.zeros(neighbor_idx.shape[0], dtype=np.float64)

        ############################################################################
        # TODO: Predict one regression value per row.                              #
        #                                                                          #
        # Requirements:                                                            #
        # - support weighting="uniform" as the simple mean                         #
        # - support weighting="distance" with weights = 1 / (d + 1e-12)           #
        ############################################################################
        raise NotImplementedError("TODO: implement predict_values")
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return y_pred

    def anomaly_scores(
        self,
        X: np.ndarray,
        k: int = 5,
        metric: str = "l2",
        num_loops: int = 0,
    ) -> np.ndarray:
        """Use distance to the k-th nearest neighbor as anomaly score."""
        neighbor_dists, _ = self.kneighbors(X, k=k, metric=metric, num_loops=num_loops)
        return neighbor_dists[:, -1]

    def _compute_distances(self, X: np.ndarray, metric: str, num_loops: int) -> np.ndarray:
        if num_loops == 2:
            return self.compute_distances_two_loops(X, metric=metric)
        if num_loops == 1:
            return self.compute_distances_one_loop(X, metric=metric)
        if num_loops == 0:
            return self.compute_distances_no_loops(X, metric=metric)
        raise ValueError(f"Unsupported num_loops: {num_loops}")

    def _check_is_fitted(self) -> None:
        if self.X_train is None:
            raise ValueError("Call fit before using the model.")

    def _check_has_labels(self) -> None:
        self._check_is_fitted()
        if self.y_train is None:
            raise ValueError("This operation requires training labels.")
