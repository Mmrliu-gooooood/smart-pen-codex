#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export XDG_CONFIG_HOME="$PWD/.tool_state/config" XDG_CACHE_HOME="$PWD/.tool_state/cache" XDG_DATA_HOME="$PWD/.tool_state/data"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
python3 build_power_safety.py
kicad-cli version > kicad_version.txt
kicad-cli sch erc power_safety_NOFAB.kicad_sch --exit-code-violations -o erc_20261028.rpt
kicad-cli sch export netlist power_safety_NOFAB.kicad_sch --format kicadxml -o power_safety_NOFAB.xml
kicad-cli sch export pdf power_safety_NOFAB.kicad_sch -o power_safety_NOFAB.pdf
python3 check_netlist.py
pdftoppm -scale-to 2000 -png -singlefile power_safety_NOFAB.pdf review_20261028
