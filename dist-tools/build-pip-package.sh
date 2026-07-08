#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${PROJECT_ROOT}/dist/pip"
CLEAN="${CLEAN:-1}"

if ! python3 -m build --version >/dev/null 2>&1; then
    echo "Missing Python build module. Install it with:"
    echo "  python3 -m pip install 'build>=1'"
    exit 1
fi

if [[ "${CLEAN}" == "1" ]]; then
    rm -rf "${OUTPUT_DIR}"
fi

mkdir -p "${OUTPUT_DIR}"

python3 -m build \
    --sdist \
    --wheel \
    --outdir "${OUTPUT_DIR}" \
    "${PROJECT_ROOT}"

echo "Python package artifacts created in: ${OUTPUT_DIR}"
