"""Run DBSCAN on the prepared Iris dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.clustering.dbscan import DBSCANClustering
from advanced_ai.config import EPS_CHOICES, IRIS_DATA_PATH, RESULTS_DIR
from advanced_ai.data_utils import load_iris_bundle, standardize_features
from advanced_ai.metrics import cluster_purity, cluster_sizes, noise_fraction
from advanced_ai.task_utils import print_section, require_file


def _sweep(X: np.ndarray, y: np.ndarray, tag: str) -> None:
    rows = []
    summary_lines = [f"Iris DBSCAN summary ({tag})", ""]
    for eps in EPS_CHOICES:
        model = DBSCANClustering(eps=eps, min_pts=4)
        labels = model.fit_predict(X)
        rows.append((eps, len(set(labels)) - (1 if -1 in labels else 0), noise_fraction(labels), cluster_purity(y, labels)))
        summary_lines.append(
            f"eps={eps:.2f} clusters={rows[-1][1]} noise_fraction={rows[-1][2]:.6f} purity={rows[-1][3]:.6f}"
        )
        print(
            f"{tag} eps={eps:.2f} clusters={rows[-1][1]} noise={rows[-1][2]:.4f} purity={rows[-1][3]:.4f}"
        )
        if eps == EPS_CHOICES[1]:
            summary_lines.append(f"cluster sizes = {cluster_sizes(labels).tolist()}")

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot([row[0] for row in rows], [row[1] for row in rows], marker="o")
    ax.set_title(f"Iris DBSCAN cluster count ({tag})")
    ax.set_xlabel(r"$\varepsilon$")
    ax.set_ylabel("clusters")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RESULTS_DIR / f"iris_dbscan_clusters_{tag}.pdf")
    (RESULTS_DIR / f"iris_dbscan_summary_{tag}.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    plt.close(fig)


def main() -> None:
    bundle = load_iris_bundle(require_file(IRIS_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)

    print_section("Iris DBSCAN on raw features")
    _sweep(X, y, tag="raw")

    print_section("\nIris DBSCAN on standardized features")
    X_std, _ = standardize_features(X)
    _sweep(X_std, y, tag="standardized")


if __name__ == "__main__":
    main()
