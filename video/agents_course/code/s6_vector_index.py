"""s6 · Embeddings in a vector index — IDEA SNIPPET, not run (needs faiss-cpu and an embedding model)."""
import faiss
import numpy as np


def build(vectors, m=32, ef_construction=200):
    """HNSW: a layered neighbour graph. Search is approximate: fast, but it can miss a true neighbour."""
    x = np.asarray(vectors, dtype="float32")
    faiss.normalize_L2(x)                                   # cosine similarity = inner product on unit vectors
    index = faiss.IndexHNSWFlat(x.shape[1], m, faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction = ef_construction
    index.add(x)
    return index


def search(index, query_vector, k=10, ef_search=64):
    index.hnsw.efSearch = ef_search                         # the knob: higher = better recall, slower queries
    q = np.asarray([query_vector], dtype="float32")
    faiss.normalize_L2(q)
    scores, ids = index.search(q, k)
    return list(zip(ids[0], scores[0]))
# Below ~100k vectors a flat (exact) scan is often fast enough; measure recall@k against it before tuning.
