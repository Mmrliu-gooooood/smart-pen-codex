#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export XDG_CONFIG_HOME="$PWD/.tool_state/config" XDG_CACHE_HOME="$PWD/.tool_state/cache" XDG_DATA_HOME="$PWD/.tool_state/data"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
python3 build_power_core.py
kicad-cli version > kicad_version.txt
kicad-cli sch erc power_core_NOFAB.kicad_sch --exit-code-violations -o erc_20261028.rpt
kicad-cli sch export netlist power_core_NOFAB.kicad_sch --format kicadxml -o power_core_NOFAB.xml
kicad-cli sch export pdf power_core_NOFAB.kicad_sch -o power_core_NOFAB.pdf
python3 check_netlist.py
pdftoppm -scale-to 2000 -png -singlefile power_core_NOFAB.pdf review_20261028
