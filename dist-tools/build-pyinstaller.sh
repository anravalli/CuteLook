#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build/pyinstaller"
OUTPUT_DIR="${PROJECT_ROOT}/dist/pyinstaller"
APP_NAME="CuteLook"
ENTRY_POINT="${PROJECT_ROOT}/CuteLook.py"
ONEFILE="${ONEFILE:-0}"

mkdir -p "${BUILD_DIR}" "${OUTPUT_DIR}"

RUNTIME_HOOK="${BUILD_DIR}/cutelook_runtime_hook.py"
cat > "${RUNTIME_HOOK}" <<'PYHOOK'
import os
import sys

if getattr(sys, "frozen", False):
    os.chdir(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))
PYHOOK

mode_args=(--onedir --contents-directory .)
if [[ "${ONEFILE}" == "1" ]]; then
    mode_args=(--onefile)
fi

python3 -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "${APP_NAME}" \
    --distpath "${OUTPUT_DIR}" \
    --workpath "${BUILD_DIR}" \
    --specpath "${BUILD_DIR}" \
    --runtime-hook "${RUNTIME_HOOK}" \
    --add-data "${PROJECT_ROOT}/icons:icons" \
    --add-data "${PROJECT_ROOT}/docs/demo.png:docs" \
    --hidden-import PyQt5.sip \
    --hidden-import PyQt5.QtSvg \
    --hidden-import pydantic_core._pydantic_core \
    --collect-submodules pydantic \
    "${mode_args[@]}" \
    "${ENTRY_POINT}"

echo "Build completed: ${OUTPUT_DIR}/${APP_NAME}"
