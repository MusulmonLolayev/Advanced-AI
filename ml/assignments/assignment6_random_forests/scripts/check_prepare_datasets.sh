#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSIGNMENT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/common.sh"

bash "${SCRIPT_DIR}/prepare_all_data.sh"

ASSIGNMENT_ROOT="${ASSIGNMENT_ROOT}" conda run -n "${ENV_NAME}" python - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

import numpy as np


assignment_root = Path(os.environ["ASSIGNMENT_ROOT"])
datasets_dir = assignment_root / "datasets"

required = {
    "toy_forest.npz": {"X", "y", "feature_names", "target_names"},
    "iris_forest.npz": {"X", "y", "feature_names", "target_names"},
    "forest_study.npz": {"X", "y", "feature_names", "target_names"},
}

for filename, keys in required.items():
    path = datasets_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing prepared dataset: {path}")
    with np.load(path, allow_pickle=True) as bundle:
        missing = sorted(keys - set(bundle.files))
        if missing:
            raise KeyError(f"{path} is missing keys: {missing}")
        X, y = bundle["X"], bundle["y"]
        if X.ndim != 2:
            raise ValueError(f"{path} must contain a 2D feature matrix.")
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"{path} has inconsistent X and y lengths.")

print("Dataset preparation check passed.")
for filename in required:
    print(f"Verified: {datasets_dir / filename}")
PY
