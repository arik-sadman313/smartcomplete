#!/usr/bin/env bash
# SmartComplete — Universal Installer Launcher
# Launches the modern GUI installer by default if a display server is present,
# or seamlessly falls back to the CLI installer if run headless or with --cli.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

USE_CLI=false
for arg in "$@"; do
    if [ "$arg" = "--cli" ]; then
        USE_CLI=true
        break
    fi
done

# If user explicitly requested CLI or no graphical session is active, run CLI installer
if [ "$USE_CLI" = true ] || { [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; }; then
    exec bash "$SCRIPT_DIR/scripts/install.sh" "$@"
else
    exec bash "$SCRIPT_DIR/gui-installer.sh" "$@"
fi
