set -eu
export PYTHONDONTWRITEBYTECODE=1
D="$PWD/camera_schmitt_independent_review_20261030/mirror/smart_pen_next_20261028/hardware/camera_schmitt_native_0745"
O="$PWD/camera_schmitt_independent_review_20261030/raw"
/usr/bin/python3 "$D/run_checks.py" > "$O/cli.log" 2>&1
for mode in normal optimized; do
 flag=''; [ "$mode" = normal ] || flag='-O'
 for script in verify physical_native native_negative; do
 /usr/bin/python3 $flag "$D/$script.py" > "$O/${script}_${mode}.json" 2> "$O/${script}_${mode}.log"
 echo "$script $mode PASS"
 done
 /usr/bin/python3 $flag "$D/replay_rollback.py" > "$O/replay_rollback_${mode}.json" 2> "$O/replay_rollback_${mode}.log"
 echo "replay rollback $mode PASS"
done
