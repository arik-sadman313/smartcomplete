#!/usr/bin/env bash
# Run explicitly with bash; no actions occur just by opening this file.
set -Eeuo pipefail
BACKUP='not-created'
trap 'echo "STOPPED at line $LINENO. Backup: $BACKUP. No automatic rollback was performed." >&2' ERR
BUNDLE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT=${1:-/home/ekrem/smartcomplete}
MODE=${2:-light}
[[ "$MODE" == light || "$MODE" == dark ]]
[[ "$EUID" -ne 0 ]] # Run as your desktop user, never sudo bash this script.
cd -- "$PROJECT"
[[ "$(git rev-parse --show-toplevel)" == "$(pwd -P)" ]]
for cmd in git cmake ctest python3 sha256sum sudo fcitx5 fcitx5-remote; do
    command -v "$cmd" >/dev/null
done
[[ -n "${WAYLAND_DISPLAY:-}${DISPLAY:-}" ]]
OLD_PID=$(pgrep -u "$(id -u)" -x fcitx5)
[[ "$OLD_PID" =~ ^[0-9]+$ ]]
fcitx5-remote --check >/dev/null
MODULE=/usr/lib/fcitx5/linuxcomplete.so
[[ -f "$MODULE" && ! -L "$MODULE" ]]
CONFIG_ROOT=${XDG_CONFIG_HOME:-$HOME/.config}
DATA_ROOT=${XDG_DATA_HOME:-$HOME/.local/share}
STATE_ROOT=${XDG_STATE_HOME:-$HOME/.local/state}
CFG="$CONFIG_ROOT/fcitx5/conf/classicui.conf"
[[ ! -L "$CFG" ]]
for mode in light dark; do
    [[ ! -e "$DATA_ROOT/fcitx5/themes/smartcomplete-modern-$mode" ]]
done
# Refuse unexpected source changes, but allow the known, uncommitted Ctrl/Alt fix.
sha256sum --check "$BUNDLE/base.sha256"
git apply --check "$BUNDLE/compact-ui.patch"
git apply --check "$BUNDLE/tray-icon.patch"
for icon in "$BUNDLE"/icons/hicolor/*/apps/linuxcomplete.*; do
    relative=${icon#"$BUNDLE/icons/"}
    [[ ! -e "$DATA_ROOT/icons/$relative" ]]
done
python3 "$BUNDLE/validate_themes.py"
python3 "$BUNDLE/validate_icons.py"

mkdir -p "$STATE_ROOT/smartcomplete"
BACKUP=$(mktemp -d "$STATE_ROOT/smartcomplete/modern-ui-backup.XXXXXX")
cp -a CMakeLists.txt "$BACKUP/CMakeLists.txt"
cp -a src/engine/engine.cpp "$BACKUP/engine.cpp"
cp -a tests/engine_shortcuts_regression.cpp "$BACKUP/engine_shortcuts_regression.cpp"
cp -a "$MODULE" "$BACKUP/linuxcomplete.so"
printf '%s\n' "$CFG" > "$BACKUP/config-path.txt"
printf '%s\n' "$DATA_ROOT/fcitx5/themes" > "$BACKUP/themes-path.txt"
printf 'Backup: %s\n' "$BACKUP"
git apply "$BUNDLE/compact-ui.patch"
git apply "$BUNDLE/tray-icon.patch"
git diff --check
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build --parallel 4
ctest --test-dir build -R '^linuxcomplete_engine_shortcuts_regression$' --no-tests=error --output-on-failure
ctest --test-dir build --no-tests=error --output-on-failure
sudo -v

# Stop gracefully before editing UI config: exit may persist its old settings.
fcitx5-remote -e
STOPPED=0
for ((i=0; i<30; i++)); do
    if ! kill -0 "$OLD_PID" 2>/dev/null; then STOPPED=1; break; fi
    sleep 0.5
done
[[ "$STOPPED" == 1 ]]
if [[ -f "$CFG" ]]; then cp -a "$CFG" "$BACKUP/classicui.conf";
else touch "$BACKUP/classicui-was-absent"; fi
# This is an existing installation: deploy only the changed addon, not global
# environment/profile/default config files from the one-click installer.
STAGED="/usr/lib/fcitx5/.linuxcomplete-modern-$$.so"
sudo install -m 755 build/linuxcomplete.so "$STAGED"
sudo mv -f -- "$STAGED" "$MODULE"
cmp build/linuxcomplete.so "$MODULE"
mkdir -p "$DATA_ROOT/fcitx5/themes" "$(dirname -- "$CFG")"
for mode in light dark; do
    cp -a "$BUNDLE/themes/smartcomplete-modern-$mode" "$DATA_ROOT/fcitx5/themes/"
done
for icon in "$BUNDLE"/icons/hicolor/*/apps/linuxcomplete.*; do
    relative=${icon#"$BUNDLE/icons/"}
    install -D -m 644 "$icon" "$DATA_ROOT/icons/$relative"
    printf '%s\n' "$DATA_ROOT/icons/$relative" >> "$BACKUP/new-icons.txt"
done
python3 - "$CFG" "$MODE" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
updates = {
    'Theme': 'smartcomplete-modern-' + sys.argv[2],
    'DarkTheme': 'smartcomplete-modern-dark',
    'UseDarkTheme': 'False',
    'UseAccentColor': 'False',
    'Font': 'Sans 12',
    'PreferTextIcon': 'False',
    'Vertical Candidate List': 'False',
}
lines = path.read_text().splitlines() if path.exists() else []
result, root = [], True
for line in lines:
    if line.strip().startswith('['): root = False
    key = line.split('=', 1)[0].strip()
    if root and '=' in line and key in updates: continue
    result.append(line)
prefix = [f'{key}={value}' for key, value in updates.items()]
path.write_text('\n'.join(prefix + result) + '\n')
PY
fcitx5 -d
READY=0
for ((i=0; i<30; i++)); do
    NEW_PID=$(pgrep -u "$(id -u)" -x fcitx5 || true)
    if [[ "$NEW_PID" =~ ^[0-9]+$ ]] && [[ "$NEW_PID" != "$OLD_PID" ]] &&
       fcitx5-remote --check >/dev/null 2>&1; then READY=1; break; fi
    sleep 0.5
done
[[ "$READY" == 1 ]]
fcitx5-remote -s linuxcomplete
fcitx5-remote -o
[[ "$(fcitx5-remote -n)" == linuxcomplete ]]
[[ "$(fcitx5-remote)" == 2 ]]
grep -E '/usr/lib/fcitx5/linuxcomplete\.so$' "/proc/$NEW_PID/maps" >/dev/null
printf 'Installed and loaded. Theme: %s. Backup: %s\n' "$MODE" "$BACKUP"
echo 'Live visual check still required: open an English text field and type hel.'
