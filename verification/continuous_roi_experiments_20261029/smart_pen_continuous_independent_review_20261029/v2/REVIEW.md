# V2 independent closure — strict short boundary fragments

## Decision

**F1 fixed within the stated bounded-fragment policy.** Do not interpret this as general ink classification, whole-frame health or physical nib VALID. The API certifies only consistent surviving ROI code windows under its fitted orthogonal model. Dot-sized ink remains indistinguishable and evidence outside the selected ROI remains unchecked.

V1 report and cases remain untouched in parent directory. V2 source is separately frozen in `v2/snapshot`:
- roi_continuous.c `66e2d18c44f4ca679269c026c495e8d7a851a2efcbeb07955d3d95a505a62f9e`
- roi_continuous.h `3a50fabc1ec5a3271bb6f73fcd41095e69fbf0b271c0e88e6e555d073a2d34ab`
- roi_opt.c/h unchanged from V1 hashes; therefore the reviewed transform implementation and old44-API regression are unaffected by this wrapper-only change.

## Observed results

- Same72 frozen V1 images replayed against V2: all **29/29** clean accepted rotated/noisy/blurred views retained; the other25 clean probes remain NO_GRID. No new false coordinate. Only changed statuses: case063/064/065 (8/11/12px deep stroke) become DETECTION rejects; output remains unchanged on failure.
- The4px-deep3px-high stroke still returns correctly decoded OK, demonstrating the explicitly retained dot-sized-ink limitation.13/20/50px strokes remain rejected.
- **48/48 additional exact-phase clean images correctly accepted**: FOV5/6/7mm × x/y fractional phases{0,.125,.5,.875}. No geometry was supplied to decoder. Output symbols, visibility, forward transform and inverse roundtrips verified independently. Maximum grid error0.435398px across these synthetic views. Not a physical accuracy measurement.
- Combined clean independent cases: **77 accepted/102 attempted, 0 wrong coordinates among77 accepted**,25 NO_GRID. Finite synthetic coverage, not a population error guarantee.
- Thin1×4 boundary fragment, half-disk fragment,1×1 corner,1×4 corner: all correctly accepted after filtering. A4×1 injected corner merged with an actual paper dot into a12pixel,6×4 threshold component touching two borders; rejection follows inward-depth6>4. The **isolated4×1 corner control correctly accepts**, so the earlier rejection was a genuine merged-component gate, not a prohibition on thin corner fragments.
- V2 native ASan+UBSan **320/320** negative traversal cases pass output-preservation/workspace-guard checks without sanitizer findings. Full-black/complex-connected inputs remain bounded. Leak scanning disabled, no target-stack claim.

## Why the change addresses F1

An erasable boundary-connected component must now simultaneously have area<=24pixels, both bounding dimensions<=6pixels, and depth<=4pixels for **every** touched edge. This prevents the previously observed1.2-pitch intrusion from being silently removed. It remains a fixed pixel envelope for Profile-C at the stated sampling range, not a measured dot classifier. Larger/blurred/tilted genuine clipped dots may be conservatively rejected; no universal coverage claim.

## Artifacts / reproducibility

- `replay_v1.json`: unchanged original pixels, before/after statuses.
- `phase.json`: all48 phase cases and hashes/oracles.
- `fragments.json`, fragmentPGMs, `corner_control.json`: half/sliver/corner checks.
- `summary.json`, `safety.log`, `SNAPSHOT.sha256`.

From workspace root:
```sh
smart_pen_host_venv_20261028/bin/python smart_pen_continuous_independent_review_20261029/v2_review.py
smart_pen_host_venv_20261028/bin/python smart_pen_continuous_independent_review_20261029/corner_control.py
```
The initial helper's empty-pixel search demanded an unnecessarily large11×8 blank patch and stopped only *after* saving replay/phase results; this test-harness condition was corrected to a six-by-four neighborhood and fragments resumed with `resume_fragments.py`, without rerunning the completed sweep. Corrected `v2_review.py` reproduces all stages in one run. Original log is retained for transparency.

For sanitizer reproduction, use the parent REVIEW command with the include/source/output paths changed from `snapshot/...` to `v2/snapshot/...` and output `v2/safety`; the independent `safety.c` is unchanged.
