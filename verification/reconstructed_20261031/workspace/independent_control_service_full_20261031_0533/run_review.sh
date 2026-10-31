set -e
export PYTHONDONTWRITEBYTECODE=1 XDG_CONFIG_HOME=/tmp/reviewservice/config XDG_CACHE_HOME=/tmp/reviewservice/cache XDG_DATA_HOME=/tmp/reviewservice/data
for mode in normal optimized; do
 flag=''; [ "$mode" = normal ] || flag=-O
 for s in verify_final check_candidate native_contract_final source_roles raw_contract anchor_regression_final boundary_flag_regression window_policy_regression; do /usr/bin/python3 $flag $s.py > independent_${s}_${mode}.log 2>&1; done
 for i in 0 1 2 3; do /usr/bin/python3 $flag negatives_final.py $i >independent_negative_${mode}_${i}.log 2>&1; done
done
/usr/bin/python3 run_saved_cuts.py >independent_savedcuts.log 2>&1
kicad-cli pcb drc --all-track-errors --schematic-parity --format json -o final_drc.json final_candidate/mainboard_revD.kicad_pcb >independent_drc.log 2>&1
/usr/bin/python3 refill_check.py >independent_refill.log 2>&1
for s in reference_check plane_delta_final plane_islands_final newpaths_final retained_reference_unions clock_centerline copper_metrics collinear_screen model_replay aggregate_checks; do /usr/bin/python3 $s.py >independent_${s}.log 2>&1; done
/usr/bin/python3 -O aggregate_checks.py >independent_aggregate_optimized.log 2>&1
