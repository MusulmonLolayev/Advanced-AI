#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for arg in "$@"; do
  if [[ "${arg}" == "--help" || "${arg}" == "-h" ]]; then
    bash "${SCRIPT_DIR}/prepare_all_data.sh" "${arg}"
    exit 0
  fi
  if [[ "${arg}" == "--core-only" || "${arg}" == "--skip-embeddings" || "${arg}" == "--skip-anomaly" ]]; then
    echo "check_prepare_all_data.sh cannot be used with ${arg} because it verifies every prepared artifact." >&2
    exit 1
  fi
done

bash "${SCRIPT_DIR}/check_prepare_pca_datasets.sh" "$@"
bash "${SCRIPT_DIR}/check_prepare_pca_embeddings.sh" "$@"
