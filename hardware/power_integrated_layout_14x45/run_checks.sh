#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export TZ=UTC
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/tmp/power14-kicad-config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/power14-kicad-cache}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-/tmp/power14-kicad-data}"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" preview
kicad-cli sch export netlist --format kicadxml -o power_integrated_study.xml power_integrated_study.kicad_sch >netlist.log
kicad-cli sch erc --exit-code-violations -o erc.rpt power_integrated_study.kicad_sch >erc.log
kicad-cli pcb drc --schematic-parity --exit-code-violations -o drc.rpt power_integrated_study.kicad_pcb >drc.log
for x in check_projection check_copper_graph power_screen check_mask_openings layout_metrics; do /usr/bin/python3 "tools/$x.py" >"$x.log"; done
/usr/bin/python3 - <<'PY'
import json
p=json.load(open('projection_check.json'));assert (p['components'],p['net_pins'],p['core_copper_items_geometrically_unchanged'],p['removed_only_obsolete_CE_branch'])==(52,150,182,8)
c=json.load(open('copper_graph.json'));assert c['status']=='PASS' and len(c['actual_copper_graph'])==25 and all(x['connected'] for x in c['actual_copper_graph'])
print('PASS native checks + source projection + 25/25 actual copper networks; NOFAB physical gates remain')
PY
