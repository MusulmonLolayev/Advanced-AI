"""Simple clustering metrics for Assignment 4."""

from __future__ import annotations

import numpy as np


def cluster_sizes(labels: np.ndarray) -> np.ndarray:
    labels = np.asarray(labels)
    if labels.size == 0:
        return np.array([], dtype=int)
    labels = labels[labels != -1]
    if labels.size == 0:
        return np.array([], dtype=int)
    unique, counts = np.unique(labels, return_counts=True)
    order = np.argsort(unique)
    return counts[order]


def contingency_table(y_true: np.ndarray, labels: np.ndarray) -> dict[int, dict[int, int]]:
    y_true = np.asarray(y_true)
    labels = np.asarray(labels)
    table: dict[int, dict[int, int]] = {}
    for true_label in np.unique(y_true):
        mask_true = y_true == true_label
        row: dict[int, int] = {}
        for pred_label in np.unique(labels):
            row[int(pred_label)] = int(np.sum(mask_true & (labels == pred_label)))
        table[int(true_label)] = row
    return table


def cluster_purity(y_true: np.ndarray, labels: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    labels = np.asarray(labels)
    if y_true.size == 0:
        return 0.0
    purity = 0
    for pred_label in np.unique(labels):
        mask = labels == pred_label
        if not np.any(mask):
            continue
        _, counts = np.unique(y_true[mask], return_counts=True)
        purity += int(counts.max())
    return purity / float(y_true.size)


def noise_fraction(labels: np.ndarray) -> float:
    labels = np.asarray(labels)
    if labels.size == 0:
        return 0.0
    return float(np.mean(labels == -1))
