#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSIGNMENT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${ASSIGNMENT_ROOT}/environment-data.yml"
source "${SCRIPT_DIR}/common.sh"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda is required but was not found on PATH." >&2
  exit 1
fi

if ! conda env list | awk '{print $1}' | grep -Fx "${ENV_NAME}" >/dev/null 2>&1; then
  conda env create -y -n "${ENV_NAME}" -f "${ENV_FILE}"
fi

conda run -n "${ENV_NAME}" python "${SCRIPT_DIR}/prepare_all_data.py"
