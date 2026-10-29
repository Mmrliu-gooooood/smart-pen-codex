#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export TZ=UTC XDG_CONFIG_HOME=/tmp/p14sf/config XDG_CACHE_HOME=/tmp/p14sf/cache XDG_DATA_HOME=/tmp/p14sf/data
mkdir -p "$XDG_CONFIG_HOME/kicad/9.0" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
cp /usr/share/kicad/template/fp-lib-table "$XDG_CONFIG_HOME/kicad/9.0/fp-lib-table"
kicad-cli sch export netlist --format kicadxml -o power_integrated_study.xml power_integrated_study.kicad_sch >single_feed_netlist.log
kicad-cli sch erc --exit-code-violations -o single_feed_erc.rpt power_integrated_study.kicad_sch >single_feed_erc.log
kicad-cli pcb drc --schematic-parity --exit-code-violations -o single_feed_drc.rpt power_integrated_study.kicad_pcb >single_feed_drc.log
/usr/bin/python3 tools/check_copper_graph.py >single_feed_copper_graph.log
/usr/bin/python3 physical_contacts.py >revB_physical.log
/usr/bin/python3 -O physical_contacts.py >revB_physical_optimized.log
cmp revB_physical.log revB_physical_optimized.log
/usr/bin/python3 reproduce_network_candidate.py >network_candidate.log
/usr/bin/python3 -O reproduce_network_candidate.py >network_candidate_optimized.log
cmp network_candidate.log network_candidate_optimized.log
/usr/bin/python3 check_single_feed.py >single_feed_check.log
/usr/bin/python3 -O check_single_feed.py >single_feed_check_optimized.log
cmp single_feed_check.log single_feed_check_optimized.log
