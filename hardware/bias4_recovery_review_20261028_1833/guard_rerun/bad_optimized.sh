#!/bin/bash
set -euo pipefail
/usr/bin/python3 -O /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_resume_20261028/validate_expected.py /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_resume_20261028/mainboard_revD.kicad_pcb /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_resume_20261028/guard_proof/bad.json
printf passed > /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/bias4_recovery_review_20261028_1833/guard_rerun/bad_optimized.marker
kicad-cli pcb drc -o /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/bias4_recovery_review_20261028_1833/guard_rerun/bad_optimized.rpt /workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_resume_20261028/mainboard_revD.kicad_pcb
