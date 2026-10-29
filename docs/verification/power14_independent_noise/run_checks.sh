#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export XDG_CONFIG_HOME=/tmp/power14audit/config
export XDG_CACHE_HOME=/tmp/power14audit/cache
export XDG_DATA_HOME=/tmp/power14audit/data
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
/usr/bin/python3 reproduce_network.py > network_run.log 2>&1
/usr/bin/python3 reproduce_thresholds.py > threshold_run.log 2>&1
sha256sum network_result.json threshold_result.json > /tmp/power14audit/result_normal.sha
/usr/bin/python3 -O reproduce_network.py > network_optimized_run.log 2>&1
/usr/bin/python3 -O reproduce_thresholds.py > threshold_optimized_run.log 2>&1
sha256sum -c /tmp/power14audit/result_normal.sha
/usr/bin/python3 - <<'PY'
import json,hashlib,pathlib
p=pathlib.Path('.').resolve();b=p.parents[2];h=b/'hardware/power_integrated_layout_14x45';m=json.loads((h/'manifest.json').read_text())
for name,sha in m['files'].items():
 if hashlib.sha256((h/name).read_bytes()).hexdigest()!=sha:raise RuntimeError('Frozen source changed: '+name)
old=json.loads((p.parent/'power14_vbus_paths/paths.json').read_text())['resistor_screen']['scenarios'];new=json.loads((p/'network_result.json').read_text())['scenarios']
for a,z in zip(old,new):
 if abs(a['trace_network_drop_mV']-z['drop_mV'])>1e-8 or abs(a['max_added_segment_current_A']-z['max_added_current_A'])>1e-8:raise RuntimeError('Network model mismatch')
print('PASS: independently reproduced network; frozen104 files intact; normal/-O outputs identical. This is analytical verification, not DRC, safety, or manufacturing approval.')
PY
