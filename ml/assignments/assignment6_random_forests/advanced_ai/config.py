"""Shared configuration for Assignment 6: Random Forests."""

from __future__ import annotations

from pathlib import Path


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RESULTS_DIR = ASSIGNMENT_ROOT / "results"

RANDOM_SEED = 231
B_CHOICES = [1, 5, 10, 20, 50, 100, 200]

TOY_DATA_PATH = DATASETS_DIR / "toy_forest.npz"
IRIS_DATA_PATH = DATASETS_DIR / "iris_forest.npz"
FOREST_STUDY_DATA_PATH = DATASETS_DIR / "forest_study.npz"
