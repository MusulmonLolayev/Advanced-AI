#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSIGNMENT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_NAME="advanced-ai-assignment1-knn-data"

for arg in "$@"; do
  if [[ "${arg}" == "--help" || "${arg}" == "-h" ]]; then
    bash "${SCRIPT_DIR}/prepare_all_data.sh" "${arg}"
    exit 0
  fi
  if [[ "${arg}" == "--core-only" || "${arg}" == "--skip-anomaly" ]]; then
    echo "check_prepare_datasets.sh cannot be used with ${arg} because it verifies the anomaly dataset too." >&2
    exit 1
  fi
done

bash "${SCRIPT_DIR}/prepare_all_data.sh" --skip-retrieval "$@"

ASSIGNMENT_ROOT="${ASSIGNMENT_ROOT}" conda run -n "${ENV_NAME}" python - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

import numpy as np


assignment_root = Path(os.environ["ASSIGNMENT_ROOT"])
datasets_dir = assignment_root / "datasets"

banknote_path = datasets_dir / "banknote_authentication.csv"
california_path = datasets_dir / "california_housing.npz"
anomaly_path = datasets_dir / "network_anomaly.npz"

if not banknote_path.exists():
    raise FileNotFoundError(f"Missing prepared dataset: {banknote_path}")
banknote = np.loadtxt(banknote_path, delimiter=",")
if banknote.ndim != 2 or banknote.shape[1] < 2:
    raise ValueError("Banknote dataset must be a 2D numeric table with features and a label column.")

if not california_path.exists():
    raise FileNotFoundError(f"Missing prepared dataset: {california_path}")
with np.load(california_path, allow_pickle=True) as california:
    required = {"X", "y"}
    missing = sorted(required - set(california.files))
    if missing:
        raise KeyError(f"California bundle missing keys: {missing}")

if not anomaly_path.exists():
    raise FileNotFoundError(f"Missing prepared dataset: {anomaly_path}")
with np.load(anomaly_path, allow_pickle=True) as anomaly:
    required = {"X_train", "X_val", "y_val", "X_test", "y_test"}
    missing = sorted(required - set(anomaly.files))
    if missing:
        raise KeyError(f"Anomaly bundle missing keys: {missing}")

print("Dataset preparation check passed.")
print(f"Verified: {banknote_path}")
print(f"Verified: {california_path}")
print(f"Verified: {anomaly_path}")
PY
