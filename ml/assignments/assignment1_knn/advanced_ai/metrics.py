"""Evaluation metrics used by the starter tasks."""

from __future__ import annotations

import numpy as np


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(y_true == y_pred))


def confusion_matrix_binary(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    return np.array([[tn, fp], [fn, tp]], dtype=int)


def precision_recall_f1(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    cm = confusion_matrix_binary(y_true, y_pred)
    tn, fp = cm[0]
    fn, tp = cm[1]

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 0.0 if precision + recall == 0.0 else 2.0 * precision * recall / (precision + recall)
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


def recall_at_k(relevance: np.ndarray, ranked_idx: np.ndarray, k: int) -> float:
    relevance = np.asarray(relevance)
    ranked_idx = np.asarray(ranked_idx)

    recalls = []
    for i in range(relevance.shape[0]):
        relevant = np.flatnonzero(relevance[i] > 0)
        if relevant.size == 0:
            continue
        hits = np.intersect1d(ranked_idx[i, :k], relevant).size
        recalls.append(hits / relevant.size)

    return float(np.mean(recalls)) if recalls else 0.0


def mean_reciprocal_rank(relevance: np.ndarray, ranked_idx: np.ndarray) -> float:
    relevance = np.asarray(relevance)
    ranked_idx = np.asarray(ranked_idx)

    rr = []
    for i in range(relevance.shape[0]):
        ordered_relevance = relevance[i, ranked_idx[i]]
        hits = np.flatnonzero(ordered_relevance > 0)
        rr.append(0.0 if hits.size == 0 else 1.0 / (hits[0] + 1))
    return float(np.mean(rr)) if rr else 0.0


def roc_auc_score_binary(y_true: np.ndarray, scores: np.ndarray) -> float:
    y_true = np.asarray(y_true).astype(int)
    scores = np.asarray(scores, dtype=np.float64)

    pos_scores = scores[y_true == 1]
    neg_scores = scores[y_true == 0]
    if pos_scores.size == 0 or neg_scores.size == 0:
        return 0.0

    comparisons = (pos_scores[:, None] > neg_scores[None, :]).sum()
    ties = (pos_scores[:, None] == neg_scores[None, :]).sum()
    auc = (comparisons + 0.5 * ties) / (pos_scores.size * neg_scores.size)
    return float(auc)


def pr_auc_score_binary(y_true: np.ndarray, scores: np.ndarray) -> float:
    y_true = np.asarray(y_true).astype(int)
    scores = np.asarray(scores, dtype=np.float64)

    order = np.argsort(-scores)
    y_sorted = y_true[order]

    tp = 0
    fp = 0
    fn = int(np.sum(y_true == 1))
    points: list[tuple[float, float]] = [(0.0, 1.0)]

    for label in y_sorted:
        if label == 1:
            tp += 1
            fn -= 1
        else:
            fp += 1
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        points.append((recall, precision))

    auc = 0.0
    for (r0, p0), (r1, p1) in zip(points[:-1], points[1:]):
        auc += (r1 - r0) * p1
    return float(auc)


def best_f1_threshold(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    y_true = np.asarray(y_true).astype(int)
    scores = np.asarray(scores, dtype=np.float64)
    thresholds = np.unique(scores)

    best_threshold = thresholds[0]
    best_f1 = -1.0
    for threshold in thresholds:
        y_pred = (scores >= threshold).astype(int)
        current_f1 = precision_recall_f1(y_true, y_pred)["f1"]
        if current_f1 > best_f1:
            best_f1 = current_f1
            best_threshold = float(threshold)
    return best_threshold, float(best_f1)
