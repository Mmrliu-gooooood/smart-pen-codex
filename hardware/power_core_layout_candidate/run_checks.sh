#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export TZ=UTC XDG_CONFIG_HOME=/tmp/rebuild-kicad/config XDG_CACHE_HOME=/tmp/rebuild-kicad/cache XDG_DATA_HOME=/tmp/rebuild-kicad/data
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" preview/schematic
kicad-cli version > kicad_version.txt
/usr/bin/python3 tools/build_footprints.py
python3 build_power_core.py
kicad-cli sch erc power_core_NOFAB.kicad_sch --exit-code-violations -o erc.rpt
kicad-cli sch export netlist power_core_NOFAB.kicad_sch --format kicadxml -o power_core_NOFAB.xml
/usr/bin/python3 tools/build_board.py
kicad-cli pcb drc power_core_NOFAB.kicad_pcb --schematic-parity -o placement_drc.rpt
/usr/bin/python3 tools/route_power.py
kicad-cli pcb drc power_core_NOFAB.kicad_pcb --schematic-parity --severity-all --exit-code-violations -o routed_drc.rpt
/usr/bin/python3 tools/verify_design.py
kicad-cli sch export svg power_core_NOFAB.kicad_sch -o preview/schematic/
kicad-cli pcb export svg power_core_NOFAB.kicad_pcb --layers F.Cu,F.Fab,Edge.Cuts --page-size-mode 2 --mode-single -o preview/front.svg
kicad-cli pcb export svg power_core_NOFAB.kicad_pcb --layers B.Cu,Edge.Cuts --page-size-mode 2 --mode-single -o preview/back.svg
/usr/bin/python3 tools/power_screen.py
/usr/bin/python3 tools/draw_diagnostics.py
