# Local continuous-paper ROI research candidate

Forked from `685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00`. Original worktrees are
frozen. This local tree has no git remote and has not been pushed or integrated
into the application. No hardware, physical nib VALID, actual pen tilt, or
ESP32-S3 FPS qualification is implied.

- Narrow design: `docs/software/continuous_roi_design.md`
- New API: `firmware/vision/roi_continuous.h`
- Integration and known limits: `docs/software/continuous_roi_integration_gate.md`
- Final evidence: `verification/CONTINUOUS_ROI_REPORT.md`
- Full results/provenance: `verification/continuous/`
- Superseded permissive-edge experiment: `verification/continuous_v1_permissive_edge/`

Run host gate with the original pinned source available:

```sh
../smart_pen_host_venv_20261028/bin/python software/verify_host.py \
  --upstream-pc-src ../smart_pen_original_20261028/digital_pen_ov5640/pc/src
../smart_pen_host_venv_20261028/bin/python tools/continuous_roi_sweep.py \
  --audit ../smart_pen_viewport_audit_20261028
```

Sweep uses the audit's actual upstream direction matrix solely for independent
rendering and post-decode oracles; none of its coordinates/FOV/angles enter C.
It is a finite synthetic evidence set, not a physical reliability estimate.
