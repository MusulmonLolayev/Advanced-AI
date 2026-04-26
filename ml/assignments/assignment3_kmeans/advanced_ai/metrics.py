"""Simple clustering metrics and summaries for Assignment 3."""

from __future__ import annotations

import numpy as np


def cluster_sizes(labels: np.ndarray, n_clusters: int) -> np.ndarray:
    labels = np.asarray(labels, dtype=int)
    return np.array([(labels == r).sum() for r in range(n_clusters)], dtype=int)


def cluster_purity(y_true: np.ndarray, labels: np.ndarray, n_clusters: int) -> float:
    y_true = np.asarray(y_true)
    labels = np.asarray(labels, dtype=int)
    total = labels.shape[0]
    correct = 0
    for r in range(n_clusters):
        cluster_targets = y_true[labels == r]
        if cluster_targets.size == 0:
            continue
        values, counts = np.unique(cluster_targets, return_counts=True)
        correct += int(counts[np.argmax(counts)])
    return float(correct) / float(total)


def contingency_table(y_true: np.ndarray, labels: np.ndarray, n_clusters: int) -> dict[int, dict[str, int]]:
    y_true = np.asarray(y_true)
    labels = np.asarray(labels, dtype=int)
    table: dict[int, dict[str, int]] = {}
    for r in range(n_clusters):
        cluster_targets = y_true[labels == r]
        values, counts = np.unique(cluster_targets, return_counts=True)
        table[r] = {str(v): int(c) for v, c in zip(values, counts)}
    return table
