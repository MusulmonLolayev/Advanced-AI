"""Shared configuration for Assignment 4: DBSCAN."""

from __future__ import annotations

from pathlib import Path


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RESULTS_DIR = ASSIGNMENT_ROOT / "results"

RANDOM_SEED = 231
EPS_CHOICES = [0.25, 0.35, 0.45, 0.55]
MIN_PTS_CHOICES = [3, 4, 5, 6]

TOY_DATA_PATH = DATASETS_DIR / "toy_dbscan.npz"
IRIS_DATA_PATH = DATASETS_DIR / "iris_dbscan.npz"
SCALING_DATA_PATH = DATASETS_DIR / "scaling_study.npz"
OUTLIER_DATA_PATH = DATASETS_DIR / "outlier_study.npz"
