"""Shared assignment configuration for the PCA lab.

Keeping paths and common hyperparameter grids in one place reduces hard-coded
values across the task scripts and keeps the starter consistent.
"""

from __future__ import annotations

from pathlib import Path


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RESULTS_DIR = ASSIGNMENT_ROOT / "results"

RANDOM_SEED = 231
N_COMPONENT_CHOICES = [1, 2, 3, 5, 8, 10]
KNN_K_CHOICES = [1, 3, 5, 9, 15, 25]

PCA_CORE_DATA_PATH = DATASETS_DIR / "pca_core_toy.npz"
TEXT_EMBEDDINGS_DATA_PATH = DATASETS_DIR / "pca_text_embeddings.npz"
ANOMALY_DATA_PATH = DATASETS_DIR / "pca_anomaly.npz"
KNN_COMPARISON_DATA_PATH = DATASETS_DIR / "pca_knn_comparison.npz"
