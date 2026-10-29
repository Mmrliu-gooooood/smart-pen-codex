#!/bin/sh
set -eu
cd "$(dirname "$0")"
export XDG_CONFIG_HOME=/tmp/rebuild-kicad/config XDG_CACHE_HOME=/tmp/rebuild-kicad/cache XDG_DATA_HOME=/tmp/rebuild-kicad/data
python3 tools/build_dqa_footprint.py
python3 tools/build_schematic.py
kicad-cli sch export netlist --format kicadxml --output usb_tail_revA.xml usb_tail_revA.kicad_sch
/usr/bin/python3 tools/build_pcb.py
./run_checks.sh
