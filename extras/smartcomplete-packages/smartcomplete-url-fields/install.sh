#!/usr/bin/env bash
set -Eeuo pipefail
BACKUP=not-created
trap 'echo "STOPPED at line $LINENO; backup: $BACKUP. No automatic rollback." >&2' ERR
BUNDLE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
[[ "$EUID" -ne 0 ]]
cd /home/ekrem/smartcomplete
[[ "$(git rev-parse --show-toplevel)" == "$(pwd -P)" ]]
[[ -n "${WAYLAND_DISPLAY:-}${DISPLAY:-}" ]]
if OLD_PID=$(pgrep -u "$(id -u)" -x fcitx5); then
    if [[ ! "$OLD_PID" =~ ^[0-9]+$ ]]; then
        echo 'Multiple Fcitx5 processes found; stopping to avoid changing the wrong session.' >&2
        exit 1
    fi
else
    status=$?
    if [[ "$status" -ne 1 ]]; then
        echo "Fcitx5 process lookup failed (pgrep exit $status)." >&2
        exit "$status"
    fi
    OLD_PID=''
    echo 'Fcitx5 is stopped; it will be started after successful installation.'
fi
sha256sum --check "$BUNDLE/base.sha256"
git apply --check "$BUNDLE/url-fields.patch"
STATE=${XDG_STATE_HOME:-$HOME/.local/state}
mkdir -p "$STATE/smartcomplete"
BACKUP=$(mktemp -d "$STATE/smartcomplete/url-fields-backup.XXXXXX")
cp src/engine/engine.cpp "$BACKUP/engine.cpp"
cp src/engine/engine.h "$BACKUP/engine.h"
cp tests/engine_shortcuts_regression.cpp "$BACKUP/engine_shortcuts_regression.cpp"
cp /usr/lib/fcitx5/linuxcomplete.so "$BACKUP/linuxcomplete.so"
printf 'Backup: %s\n' "$BACKUP"
git apply "$BUNDLE/url-fields.patch"
git diff --check
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build --parallel 4
ctest --test-dir build -R '^linuxcomplete_engine_shortcuts_regression$' --no-tests=error --output-on-failure
ctest --test-dir build --no-tests=error --output-on-failure
STAGED="/usr/lib/fcitx5/.linuxcomplete-url-$$.so"
sudo test ! -e "$STAGED"
sudo install -m 755 build/linuxcomplete.so "$STAGED"
sudo mv -f -- "$STAGED" /usr/lib/fcitx5/linuxcomplete.so
cmp build/linuxcomplete.so /usr/lib/fcitx5/linuxcomplete.so
fcitx5 -rd
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
echo 'URL field bypass installed and addon loaded. Normal text fields remain enabled.'
