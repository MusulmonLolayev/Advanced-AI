#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSIGNMENT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${ASSIGNMENT_ROOT}/environment-data.yml"
source "${SCRIPT_DIR}/common.sh"
SKIP_INSTALL=0
CORE_ONLY=0
SKIP_RETRIEVAL=0
SHOW_HELP=0
FORWARD_ARGS=()

retry_cmd() {
  local attempts="$1"
  shift
  local try=1
  while true; do
    if "$@"; then
      return 0
    fi
    if [[ "${try}" -ge "${attempts}" ]]; then
      return 1
    fi
    try=$((try + 1))
    sleep 2
  done
}

install_core_requirements() {
  retry_cmd 2 conda run -n "${ENV_NAME}" python -m pip install "${CORE_REQUIREMENTS[@]}"
}

install_retrieval_requirements() {
  retry_cmd 2 conda run -n "${ENV_NAME}" python -m pip install "${RETRIEVAL_REQUIREMENTS[@]}"
}

for arg in "$@"; do
  if [[ "${arg}" == "--skip-install" ]]; then
    SKIP_INSTALL=1
  elif [[ "${arg}" == "--help" || "${arg}" == "-h" ]]; then
    SHOW_HELP=1
    FORWARD_ARGS+=("${arg}")
  else
    if [[ "${arg}" == "--core-only" ]]; then
      CORE_ONLY=1
    fi
    if [[ "${arg}" == "--skip-retrieval" ]]; then
      SKIP_RETRIEVAL=1
    fi
    FORWARD_ARGS+=("${arg}")
  fi
done

if ! command -v conda >/dev/null 2>&1; then
  echo "conda is required but was not found on PATH." >&2
  exit 1
fi

if [[ "${SHOW_HELP}" -eq 1 ]]; then
  python "${SCRIPT_DIR}/prepare_all_data.py" "${FORWARD_ARGS[@]}"
  exit 0
fi

if ! conda env list | awk '{print $1}' | grep -Fx "${ENV_NAME}" >/dev/null 2>&1; then
  retry_cmd 2 conda env create -y -n "${ENV_NAME}" -f "${ENV_FILE}"
fi

if [[ "${SKIP_INSTALL}" -eq 0 ]]; then
  install_core_requirements
  if [[ "${CORE_ONLY}" -eq 0 && "${SKIP_RETRIEVAL}" -eq 0 ]]; then
    if ! conda run -n "${ENV_NAME}" python -c "import torch" >/dev/null 2>&1; then
      retry_cmd 2 conda run -n "${ENV_NAME}" python -m pip install --index-url https://download.pytorch.org/whl/cpu torch
    fi
    install_retrieval_requirements
  fi
fi

conda run -n "${ENV_NAME}" python "${SCRIPT_DIR}/prepare_all_data.py" "${FORWARD_ARGS[@]}"
