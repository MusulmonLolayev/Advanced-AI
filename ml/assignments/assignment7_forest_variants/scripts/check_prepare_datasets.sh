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
    "isolation_toy.npz": {"X", "y_outlier", "feature_names"},
    "extra_trees_iris.npz": {"X", "y", "feature_names", "target_names"},
    "quantile_regression.npz": {"X_train", "y_train", "X_test", "y_test", "feature_names"},
}

for filename, keys in required.items():
    path = datasets_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing prepared dataset: {path}")
    with np.load(path, allow_pickle=True) as bundle:
        missing = sorted(keys - set(bundle.files))
        if missing:
            raise KeyError(f"{path} is missing keys: {missing}")
        if "X" in bundle and "y" in bundle:
            X, y = bundle["X"], bundle["y"]
            if X.ndim != 2:
                raise ValueError(f"{path} must contain a 2D feature matrix.")
            if X.shape[0] != y.shape[0]:
                raise ValueError(f"{path} has inconsistent X and y lengths.")
        if "X_train" in bundle and "y_train" in bundle:
            X_train, y_train = bundle["X_train"], bundle["y_train"]
            X_test, y_test = bundle["X_test"], bundle["y_test"]
            if X_train.ndim != 2 or X_test.ndim != 2:
                raise ValueError(f"{path} must contain 2D feature matrices.")
            if X_train.shape[0] != y_train.shape[0] or X_test.shape[0] != y_test.shape[0]:
                raise ValueError(f"{path} has inconsistent X and y lengths.")

print("Dataset preparation check passed.")
for filename in required:
    print(f"Verified: {datasets_dir / filename}")
PY
