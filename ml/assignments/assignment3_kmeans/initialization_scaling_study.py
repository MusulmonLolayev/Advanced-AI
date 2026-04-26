"""Study initialization sensitivity for k-means."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.clustering.kmeans import KMeansClustering
from advanced_ai.config import INIT_STUDY_DATA_PATH, RANDOM_SEED, RESULTS_DIR
from advanced_ai.data_utils import load_init_study_bundle, standardize_features
from advanced_ai.metrics import cluster_sizes
from advanced_ai.task_utils import print_section, require_file


def _run_many(X: np.ndarray, tag: str) -> None:
    rows = []
    for seed in range(RANDOM_SEED, RANDOM_SEED + 10):
        model = KMeansClustering(n_clusters=3, max_iter=100, n_init=1, random_state=seed)
        model.fit(X)
        rows.append(
            {
                "seed": seed,
                "inertia": float(model.inertia_),
                "cluster_sizes": cluster_sizes(model.labels_, 3).tolist(),
            }
        )

    inertias = [row["inertia"] for row in rows]
    print(f"{tag} best   = {min(inertias):.4f}")
    print(f"{tag} median = {float(np.median(inertias)):.4f}")
    print(f"{tag} worst  = {max(inertias):.4f}")

    summary_lines = [f"Initialization study ({tag})", ""]
    for row in rows:
        summary_lines.append(
            f"seed={row['seed']} inertia={row['inertia']:.6f} cluster_sizes={row['cluster_sizes']}"
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / f"initialization_study_{tag}.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.plot([row["seed"] for row in rows], inertias, marker="o")
    ax.set_title(f"Initialization sensitivity ({tag})")
    ax.set_xlabel("random seed")
    ax.set_ylabel("inertia")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"initialization_study_{tag}.pdf")
    plt.close(fig)


def main() -> None:
    bundle = load_init_study_bundle(require_file(INIT_STUDY_DATA_PATH))
    X = bundle["X"].astype(np.float64)

    print_section("Initialization study on raw features")
    _run_many(X, tag="raw")

    print_section("\nInitialization study on standardized features")
    X_std, _ = standardize_features(X)
    _run_many(X_std, tag="standardized")


if __name__ == "__main__":
    main()
