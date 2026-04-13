"""Optional extension: compare PCA with and without whitening."""

from __future__ import annotations

import numpy as np

from advanced_ai.config import KNN_COMPARISON_DATA_PATH
from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor
from advanced_ai.data_utils import load_pca_knn_bundle, standardize_from_train
from advanced_ai.pca import PrincipalComponentAnalysis
from advanced_ai.task_utils import print_section, require_file


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


def _run_knn(X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, k: int = 5) -> tuple[float, float]:
    model = KNearestNeighbor().fit(X_train, y_train)
    val_pred = model.predict(X_val, k=k)
    test_pred = model.predict(X_test, k=k)
    return _accuracy(y_val, val_pred), _accuracy(y_test, test_pred)


def main() -> None:
    bundle = load_pca_knn_bundle(require_file(KNN_COMPARISON_DATA_PATH))
    X_train = bundle["X_train"]
    y_train = bundle["y_train"]
    X_val = bundle["X_val"]
    y_val = bundle["y_val"]
    X_test = bundle["X_test"]
    y_test = bundle["y_test"]

    X_train_std, X_val_std, X_test_std, _ = standardize_from_train(X_train, X_val, X_test)

    pca = PrincipalComponentAnalysis()
    pca.fit(X_train_std, method="svd")
    n_components = 5
    Z_train = pca.transform(X_train_std, n_components=n_components)
    Z_val = pca.transform(X_val_std, n_components=n_components)
    Z_test = pca.transform(X_test_std, n_components=n_components)

    val_plain, test_plain = _run_knn(Z_train, y_train, Z_val, y_val, Z_test, y_test, k=5)

    eigenvalues = pca.eigenvalues_[:n_components]
    whitening = np.sqrt(np.maximum(eigenvalues, 1e-12))
    Z_train_white = Z_train / whitening
    Z_val_white = Z_val / whitening
    Z_test_white = Z_test / whitening
    val_white, test_white = _run_knn(Z_train_white, y_train, Z_val_white, y_val, Z_test_white, y_test, k=5)

    print_section("Whitening comparison")
    print(f"plain_pca   val_accuracy={val_plain:.4f} test_accuracy={test_plain:.4f}")
    print(f"whitened    val_accuracy={val_white:.4f} test_accuracy={test_white:.4f}")


if __name__ == "__main__":
    main()
