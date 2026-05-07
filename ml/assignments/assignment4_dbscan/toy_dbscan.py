"""Run DBSCAN on the prepared toy dataset."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.clustering.dbscan import DBSCANClustering
from advanced_ai.config import RESULTS_DIR, TOY_DATA_PATH
from advanced_ai.data_utils import load_toy_bundle
from advanced_ai.metrics import cluster_purity, cluster_sizes, noise_fraction
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
    bundle = load_toy_bundle(require_file(TOY_DATA_PATH))
    X = bundle["X"].astype(np.float64)
    y = bundle["y"].astype(np.int64)

    print_section("Toy DBSCAN")
    model = DBSCANClustering(eps=0.38, min_pts=4)
    labels = model.fit_predict(X)
    print(f"clusters = {len(set(labels)) - (1 if -1 in labels else 0)}")
    print(f"noise fraction = {noise_fraction(labels):.4f}")
    print(f"cluster sizes = {cluster_sizes(labels).tolist()}")
    print(f"purity = {cluster_purity(y, labels):.4f}")
    _plot(X, labels, "toy_dbscan_labels.pdf", "Toy DBSCAN clustering")


if __name__ == "__main__":
    main()
