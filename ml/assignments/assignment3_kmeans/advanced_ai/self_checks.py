"""Text-based self checks for the k-means implementation."""

from __future__ import annotations

import numpy as np

from advanced_ai.clustering.kmeans import KMeansClustering


def _print_result(name: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


def run_basic_checks() -> None:
    X = np.array(
        [
            [1.0, 1.0],
            [1.0, 2.0],
            [5.0, 4.0],
            [6.0, 5.0],
        ]
    )
    model = KMeansClustering(n_clusters=2, max_iter=20, n_init=2, random_state=7)

    try:
        init = model.initialize_centroids(X, seed=7)
        _print_result("initialize_centroids shape", init.shape == (2, 2), f"shape = {init.shape}")
    except NotImplementedError as exc:
        _print_result("initialize_centroids", False, str(exc))
        return

    try:
        labels = model.assign_labels(X, np.array([[1.0, 1.0], [6.0, 5.0]]))
        _print_result("assign_labels shape", labels.shape == (4,), f"shape = {labels.shape}")
        _print_result("assign_labels range", np.all((labels >= 0) & (labels < 2)), f"labels = {labels.tolist()}")
    except NotImplementedError as exc:
        _print_result("assign_labels", False, str(exc))
        return

    try:
        centroids = model.update_centroids(X, np.array([0, 0, 1, 1]), np.array([[1.0, 1.0], [6.0, 5.0]]))
        expected = np.array([[1.0, 1.5], [5.5, 4.5]])
        passed = np.allclose(centroids, expected, atol=1e-8)
        _print_result("update_centroids", passed, f"centroids = {centroids.tolist()}")
    except NotImplementedError as exc:
        _print_result("update_centroids", False, str(exc))
        return

    try:
        inertia = model.compute_inertia(X, np.array([0, 0, 1, 1]), np.array([[1.0, 1.5], [5.5, 4.5]]))
        _print_result("compute_inertia", np.isclose(inertia, 1.5, atol=1e-8), f"inertia = {inertia:.6f}")
    except NotImplementedError as exc:
        _print_result("compute_inertia", False, str(exc))
        return

    try:
        model.fit(X)
        _print_result("fit cluster_centers_", model.cluster_centers_ is not None, "fit completed")
        _print_result("fit labels_", model.labels_ is not None, f"labels = {model.labels_.tolist()}")
        _print_result("fit inertia_", model.inertia_ is not None, f"inertia = {float(model.inertia_):.6f}")
    except NotImplementedError as exc:
        _print_result("fit", False, str(exc))


def main() -> None:
    print("Advanced AI Assignment 3 self-checks")
    print("------------------------------------")
    run_basic_checks()


if __name__ == "__main__":
    main()
