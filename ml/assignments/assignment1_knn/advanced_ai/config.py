"""Shared assignment configuration.

Keeping paths and common hyperparameter grids in one place reduces hard-coded
values across the task scripts and keeps the starter consistent.
"""

from __future__ import annotations

from pathlib import Path


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RESULTS_DIR = ASSIGNMENT_ROOT / "results"

RANDOM_SEED = 231
K_CHOICES = [1, 3, 5, 9, 15, 25]
CORE_METRICS = ["l2", "l1"]
CORE_WEIGHTINGS = ["uniform", "distance"]

BANKNOTE_DATA_PATH = DATASETS_DIR / "banknote_authentication.csv"
CALIFORNIA_DATA_PATH = DATASETS_DIR / "california_housing.npz"
RETRIEVAL_DATA_PATH = DATASETS_DIR / "text_retrieval_embeddings.npz"
ANOMALY_DATA_PATH = DATASETS_DIR / "network_anomaly.npz"
