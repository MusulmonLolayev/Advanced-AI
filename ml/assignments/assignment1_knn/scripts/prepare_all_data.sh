#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSIGNMENT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${ASSIGNMENT_ROOT}/environment-data.yml"
REQUIREMENTS_FILE="${ASSIGNMENT_ROOT}/requirements.txt"
ENV_NAME="ad-ai-ass1"
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

install_requirements() {
  local install_mode="$1"
  local temp_requirements
  temp_requirements="$(mktemp)"

  if [[ "${install_mode}" == "core" ]]; then
    awk '
      /^\s*#/ {
        if ($0 ~ /^# Retrieval dependencies$/) {
          exit
        }
        next
      }
      /^\s*$/ { next }
      { print }
    ' "${REQUIREMENTS_FILE}" > "${temp_requirements}"
  elif [[ "${install_mode}" == "retrieval" ]]; then
    awk '
      BEGIN { include = 0 }
      /^# Retrieval dependencies$/ { include = 1; next }
      /^\s*#/ { next }
      /^\s*$/ { next }
      include { print }
    ' "${REQUIREMENTS_FILE}" > "${temp_requirements}"
  else
    echo "Unsupported install mode: ${install_mode}" >&2
    rm -f "${temp_requirements}"
    return 1
  fi

  retry_cmd 2 conda run -n "${ENV_NAME}" python -m pip install -r "${temp_requirements}"
  rm -f "${temp_requirements}"
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
  install_requirements "core"
  if [[ "${CORE_ONLY}" -eq 0 && "${SKIP_RETRIEVAL}" -eq 0 ]]; then
    if ! conda run -n "${ENV_NAME}" python -c "import torch" >/dev/null 2>&1; then
      retry_cmd 2 conda run -n "${ENV_NAME}" python -m pip install --index-url https://download.pytorch.org/whl/cpu torch
    fi
    install_requirements "retrieval"
  fi
fi

conda run -n "${ENV_NAME}" python "${SCRIPT_DIR}/prepare_all_data.py" "${FORWARD_ARGS[@]}"
