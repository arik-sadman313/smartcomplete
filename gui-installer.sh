#!/usr/bin/env bash
# SmartComplete — GUI Installer & Control Center Launcher
# Automatically verifies Python 3 & PyQt6 and launches the modern graphical installer.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required to run the SmartComplete GUI installer."
    exit 1
fi

# 2. Check PyQt6
if ! python3 -c "import PyQt6" &>/dev/null; then
    echo "PyQt6 is required for the graphical installer. Attempting automatic installation..."
    if command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm python-pyqt6
    elif command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y python3-pyqt6
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-pyqt6
    else
        pip3 install PyQt6 || {
            echo "Failed to install PyQt6 automatically. Please install python3-pyqt6 or PyQt6 via pip."
            exit 1
        }
    fi
fi

# 3. Launch GUI Installer
exec python3 "$SCRIPT_DIR/installer_gui.py" "$@"
