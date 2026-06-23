"""Shared configuration for Assignment 7: Forest Variants."""

from __future__ import annotations

from pathlib import Path


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RESULTS_DIR = ASSIGNMENT_ROOT / "results"

RANDOM_SEED = 231

B_CHOICES = [1, 5, 10, 20, 50, 100]
PSI_CHOICES = [64, 128, 256, 512]
N_REPEATS = 5

TAU_LOW = 0.1
TAU_MEDIAN = 0.5
TAU_HIGH = 0.9

ISOLATION_DATA_PATH = DATASETS_DIR / "isolation_toy.npz"
EXTRA_TREES_DATA_PATH = DATASETS_DIR / "extra_trees_iris.npz"
QUANTILE_DATA_PATH = DATASETS_DIR / "quantile_regression.npz"
