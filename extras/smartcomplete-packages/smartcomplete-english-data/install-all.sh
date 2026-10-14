#!/usr/bin/env bash
# Explicit user-run deployment: modern UI + tray icon, then English data.
set -Eeuo pipefail
BACKUP=not-created
trap 'echo "STOPPED at line $LINENO. English backup: $BACKUP. Check the earlier UI backup message too." >&2' ERR
BUNDLE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT=${1:-/home/ekrem/smartcomplete}
MODE=${2:-light}
[[ "$EUID" -ne 0 ]]
[[ "$MODE" == light || "$MODE" == dark ]]
cd -- "$PROJECT"
[[ "$(git rev-parse --show-toplevel)" == "$(pwd -P)" ]]
# This installer targets the existing /usr installation, not a user dictionary override.
if [[ -d "$HOME/.local/share/linuxcomplete/dict" ]]; then
    echo 'User dictionary override exists. Stop and identify the active data path first.' >&2
    exit 1
fi
FILES=(dict/en_US.txt frequency/en_freq.txt ngram/en_bigrams.txt ngram/en_phrases.txt
       rules/en_grammar_pair_rules.txt rules/en_grammar_triple_rules.txt)
for file in "${FILES[@]}"; do
    [[ -f "/usr/share/linuxcomplete/$file" && ! -L "/usr/share/linuxcomplete/$file" ]]
done
sha256sum --check "$BUNDLE/base.sha256"
git apply --check "$BUNDLE/english-data.patch"
# The UI installer checks its original source hashes, so it must run first.
bash "$BUNDLE/../smartcomplete-modern-ui/install.sh" "$PROJECT" "$MODE"

STATE=${XDG_STATE_HOME:-$HOME/.local/state}
mkdir -p "$STATE/smartcomplete"
BACKUP=$(mktemp -d "$STATE/smartcomplete/english-data-backup.XXXXXX")
cp CMakeLists.txt "$BACKUP/CMakeLists.txt"
for file in "${FILES[@]}"; do
    mkdir -p "$BACKUP/source/$(dirname -- "$file")" "$BACKUP/installed/$(dirname -- "$file")"
    cp "data/$file" "$BACKUP/source/$file"
    cp "/usr/share/linuxcomplete/$file" "$BACKUP/installed/$file"
done
printf 'English data backup: %s\n' "$BACKUP"
git apply --check "$BUNDLE/english-data.patch"
git apply "$BUNDLE/english-data.patch"
git diff --check
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build --parallel 4
ctest --test-dir build -R '^linuxcomplete_english_data_regression$' --no-tests=error --output-on-failure
ctest --test-dir build --no-tests=error --output-on-failure
sudo -v
OLD_PID=$(pgrep -u "$(id -u)" -x fcitx5)
[[ "$OLD_PID" =~ ^[0-9]+$ ]]
fcitx5-remote -e
STOPPED=0
for ((i=0; i<30; i++)); do
    if ! kill -0 "$OLD_PID" 2>/dev/null; then STOPPED=1; break; fi
    sleep 0.5
done
[[ "$STOPPED" == 1 ]]
# Update only the six data files; do not overwrite profiles, themes or learned words.
for file in "${FILES[@]}"; do
    target="/usr/share/linuxcomplete/$file"
    sudo install -m 644 "data/$file" "$target.new.$$"
    sudo mv -f -- "$target.new.$$" "$target"
    cmp "data/$file" "$target"
done
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
echo "Installed UI, tray icon and English data. English backup: $BACKUP"
echo 'Live suggestion examples to check in a graphical text field: resch, onboarding, can we .'
