#!/bin/bash
set -eu
cd "$(dirname "$0")"
export XDG_CONFIG_HOME=/tmp/rebuild-kicad/config XDG_CACHE_HOME=/tmp/rebuild-kicad/cache XDG_DATA_HOME=/tmp/rebuild-kicad/data
kicad-cli sch export netlist --format kicadxml -o mainboard_revD.xml mainboard_revD.kicad_sch
kicad-cli sch erc -o erc.rpt mainboard_revD.kicad_sch
kicad-cli pcb drc --schematic-parity -o drc.rpt mainboard_revD.kicad_pcb
/usr/bin/python3 tools/check_native_source.py >native_source_check.log
/usr/bin/python3 tools/check_xclk_delta_return.py >xclk_delta_return.log 2>&1
/usr/bin/python3 tools/check_input_aon.py mainboard_revD
/usr/bin/python3 tools/check_input_other_rails.py mainboard_revD GND
/usr/bin/python3 tools/check_input_other_rails.py mainboard_revD SENS_VIO_1V8
/usr/bin/python3 tools/check_signal_components.py mainboard_revD
/usr/bin/python3 tools/check_plane_corridor.py >plane_corridor.log
