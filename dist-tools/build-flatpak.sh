#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build/flatpak"
OUTPUT_DIR="${PROJECT_ROOT}/dist/flatpak"
APP_ID="${APP_ID:-io.github.cutelook.CuteLook}"
APP_NAME="CuteLook"
RUNTIME="${FLATPAK_RUNTIME:-org.freedesktop.Platform}"
SDK="${FLATPAK_SDK:-org.freedesktop.Sdk}"
RUNTIME_VERSION="${FLATPAK_RUNTIME_VERSION:-24.08}"
INSTALL="${INSTALL:-0}"

if ! command -v flatpak-builder >/dev/null 2>&1; then
    echo "Missing flatpak-builder. Install it with your system package manager."
    exit 1
fi

mkdir -p "${BUILD_DIR}/assets" "${OUTPUT_DIR}"

DESKTOP_FILE="${BUILD_DIR}/assets/${APP_ID}.desktop"
METAINFO_FILE="${BUILD_DIR}/assets/${APP_ID}.metainfo.xml"
LAUNCHER_FILE="${BUILD_DIR}/assets/cutelook"
MANIFEST_FILE="${BUILD_DIR}/${APP_ID}.json"
REPO_DIR="${OUTPUT_DIR}/repo"
APP_DIR="${BUILD_DIR}/app"

cat > "${DESKTOP_FILE}" <<EOF_DESKTOP
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Comment=A reference board application for artists
Exec=cutelook
Icon=${APP_ID}
Categories=Graphics;Qt;
Terminal=false
EOF_DESKTOP

cat > "${METAINFO_FILE}" <<EOF_METAINFO
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${APP_ID}</id>
  <name>${APP_NAME}</name>
  <summary>A reference board application for artists</summary>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>GPL-3.0-or-later</project_license>
  <description>
    <p>CuteLook helps artists arrange, zoom, crop, and manage reference images on boards.</p>
  </description>
  <launchable type="desktop-id">${APP_ID}.desktop</launchable>
</component>
EOF_METAINFO

cat > "${LAUNCHER_FILE}" <<'EOF_LAUNCHER'
#!/usr/bin/env bash
cd /app/share/cutelook
exec python3 CuteLook.py "$@"
EOF_LAUNCHER
chmod +x "${LAUNCHER_FILE}"

cat > "${MANIFEST_FILE}" <<EOF_MANIFEST
{
  "app-id": "${APP_ID}",
  "runtime": "${RUNTIME}",
  "runtime-version": "${RUNTIME_VERSION}",
  "sdk": "${SDK}",
  "command": "cutelook",
  "finish-args": [
    "--share=ipc",
    "--socket=x11",
    "--socket=fallback-x11",
    "--socket=wayland",
    "--device=dri",
    "--talk-name=org.freedesktop.portal.Desktop",
    "--env=QT_QPA_PLATFORMTHEME=xdgdesktopportal"
  ],
  "modules": [
    {
      "name": "cutelook",
      "buildsystem": "simple",
      "build-options": {
        "build-args": [
          "--share=network"
        ]
      },
      "build-commands": [
        "python3 -m pip install --prefix=/app --no-cache-dir --no-build-isolation .",
        "mkdir -p /app/share/cutelook",
        "cp -a *.py CustomWidgets icons docs /app/share/cutelook/",
        "install -Dm755 build/flatpak/assets/cutelook /app/bin/cutelook",
        "install -Dm644 build/flatpak/assets/${APP_ID}.desktop /app/share/applications/${APP_ID}.desktop",
        "install -Dm644 build/flatpak/assets/${APP_ID}.metainfo.xml /app/share/metainfo/${APP_ID}.metainfo.xml",
        "install -Dm644 icons/add-image.svg /app/share/icons/hicolor/scalable/apps/${APP_ID}.svg"
      ],
      "sources": [
        {
          "type": "dir",
          "path": "${PROJECT_ROOT}"
        }
      ]
    }
  ]
}
EOF_MANIFEST

flatpak-builder \
    --force-clean \
    --install-deps-from=flathub \
    --repo="${REPO_DIR}" \
    "${APP_DIR}" \
    "${MANIFEST_FILE}"

flatpak build-bundle \
    "${REPO_DIR}" \
    "${OUTPUT_DIR}/${APP_ID}.flatpak" \
    "${APP_ID}"

if [[ "${INSTALL}" == "1" ]]; then
    flatpak install --user -y "${OUTPUT_DIR}/${APP_ID}.flatpak"
fi

echo "Flatpak bundle created: ${OUTPUT_DIR}/${APP_ID}.flatpak"
