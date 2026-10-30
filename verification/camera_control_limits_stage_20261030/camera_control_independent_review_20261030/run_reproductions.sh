#!/bin/bash
set -eu
export PYTHONDONTWRITEBYTECODE=1
D="$PWD/camera_control_independent_review_20261030/mirror/smart_pen_next_20261028/hardware/camera_isolation_control_native_0628"
O="$PWD/camera_control_independent_review_20261030/raw"
for mode in normal optimized; do
 flag=''; [ "$mode" = normal ] || flag='-O'
 for script in verify physical_native reference_delta aon_neck_screen native_negative; do
  /usr/bin/python3 $flag "$D/$script.py" > "$O/${script}_${mode}.json" 2> "$O/${script}_${mode}.log"
  echo "$script $mode PASS"
 done
 IMU_NATIVE_OUTPUT="$D/fresh_replay_$mode/native" /usr/bin/python3 $flag "$D/materialize.py" > "$O/replay_$mode.log" 2>&1
 echo "replay $mode PASS"
done
