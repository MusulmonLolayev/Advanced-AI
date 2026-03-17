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
  if [[ "${arg}" == "--core-only" || "${arg}" == "--skip-retrieval" ]]; then
    echo "check_prepare_embeddings.sh cannot be used with ${arg} because it verifies retrieval embeddings." >&2
    exit 1
  fi
done

bash "${SCRIPT_DIR}/prepare_all_data.sh" --skip-anomaly "$@"

ASSIGNMENT_ROOT="${ASSIGNMENT_ROOT}" conda run -n "${ENV_NAME}" python - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

import numpy as np


assignment_root = Path(os.environ["ASSIGNMENT_ROOT"])
retrieval_path = assignment_root / "datasets" / "text_retrieval_embeddings.npz"

if not retrieval_path.exists():
    raise FileNotFoundError(f"Missing prepared embeddings: {retrieval_path}")

with np.load(retrieval_path, allow_pickle=True) as retrieval:
    required = {
        "query_embeddings",
        "doc_embeddings",
        "relevance",
        "query_lengths",
        "doc_lengths",
    }
    missing = sorted(required - set(retrieval.files))
    if missing:
        raise KeyError(f"Retrieval bundle missing keys: {missing}")

    query_embeddings = retrieval["query_embeddings"]
    doc_embeddings = retrieval["doc_embeddings"]
    relevance = retrieval["relevance"]
    if query_embeddings.ndim != 2 or doc_embeddings.ndim != 2:
        raise ValueError("Embedding arrays must be rank-2 matrices.")
    if relevance.shape != (query_embeddings.shape[0], doc_embeddings.shape[0]):
        raise ValueError("Relevance matrix shape does not match the embedding counts.")

print("Embedding preparation check passed.")
print(f"Verified: {retrieval_path}")
PY
