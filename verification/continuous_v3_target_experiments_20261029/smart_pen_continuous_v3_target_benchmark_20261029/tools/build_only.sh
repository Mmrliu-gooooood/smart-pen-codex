#!/usr/bin/env bash
set -euo pipefail
# Compilation only. Deliberately accepts no user-supplied idf.py action.
profile=${1:-disabled}
case "$profile" in disabled|enabled) ;; *) echo 'usage: build_only.sh [disabled|enabled]' >&2; exit 2;; esac
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
: "${IDF_PATH:?First source the verified ESP-IDF v5.4 export.sh}"
cd "$root"
defaults="$root/sdkconfig.defaults"
if [[ "$profile" == enabled ]]; then defaults="$defaults;$root/profiles/enabled.defaults"; fi
idf.py -B "build-$profile" -D "SDKCONFIG=$root/build-$profile.config" -D "SDKCONFIG_DEFAULTS=$defaults" build
