"""Text-based self checks for the k-NN implementation."""

from __future__ import annotations

import numpy as np

from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor


def _print_result(name: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


def _check_close(name: str, actual: np.ndarray, expected: np.ndarray, atol: float = 1e-8) -> None:
    passed = np.allclose(actual, expected, atol=atol)
    detail = f"max abs diff = {np.max(np.abs(actual - expected)):.3e}"
    _print_result(name, passed, detail)


def run_distance_checks(model: KNearestNeighbor) -> None:
    X_train = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 2.0],
        ]
    )
    X_test = np.array(
        [
            [1.0, 1.0],
            [2.0, 0.0],
        ]
    )
    model.fit(X_train, np.array([0, 1, 1]))

    expected_l2 = np.array(
        [
            [np.sqrt(2.0), 1.0, np.sqrt(2.0)],
            [2.0, 1.0, np.sqrt(8.0)],
        ]
    )
    expected_l1 = np.array(
        [
            [2.0, 1.0, 2.0],
            [2.0, 1.0, 4.0],
        ]
    )

    for metric, expected in [("l2", expected_l2), ("l1", expected_l1)]:
        try:
            two_loop = model.compute_distances_two_loops(X_test, metric=metric)
            one_loop = model.compute_distances_one_loop(X_test, metric=metric)
            no_loops = model.compute_distances_no_loops(X_test, metric=metric)
        except NotImplementedError as exc:
            _print_result(f"{metric} distances", False, str(exc))
            continue

        _check_close(f"{metric} two_loops", two_loop, expected)
        _check_close(f"{metric} one_loop", one_loop, expected)
        _check_close(f"{metric} no_loops", no_loops, expected)

    try:
        cosine = model.compute_distances_no_loops(X_test, metric="cosine")
        _print_result("cosine distance shape", cosine.shape == (2, 3), f"shape = {cosine.shape}")
    except NotImplementedError as exc:
        _print_result("cosine distance", False, str(exc))


def run_prediction_checks(model: KNearestNeighbor) -> None:
    X_train = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [2.0, 2.0],
        ]
    )
    y_class = np.array([0, 0, 1, 1])
    y_reg = np.array([0.0, 0.0, 1.0, 4.0])
    X_test = np.array([[0.9, 0.1], [0.2, 0.9]])

    model.fit(X_train, y_class)
    try:
        pred = model.predict(X_test, k=3, metric="l2", task="classification", weighting="uniform")
        _print_result("classification prediction shape", pred.shape == (2,), f"pred = {pred}")
    except NotImplementedError as exc:
        _print_result("classification prediction", False, str(exc))

    model.fit(X_train, y_reg)
    try:
        pred = model.predict(X_test, k=2, metric="l2", task="regression", weighting="uniform")
        _print_result("regression prediction shape", pred.shape == (2,), f"pred = {np.round(pred, 4)}")
    except NotImplementedError as exc:
        _print_result("regression prediction", False, str(exc))

    model.fit(X_train)
    try:
        scores = model.anomaly_scores(X_test, k=2, metric="l2")
        _print_result("anomaly scores shape", scores.shape == (2,), f"scores = {np.round(scores, 4)}")
    except NotImplementedError as exc:
        _print_result("anomaly scores", False, str(exc))


def main() -> None:
    print("Advanced AI Assignment 1 self-checks")
    print("------------------------------------")
    model = KNearestNeighbor()
    run_distance_checks(model)
    run_prediction_checks(model)


if __name__ == "__main__":
    main()
