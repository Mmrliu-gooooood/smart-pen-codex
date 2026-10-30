# Local V3 continuous-fit research candidate

V2 is frozen in the separate `smart_pen_continuous_roi_candidate_20261028` tree.
This independent V3 augments current-pixel cold geometry with bounded all-point
continuous orthogonal fitting; original acceptance gates and old opt API remain.
No push, app integration, physical nib VALID, real pen tilt, or S3 FPS claim.

- Design: `docs/software/continuous_refine_v3_design.md`
- Final results/limits: `verification/CONTINUOUS_V3_REPORT.md`
- API/ABI: `firmware/vision/roi_continuous.h` and `roi_opt.h`
- Integration gate: `docs/software/continuous_roi_integration_gate.md`
- Full340 results/provenance: `verification/continuous/`
- Corrupt-code/cross-window evidence: `verification/v3_adversarial/`
- Prior V2 evidence retained under `verification/v2_baseline/` (historical,
  not current source hashes). Original V2 remains the authoritative snapshot.
- Root-cause experiments: sibling `smart_pen_continuous_fit_diagnostic_20261029`
- Independent review: sibling `smart_pen_continuous_v3_independent_review_20261029`

```sh
PYTHONDONTWRITEBYTECODE=1 ../smart_pen_host_venv_20261028/bin/python software/verify_host.py \
  --upstream-pc-src ../smart_pen_original_20261028/digital_pen_ov5640/pc/src
PYTHONDONTWRITEBYTECODE=1 ../smart_pen_host_venv_20261028/bin/python tools/continuous_roi_sweep.py
PYTHONDONTWRITEBYTECODE=1 ../smart_pen_host_venv_20261028/bin/python tools/adversarial_refine_v3.py
```

No coordinates, FOV, angle or fake prior enters C. Independent renderer truth
is used only after decoding. V3's result appends telemetry (matching header
required); never pass a V2 result buffer or cast this into the application mapper.
