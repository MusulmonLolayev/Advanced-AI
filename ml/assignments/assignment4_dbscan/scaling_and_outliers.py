"""Compare DBSCAN under scaling and outlier settings."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.clustering.dbscan import DBSCANClustering
from advanced_ai.config import OUTLIER_DATA_PATH, RESULTS_DIR, SCALING_DATA_PATH
from advanced_ai.data_utils import load_outlier_bundle, load_scaling_bundle, standardize_features
from advanced_ai.metrics import cluster_sizes, noise_fraction
from advanced_ai.task_utils import print_section, require_file


def _plot(X: np.ndarray, labels: np.ndarray, filename: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    scatter = ax.scatter(X[:, 0], X[:, 1], c=labels, cmap="tab10", s=28)
    ax.set_title(title)
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.grid(True, alpha=0.3)
    fig.colorbar(scatter, ax=ax, shrink=0.82)
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / filename)
    plt.close(fig)


def main() -> None:
    scaling_bundle = load_scaling_bundle(require_file(SCALING_DATA_PATH))
    X_scale = scaling_bundle["X"].astype(np.float64)

    print_section("Scaling study")
    model_raw = DBSCANClustering(eps=10.0, min_pts=4)
    labels_raw = model_raw.fit_predict(X_scale)
    print(f"raw noise fraction = {noise_fraction(labels_raw):.4f}")
    print(f"raw cluster sizes = {cluster_sizes(labels_raw).tolist()}")
    _plot(X_scale, labels_raw, "scaling_raw.pdf", "Scaling study: raw features")

    X_std, _ = standardize_features(X_scale)
    model_std = DBSCANClustering(eps=0.7, min_pts=4)
    labels_std = model_std.fit_predict(X_std)
    print(f"standardized noise fraction = {noise_fraction(labels_std):.4f}")
    print(f"standardized cluster sizes = {cluster_sizes(labels_std).tolist()}")
    _plot(X_std, labels_std, "scaling_standardized.pdf", "Scaling study: standardized features")

    outlier_bundle = load_outlier_bundle(require_file(OUTLIER_DATA_PATH))
    X_out = outlier_bundle["X"].astype(np.float64)

    print_section("\nOutlier study")
    model_out = DBSCANClustering(eps=0.38, min_pts=4)
    labels_out = model_out.fit_predict(X_out)
    print(f"outlier noise fraction = {noise_fraction(labels_out):.4f}")
    print(f"outlier cluster sizes = {cluster_sizes(labels_out).tolist()}")
    _plot(X_out, labels_out, "outlier_dbscan.pdf", "Outlier study: DBSCAN labels")


if __name__ == "__main__":
    main()
