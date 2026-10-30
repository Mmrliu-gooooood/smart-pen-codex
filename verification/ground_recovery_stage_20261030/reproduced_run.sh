#!/bin/sh
# Usage: sh reproduced_run.sh /absolute/newly-reconstructed-workspace
# Run reconstruct.py first, with repository root containing prior-stage aliases.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
W=$(CDPATH= cd -- "$1" && pwd)
I="$W/ground_recovery_independent_review_20261030"
export PYTHONDONTWRITEBYTECODE=1
export XDG_CONFIG_HOME="$W/.xdg-config"
cd "$W"
# Does fresh bound CLI then real 20 native negatives/replay/inverse-patch in both modes.
bash "$I/run.sh"
for name in independent_delta independent_inventory independent_raw_probe finalize_review; do
 cp "$HERE/reproduced_${name}_isolated.py" "$I/${name}_isolated.py"
done
for flag in '' '-O'; do
 /usr/bin/python3 $flag "$I/independent_delta_isolated.py"
 /usr/bin/python3 $flag "$I/independent_inventory_isolated.py"
 /usr/bin/python3 $flag "$I/independent_raw_probe_isolated.py"
done
/usr/bin/python3 "$I/finalize_review_isolated.py"
# Success means bounded static experimental checks only; still NOFAB / NOPOWER.
