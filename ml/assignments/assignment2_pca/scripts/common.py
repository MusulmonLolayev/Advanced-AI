"""Shared helpers for instructor-side PCA data preparation."""

from __future__ import annotations

from pathlib import Path

import numpy as np


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_bundle(path: str | Path, **arrays: np.ndarray) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    np.savez_compressed(path, **arrays)
    return path


def make_pca_core_dataset(seed: int = 231) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    t = np.linspace(-2.0, 2.0, 24)
    x1 = 2.5 * t + 0.15 * rng.normal(size=t.shape[0])
    x2 = 1.2 * t + 0.15 * rng.normal(size=t.shape[0])
    X = np.stack([x1, x2], axis=1)
    return {"X": X}


def make_text_embeddings_bundle(seed: int = 231) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_queries = 12
    docs_per_topic = 8
    topics = np.array(["vision", "language", "security"])
    latent_dim = 3
    embed_dim = 24
    topic_centers = np.array(
        [
            [2.0, -0.5, 0.2],
            [-0.2, 2.2, 0.4],
            [0.4, -0.3, 2.4],
        ],
        dtype=np.float64,
    )
    projection = rng.normal(size=(latent_dim, embed_dim))
    projection /= np.linalg.norm(projection, axis=0, keepdims=True)

    query_topics = np.repeat(np.arange(3), n_queries // 3)
    doc_topics = np.repeat(np.arange(3), docs_per_topic)

    query_latent = topic_centers[query_topics] + 0.35 * rng.normal(size=(n_queries, latent_dim))
    doc_latent = topic_centers[doc_topics] + 0.40 * rng.normal(size=(docs_per_topic * 3, latent_dim))

    query_embeddings = query_latent @ projection + 0.05 * rng.normal(size=(n_queries, embed_dim))
    doc_embeddings = doc_latent @ projection + 0.05 * rng.normal(size=(docs_per_topic * 3, embed_dim))

    relevance = (query_topics[:, None] == doc_topics[None, :]).astype(int)
    query_lengths = rng.integers(6, 16, size=n_queries)
    doc_lengths = rng.integers(8, 40, size=docs_per_topic * 3)

    return {
        "query_embeddings": query_embeddings,
        "doc_embeddings": doc_embeddings,
        "relevance": relevance,
        "query_lengths": query_lengths,
        "doc_lengths": doc_lengths,
        "query_topics": query_topics,
        "doc_topics": doc_topics,
        "topic_names": topics,
    }


def make_anomaly_bundle(seed: int = 231) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_train = 240
    n_val = 100
    n_test = 120
    n_features = 10

    base_cov = np.diag(np.linspace(2.2, 0.3, n_features))
    transform = rng.normal(size=(n_features, n_features))
    transform, _ = np.linalg.qr(transform)
    cov = transform @ base_cov @ transform.T

    X_train = rng.multivariate_normal(np.zeros(n_features), cov, size=n_train)
    X_val_normal = rng.multivariate_normal(np.zeros(n_features), cov, size=n_val - 20)
    X_val_anom = rng.multivariate_normal(np.full(n_features, 4.0), 1.5 * np.eye(n_features), size=20)
    X_val = np.vstack([X_val_normal, X_val_anom])
    y_val = np.concatenate([np.zeros(X_val_normal.shape[0], dtype=int), np.ones(X_val_anom.shape[0], dtype=int)])

    X_test_normal = rng.multivariate_normal(np.zeros(n_features), cov, size=n_test - 24)
    X_test_anom = rng.multivariate_normal(np.full(n_features, 4.0), 1.5 * np.eye(n_features), size=24)
    X_test = np.vstack([X_test_normal, X_test_anom])
    y_test = np.concatenate([np.zeros(X_test_normal.shape[0], dtype=int), np.ones(X_test_anom.shape[0], dtype=int)])

    return {
        "X_train": X_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
    }


def make_knn_comparison_bundle(seed: int = 231) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_per_class = 120
    latent_dim = 2
    embed_dim = 18
    class_centers = np.array([[-2.0, -1.0], [2.0, 1.5]], dtype=np.float64)
    projection = rng.normal(size=(latent_dim, embed_dim))
    projection /= np.linalg.norm(projection, axis=0, keepdims=True)

    X_latent = np.vstack(
        [
            class_centers[0] + 0.8 * rng.normal(size=(n_per_class, latent_dim)),
            class_centers[1] + 0.8 * rng.normal(size=(n_per_class, latent_dim)),
        ]
    )
    y = np.concatenate([np.zeros(n_per_class, dtype=int), np.ones(n_per_class, dtype=int)])
    X = X_latent @ projection + 0.08 * rng.normal(size=(2 * n_per_class, embed_dim))

    idx = rng.permutation(X.shape[0])
    X = X[idx]
    y = y[idx]

    n_train = 160
    n_val = 40
    return {
        "X_train": X[:n_train],
        "y_train": y[:n_train],
        "X_val": X[n_train : n_train + n_val],
        "y_val": y[n_train : n_train + n_val],
        "X_test": X[n_train + n_val :],
        "y_test": y[n_train + n_val :],
    }
