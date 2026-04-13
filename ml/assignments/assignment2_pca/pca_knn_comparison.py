"""Compare k-NN on raw features versus PCA-reduced features."""

from __future__ import annotations

import time

import numpy as np

from advanced_ai.config import KNN_COMPARISON_DATA_PATH, KNN_K_CHOICES, N_COMPONENT_CHOICES
from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor
from advanced_ai.data_utils import load_pca_knn_bundle, standardize_from_train
from advanced_ai.pca import PrincipalComponentAnalysis
from advanced_ai.task_utils import print_section, require_file


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


def _sweep_knn(X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, label: str) -> tuple[dict[str, object], float]:
    best: dict[str, object] | None = None
    for k in KNN_K_CHOICES:
        model = KNearestNeighbor().fit(X_train, y_train)
        start = time.perf_counter()
        y_val_pred = model.predict(X_val, k=k)
        elapsed = time.perf_counter() - start
        val_acc = _accuracy(y_val, y_val_pred)
        row = {"k": k, "val_accuracy": val_acc, "val_time": elapsed}
        if best is None or val_acc > best["val_accuracy"]:
            best = row

    assert best is not None
    model = KNearestNeighbor().fit(X_train, y_train)
    start = time.perf_counter()
    y_test_pred = model.predict(X_test, k=int(best["k"]))
    test_time = time.perf_counter() - start
    best["test_accuracy"] = _accuracy(y_test, y_test_pred)
    best["test_time"] = test_time
    print_section(label)
    print(f"k={best['k']:>2d} val_accuracy={best['val_accuracy']:.4f} test_accuracy={best['test_accuracy']:.4f}")
    print(f"val_time={best['val_time']:.4f}s test_time={best['test_time']:.4f}s")
    return best, float(best["val_time"])


def main() -> None:
    bundle = load_pca_knn_bundle(require_file(KNN_COMPARISON_DATA_PATH))
    X_train = bundle["X_train"]
    y_train = bundle["y_train"]
    X_val = bundle["X_val"]
    y_val = bundle["y_val"]
    X_test = bundle["X_test"]
    y_test = bundle["y_test"]

    X_train_std, X_val_std, X_test_std, _ = standardize_from_train(X_train, X_val, X_test)

    raw_best, _ = _sweep_knn(X_train_std, y_train, X_val_std, y_val, X_test_std, y_test, "Raw standardized features")

    pca = PrincipalComponentAnalysis()
    pca.fit(X_train_std, method="svd")

    best_pca: dict[str, object] | None = None
    for n_components in N_COMPONENT_CHOICES:
        Z_train = pca.transform(X_train_std, n_components=n_components)
        Z_val = pca.transform(X_val_std, n_components=n_components)
        Z_test = pca.transform(X_test_std, n_components=n_components)
        candidate, _ = _sweep_knn(
            Z_train,
            y_train,
            Z_val,
            y_val,
            Z_test,
            y_test,
            f"PCA-reduced features (n_components={n_components})",
        )
        candidate["n_components"] = n_components
        if best_pca is None or candidate["val_accuracy"] > best_pca["val_accuracy"]:
            best_pca = candidate

    assert best_pca is not None
    print_section("Comparison summary")
    print(
        f"raw_best_acc={raw_best['test_accuracy']:.4f} | "
        f"pca_best_acc={best_pca['test_accuracy']:.4f} | "
        f"best_n_components={best_pca['n_components']}"
    )


if __name__ == "__main__":
    main()
