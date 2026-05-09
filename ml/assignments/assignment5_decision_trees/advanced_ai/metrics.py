"""Simple classification metrics for Assignment 5."""

from __future__ import annotations

import numpy as np


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape.")
    if y_true.size == 0:
        return 0.0
    return float(np.mean(y_true == y_pred))


def class_counts(y: np.ndarray) -> dict[int, int]:
    y = np.asarray(y)
    unique, counts = np.unique(y, return_counts=True)
    return {int(label): int(count) for label, count in zip(unique, counts)}


def confusion_table(y_true: np.ndarray, y_pred: np.ndarray) -> dict[int, dict[int, int]]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    labels = np.unique(np.concatenate([y_true, y_pred]))
    table: dict[int, dict[int, int]] = {}
    for true_label in labels:
        row: dict[int, int] = {}
        for pred_label in labels:
            row[int(pred_label)] = int(np.sum((y_true == true_label) & (y_pred == pred_label)))
        table[int(true_label)] = row
    return table
