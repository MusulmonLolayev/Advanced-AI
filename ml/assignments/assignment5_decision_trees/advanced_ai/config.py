"""Shared configuration for Assignment 5: Decision Trees."""

from __future__ import annotations

from pathlib import Path


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RESULTS_DIR = ASSIGNMENT_ROOT / "results"

RANDOM_SEED = 231
DEPTH_CHOICES = [1, 2, 3, 4, 6]
MIN_LEAF_CHOICES = [1, 3, 5, 10]

TOY_DATA_PATH = DATASETS_DIR / "toy_tree.npz"
IRIS_DATA_PATH = DATASETS_DIR / "iris_tree.npz"
DEPTH_DATA_PATH = DATASETS_DIR / "depth_study.npz"
