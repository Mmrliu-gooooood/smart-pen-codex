set -eu
export PYTHONDONTWRITEBYTECODE=1
D="$PWD/ground_recovery_independent_review_20261030/mirror/smart_pen_next_20261028/hardware/ground_recovery_native_0818"
O="$PWD/ground_recovery_independent_review_20261030/raw"
/usr/bin/python3 "$D/run_checks.py" > "$O/cli.log" 2>&1
for mode in normal optimized; do
 flag=''; [ "$mode" = normal ] || flag='-O'
 for script in verify physical_native probe_access negative_ground replay_rollback; do
 /usr/bin/python3 $flag "$D/$script.py" > "$O/${script}_${mode}.json" 2> "$O/${script}_${mode}.log"
 echo "$script $mode PASS"
 done
done
cp "$O/negative_ground_normal.json" "$D/negative_ground.json"
cp "$O/negative_ground_optimized.json" "$D/negative_ground_optimized.json"
/usr/bin/python3 "$D/negative_ground_compare.py" > "$O/exact_negative_comparison.json" 2> "$O/exact_negative_comparison.log"
/usr/bin/python3 "$D/export_bom_status.py" > "$O/bom_export.log" 2>&1
