"""Shared configuration for Assignment 3: k-means."""

from __future__ import annotations

from pathlib import Path


ASSIGNMENT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = ASSIGNMENT_ROOT / "datasets"
RESULTS_DIR = ASSIGNMENT_ROOT / "results"

RANDOM_SEED = 231
K_CHOICES = [2, 3, 4, 5, 6]
N_INIT_CHOICES = [1, 5, 10]
MAX_ITER = 100

IRIS_CLUSTERING_DATA_PATH = DATASETS_DIR / "iris_clustering.npz"
PCA_CLUSTERING_DATA_PATH = DATASETS_DIR / "pca_projection_clustering.npz"
INIT_STUDY_DATA_PATH = DATASETS_DIR / "initialization_study.npz"
IMAGE_QUANTIZATION_DATA_PATH = DATASETS_DIR / "image_quantization.npz"
