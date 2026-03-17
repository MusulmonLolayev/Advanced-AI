"""Optional text retrieval extension using prepared embeddings."""

from __future__ import annotations

import numpy as np

from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor
from advanced_ai.config import RETRIEVAL_DATA_PATH
from advanced_ai.data_utils import load_retrieval_bundle
from advanced_ai.metrics import mean_reciprocal_rank, recall_at_k
from advanced_ai.task_utils import print_section, require_file


def main() -> None:
    bundle = load_retrieval_bundle(require_file(RETRIEVAL_DATA_PATH))
    model = KNearestNeighbor()
    model.fit(bundle["doc_embeddings"])

    dists = model.compute_distances_no_loops(bundle["query_embeddings"], metric="cosine")
    ranked_idx = np.argsort(dists, axis=1)

    r5 = recall_at_k(bundle["relevance"], ranked_idx, k=5)
    r10 = recall_at_k(bundle["relevance"], ranked_idx, k=10)
    mrr = mean_reciprocal_rank(bundle["relevance"], ranked_idx)

    first_relevant_rank = np.full(bundle["query_embeddings"].shape[0], fill_value=np.nan, dtype=np.float64)
    for i in range(bundle["query_embeddings"].shape[0]):
        ordered_relevance = bundle["relevance"][i, ranked_idx[i]]
        hits = np.flatnonzero(ordered_relevance > 0)
        if hits.size > 0:
            first_relevant_rank[i] = hits[0] + 1

    valid = ~np.isnan(first_relevant_rank)
    length_corr = 0.0
    if np.sum(valid) > 1:
        length_corr = float(np.corrcoef(bundle["query_lengths"][valid], first_relevant_rank[valid])[0, 1])

    print_section("Optional retrieval report")
    print(f"Recall@5  = {r5:.4f}")
    print(f"Recall@10 = {r10:.4f}")
    print(f"MRR       = {mrr:.4f}")
    print(f"corr(query_length, first_relevant_rank) = {length_corr:.4f}")


if __name__ == "__main__":
    main()
