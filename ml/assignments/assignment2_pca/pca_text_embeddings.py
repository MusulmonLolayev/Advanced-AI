"""Run the PCA text-embedding visualization task."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import RESULTS_DIR, TEXT_EMBEDDINGS_DATA_PATH
from advanced_ai.data_utils import load_text_embeddings_bundle
from advanced_ai.pca import PrincipalComponentAnalysis
from advanced_ai.task_utils import print_section, require_file


def main() -> None:
    bundle = load_text_embeddings_bundle(require_file(TEXT_EMBEDDINGS_DATA_PATH))
    X = np.vstack([bundle["query_embeddings"], bundle["doc_embeddings"]])
    query_topics = bundle["query_topics"]
    doc_topics = bundle["doc_topics"]
    topic_names = [str(name) for name in bundle["topic_names"]]

    labels = np.concatenate([query_topics, doc_topics])
    point_kinds = np.concatenate(
        [np.zeros_like(query_topics, dtype=int), np.ones_like(doc_topics, dtype=int)]
    )

    pca = PrincipalComponentAnalysis()
    Z = pca.fit_transform(X, method="svd", n_components=2)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#2166ac", "#d95f02", "#1b9e77"]
    markers = ["o", "x"]
    for topic_id, topic_name in enumerate(topic_names):
        for kind, marker_name in enumerate(markers):
            mask = (labels == topic_id) & (point_kinds == kind)
            if not np.any(mask):
                continue
            ax.scatter(
                Z[mask, 0],
                Z[mask, 1],
                s=36,
                marker=marker_name,
                color=colors[topic_id],
                alpha=0.85,
                label=f"{topic_name} {'queries' if kind == 0 else 'docs'}",
            )
    ax.set_title("PCA of Synthetic Text Embeddings")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "pca_text_embeddings_2d.pdf")
    plt.close(fig)

    print_section("Explained variance")
    ratios = pca.explained_variance_ratio()
    print(np.round(ratios[:5], 4))
    print_section("First two coordinates")
    print(np.round(Z[:5], 4))
    print(f"Saved figure: {RESULTS_DIR / 'pca_text_embeddings_2d.pdf'}")


if __name__ == "__main__":
    main()
