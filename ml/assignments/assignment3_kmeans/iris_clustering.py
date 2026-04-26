"""Run the Iris clustering task for Assignment 3."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.clustering.kmeans import KMeansClustering
from advanced_ai.config import IRIS_CLUSTERING_DATA_PATH, K_CHOICES, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_iris_bundle, standardize_features
from advanced_ai.metrics import cluster_purity, cluster_sizes, contingency_table
from advanced_ai.task_utils import print_section, require_file


def _run_sweep(X: np.ndarray, y: np.ndarray, tag: str) -> None:
    rows = []
    summary_lines = [f"Iris clustering summary ({tag})", ""]
    for k in K_CHOICES:
        model = KMeansClustering(n_clusters=k, max_iter=100, n_init=10, random_state=RANDOM_SEED)
        labels = model.fit_predict(X)
        purity = cluster_purity(y, labels, n_clusters=k)
        rows.append((k, float(model.inertia_), purity))
        summary_lines.append(f"k={k} inertia={float(model.inertia_):.6f} purity={purity:.6f}")
        print(f"{tag} k={k} inertia={float(model.inertia_):.4f} purity={purity:.4f}")
        if k == 3:
            size_summary = cluster_sizes(labels, 3).tolist()
            contingency_summary = contingency_table(y, labels, 3)
            print(f"{tag} cluster sizes: {size_summary}")
            print(f"{tag} contingency: {contingency_summary}")
            summary_lines.append(f"cluster sizes (k=3): {size_summary}")
            summary_lines.append(f"contingency (k=3): {contingency_summary}")

    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.plot([row[0] for row in rows], [row[1] for row in rows], marker="o")
    ax.set_title(f"Iris inertia sweep ({tag})")
    ax.set_xlabel("k")
    ax.set_ylabel("inertia")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / f"iris_inertia_{tag}.pdf")
    (RESULTS_DIR / f"iris_summary_{tag}.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    plt.close(fig)


def main() -> None:
    bundle = load_iris_bundle(require_file(IRIS_CLUSTERING_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"]

    print_section("Iris clustering on raw features")
    _run_sweep(X, y, tag="raw")

    print_section("\nIris clustering on standardized features")
    X_std, _ = standardize_features(X)
    _run_sweep(X_std, y, tag="standardized")


if __name__ == "__main__":
    main()
