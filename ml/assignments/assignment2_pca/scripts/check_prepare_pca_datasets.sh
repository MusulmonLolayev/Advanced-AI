#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSIGNMENT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/common.sh"

for arg in "$@"; do
  if [[ "${arg}" == "--help" || "${arg}" == "-h" ]]; then
    bash "${SCRIPT_DIR}/prepare_all_data.sh" "${arg}"
    exit 0
  fi
  if [[ "${arg}" == "--core-only" || "${arg}" == "--skip-embeddings" ]]; then
    echo "check_prepare_pca_datasets.sh cannot be used with ${arg} because it verifies all non-embedding PCA datasets." >&2
    exit 1
  fi
done

bash "${SCRIPT_DIR}/prepare_all_data.sh" --skip-embeddings "$@"

ASSIGNMENT_ROOT="${ASSIGNMENT_ROOT}" conda run -n "${ENV_NAME}" python - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

import numpy as np


assignment_root = Path(os.environ["ASSIGNMENT_ROOT"])
datasets_dir = assignment_root / "datasets"

core_path = datasets_dir / "pca_core_toy.npz"
knn_path = datasets_dir / "pca_knn_comparison.npz"
anomaly_path = datasets_dir / "pca_anomaly.npz"

for path in [core_path, knn_path, anomaly_path]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prepared dataset: {path}")

with np.load(core_path, allow_pickle=True) as core:
    if "X" not in core:
        raise KeyError("PCA core bundle must contain X.")

with np.load(knn_path, allow_pickle=True) as knn:
    required = {"X_train", "y_train", "X_val", "y_val", "X_test", "y_test"}
    missing = sorted(required - set(knn.files))
    if missing:
        raise KeyError(f"PCA+KNN bundle missing keys: {missing}")

with np.load(anomaly_path, allow_pickle=True) as anomaly:
    required = {"X_train", "X_val", "y_val", "X_test", "y_test"}
    missing = sorted(required - set(anomaly.files))
    if missing:
        raise KeyError(f"Anomaly bundle missing keys: {missing}")

print("Dataset preparation check passed.")
print(f"Verified: {core_path}")
print(f"Verified: {knn_path}")
print(f"Verified: {anomaly_path}")
PY
