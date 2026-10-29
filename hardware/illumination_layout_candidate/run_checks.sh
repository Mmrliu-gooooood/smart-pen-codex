#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export TZ=UTC
export XDG_CONFIG_HOME=/tmp/illum-layout-config XDG_CACHE_HOME=/tmp/illum-layout-cache XDG_DATA_HOME=/tmp/illum-layout-data
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" preview
kicad-cli sch export netlist --format kicadxml -o illumination_NOFAB.xml illumination_NOFAB.kicad_sch >netlist.log
kicad-cli sch erc --exit-code-violations -o erc.rpt illumination_NOFAB.kicad_sch >erc.log
kicad-cli pcb drc --schematic-parity --exit-code-violations -o drc.rpt illumination_NOFAB.kicad_pcb >drc.log
/usr/bin/python3 tools/check_design.py >verification.log
/usr/bin/python3 tools/check_copper_graph.py >copper_graph.log
/usr/bin/python3 - <<'PY'
import json
x=json.load(open('copper_graph.json'));assert x['status']=='PASS' and len(x['actual_copper_graph'])==7
print('PASS 16 source/PCB endpoints and 7 actual copper networks; NOFAB optical and assembly gates remain')
PY
