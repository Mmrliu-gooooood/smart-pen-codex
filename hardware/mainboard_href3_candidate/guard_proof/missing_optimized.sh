#!/bin/bash
set -euo pipefail
/usr/bin/python3 -O /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href3_candidate/validate_expected.py /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href3_candidate/mainboard_revD.kicad_pcb /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href3_candidate/guard_proof/missing.json
printf passed > /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href3_candidate/guard_proof/missing_optimized.marker
kicad-cli pcb drc --exit-code-violations --all-track-errors --schematic-parity -o /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href3_candidate/guard_proof/missing_optimized.rpt /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_href3_candidate/mainboard_revD.kicad_pcb
