#!/usr/bin/env bash
# SmartComplete — Universal Uninstaller Launcher
# Launches the GUI uninstaller tab if display is present, or runs CLI uninstaller if --cli or headless.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

USE_CLI=false
for arg in "$@"; do
    if [ "$arg" = "--cli" ]; then
        USE_CLI=true
        break
    fi
done

if [ "$USE_CLI" = true ] || { [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; }; then
    exec bash "$SCRIPT_DIR/scripts/uninstall.sh" "$@"
else
    exec bash "$SCRIPT_DIR/gui-installer.sh" --tab uninstall "$@"
fi
