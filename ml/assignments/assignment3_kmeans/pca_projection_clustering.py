"""Visualize k-means assignments in a provided 2D PCA projection."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.clustering.kmeans import KMeansClustering
from advanced_ai.config import PCA_CLUSTERING_DATA_PATH, RESULTS_DIR, RANDOM_SEED
from advanced_ai.data_utils import load_projection_bundle, standardize_features
from advanced_ai.metrics import cluster_sizes
from advanced_ai.task_utils import print_section, require_file


def _plot_projection(X_pca2: np.ndarray, labels: np.ndarray, title: str, filename: str) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    scatter = ax.scatter(X_pca2[:, 0], X_pca2[:, 1], c=labels, cmap="tab10", s=28)
    ax.set_title(title)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.grid(True, alpha=0.3)
    fig.colorbar(scatter, ax=ax, shrink=0.82)
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / filename)
    plt.close(fig)


def main() -> None:
    bundle = load_projection_bundle(require_file(PCA_CLUSTERING_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    X_pca2 = bundle["X_pca2"].astype(np.float64)
    summary_lines = ["PCA projection clustering summary", ""]

    print_section("k-means in original feature space")
    model_raw = KMeansClustering(n_clusters=3, max_iter=100, n_init=10, random_state=RANDOM_SEED)
    labels_raw = model_raw.fit_predict(X)
    print(f"raw inertia = {float(model_raw.inertia_):.4f}")
    print(f"raw cluster sizes = {cluster_sizes(labels_raw, 3).tolist()}")
    summary_lines.append(f"raw inertia = {float(model_raw.inertia_):.6f}")
    summary_lines.append(f"raw cluster sizes = {cluster_sizes(labels_raw, 3).tolist()}")
    _plot_projection(X_pca2, labels_raw, "Assignments from raw-space clustering", "pca_projection_raw_labels.pdf")

    print_section("\nk-means after standardization")
    X_std, _ = standardize_features(X)
    model_std = KMeansClustering(n_clusters=3, max_iter=100, n_init=10, random_state=RANDOM_SEED)
    labels_std = model_std.fit_predict(X_std)
    print(f"standardized inertia = {float(model_std.inertia_):.4f}")
    print(f"standardized cluster sizes = {cluster_sizes(labels_std, 3).tolist()}")
    summary_lines.append(f"standardized inertia = {float(model_std.inertia_):.6f}")
    summary_lines.append(f"standardized cluster sizes = {cluster_sizes(labels_std, 3).tolist()}")
    _plot_projection(X_pca2, labels_std, "Assignments after standardization", "pca_projection_standardized_labels.pdf")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "pca_projection_summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
