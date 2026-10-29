#!/bin/bash
set -euo pipefail
/usr/bin/python3 /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href2_candidate/validate_expected.py /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href2_candidate/mainboard_revD.kicad_pcb /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href2_candidate/guard_proof/empty.json
printf passed > /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href2_candidate/guard_proof/empty_normal.marker
kicad-cli pcb drc --exit-code-violations --all-track-errors --schematic-parity -o /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href2_candidate/guard_proof/empty_normal.rpt /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href2_candidate/mainboard_revD.kicad_pcb
