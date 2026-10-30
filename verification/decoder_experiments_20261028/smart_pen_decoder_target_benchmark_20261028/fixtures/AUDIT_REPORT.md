# Continuous-paper viewport integration audit — 2026-10-28

**Synthetic integration evidence only. No hardware, real camera frames, physical accuracy, S3 timing, nib pose, or VALID pen output is claimed. No decoder/repository files changed; no upload or push.**

## Main finding

The proposed 200×200 Gray8 / 5–7 mm FOV / .3 mm pitch configuration cannot be passed directly to the current optimized decoder: `detect()` rejects the 129th accepted dot, and rejects any >=3-pixel threshold component touching an image boundary. It does not truncate the input to 128 dots or ignore clipped boundary dots. Fixed center cropping alone is not enough to meet that contract reliably.

This is a mismatch between the optical-field proposal and the deliberately bounded small-ROI decoder, not evidence that rolling Anoto encoding requires 6×6 block alignment. It is not repaired here.

## Provenance and method

- Paper source: `smart_pen_original_20261028`, clean pinned commit `0f8b569176c77dad34aaf83bb008eb118c9f1208`.
- Decoder: `smart_pen_vision_opt_20261028`, clean commit `685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00`.
- Actual upstream `microdots.anoto_6x6_a4_fixed.encode_bitmatrix((1000,710),(10,2))`; full 1000×710 direction matrix saved as `upstream_directions.npy`. Not invented independent tiles and not firmware-generated answers.
- Pinned `digital_pen_ov5640/pc/configs/pattern.yaml` profile C: .3 mm pitch, .05 mm directional offset, .05 mm radius. Direction convention follows upstream codec adapter, camera canonical top-left +y downward. We render the actual encoding in canonical raster orientation, **not** a scan or rasterization of a user PDF.
- Continuous paper is independently rasterized to 200×200 Gray8 using 4×4 area samples/pixel, background 240, ink 30, ideal frontoparallel geometry, no added noise/blur. Offsets/radius are both pitch/6, unlike the older isolated .1-cell-radius fixture.
- FOV 5/6/7 mm gives pitch 12/10/8.5714 px. 36 views/FOV span all x/y integer origin residues mod 6, each with a fixed-seed random fractional cell origin (`20261028`). Origins lie near cells (120,240), section (10,2). Center crops are 200,96,80,64 px, with no rescaling.
- Only pixels, dimensions, known paper bounds/section, caller workspace, and an initially empty or previous-decode geometry prior enter the actual C decoder. Ground-truth geometry is used only after decoding to check coordinates and symbols, never to fit/select a grid or seed a prior.
- `audit.py` compiles unmodified `roi_opt.c`/`anoto.c` through a separate bridge in this artifact directory. Failed calls must leave poisoned output bytes untouched and clear prior. A C OK means decoded paper-window origin, not physical nib pose/VALID ink.
- Per-image raw-byte SHA256 and all parameters/statuses appear in `results.json`; sample PGM fixtures are included. Generator/profile file hashes and commits are in `provenance.json`.

## Untreated crops: actual decoder result

36 independent views per table cell; percentages are empirical coverage, not physical reliability estimates.

| FOV | 200 px | 96 px | 80 px | 64 px |
|---|---:|---:|---:|---:|
| 5 mm | 0/36 | 1/36 (2.8%) | 0/36 | 0/36 |
| 6 mm | 0/36 | 0/36 | 5/36 (13.9%) | 3/36 (8.3%) |
| 7 mm | 0/36 | 5/36 (13.9%) | 2/36 (5.6%) | 0/36 |

Across 432 cold calls: **16 OK (3.70%), 415 detection rejects (96.06%), 1 no-grid (0.23%), 0 ambiguity**. False-coordinate successes: **0/16**. Each success was decoded a second time with its returned prior: **16/16 correct warm successes**, not a stale-coordinate reuse test across moving frames. Successful images include 36–121 dots and 1–36 agreeing code windows. No-grid occurs for one 7 mm /96 px view. Detection failures combine edge policy, dot count, and insufficient accepted dots; don't attribute every untreated failure solely to the 128 cap.

## Code-window semantics

`roi_opt.c:107–118` checks every sliding complete 6×6 window in a candidate lattice and verifies that all decoded windows agree on `decoded_x-col, decoded_y-row`. It returns the first decoded window origin; that need not be image top-left or nib position. Neighboring windows deliberately have different x/y by their lattice offsets and are not treated as conflicting merely for that reason.

`verify_rolling.py` directly checks 576 overlapping windows (24×24 distinct origins), all x/y mod-6 phases: **576/576 exact positions**, zero errors. This is an isolated codec semantic test, not an acquisition coverage claim. The upstream PC `anoto/window_consensus.py` also explicitly implements sliding windows, not independent disjoint blocks. A small ROI must include at least one *complete observed* 6×6 lattice window; arbitrary viewport phases can leave fewer than six usable rows/columns even when nominal extent is six pitches.

## Tilt/perspective limitation (source inspection)

The candidate model is `R(angle) × diag(pitch,pitch*ratio)`, not general affine or homography. Cold search is angle −60…60° step 2°, pitch 8…32 px step .5, ratio .6…1.4 step .1. Its ranges do not guarantee continuous coverage. Every retained point must satisfy displaced-dot residual gates (`major .10… .30 cells`, `minor <=.065 cells`). It has no shear, projective denominator, lens distortion, paper curl, or nib-offset solve. In-plane angle ±60° **does not mean** physical pen tilt ±60°. The original PC has homography/spline facilities; these are not present in this C candidate.

Warm acceptance checks only local candidates; it does not establish global cold-search uniqueness. A correct finite warm test set cannot remove this known safety limitation. No physical tilted-pen claim is made by this frontoparallel test.

## Decision and next integration gate

Keep the optical 200×200 field as a capture option, but do not feed the whole field into this decoder and claim support. A production image-driven ROI/component-selection stage needs an explicit cap, partial-edge-dot policy, complete-window check, consistent frame-to-paper transform, failure propagation, and adversarial/real-frame tests. A center crop is not that stage. Simply increasing DOTS also leaves boundary policy, model validity, CPU/workspace cost, and safety unresolved.

The separate boundary-removal experiment below is diagnostic only: it erases threshold-connected components touching the crop border based solely on current pixels, never synthetic coordinates. It does not manufacture missing dots, choose a true grid phase, or change the decoder. It identifies whether conservative boundary handling can unlock the existing bounded model; it is not a proposed production-approved fix.

## Reproduction

From workspace root:

```sh
smart_pen_host_venv_20261028/bin/python smart_pen_viewport_audit_20261028/audit.py
smart_pen_host_venv_20261028/bin/python smart_pen_viewport_audit_20261028/verify_rolling.py
smart_pen_host_venv_20261028/bin/python smart_pen_viewport_audit_20261028/boundary_diagnostic.py
```

Only this separate artifact directory is written. Requires installed NumPy and host `cc`; no network or new dependencies. PGM fixtures avoid a Pillow dependency. `boundary_diagnostic.py` intentionally loads the setup/render/decoder portion of `audit.py` before the main sweep; run the baseline first.

## Diagnostic edge-component removal results (NOT production)

36 views per cell. Cold and sequential-prior status counts are identical in this finite sweep. Sequential prior comes only from previous actual image decoding within each FOV/ROI group; failures clear it.

| FOV | 200 px | 96 px | 80 px | 64 px |
|---|---:|---:|---:|---:|
| 5 mm | 0/36 | 36/36 | 31/36 | 0/36 |
| 6 mm | 0/36 | 36/36 | 36/36 | 20/36 |
| 7 mm | 0/36 | 30/36 | 36/36 | 36/36 |

Across 432 filtered cold calls: **261 OK (60.42%), 155 detection rejects (35.88%), 16 no-grid (3.70%), 0 ambiguity**. False successes: **0/261**. A separate 432-call sequential-prior pass has the same status totals, **232 actual warm-path successes**, and zero false successes. No no-grid case was converted into a wrong-coordinate OK.

After removing edge components, full 200px images still contain **256–281 / 364–400 / 506–533** interior accepted-size components at 5/6/7 mm. All 108 full-field cases still fail detection, isolating the >128-dot incompatibility independently of border clipping. At 5 mm, 64px contains only 22–27 interior dots (below required 36); at 6 mm it contains 33–38 and remains phase-sensitive. At 7 mm, 96px contains 101–121 dots, yet 6/36 clean crops still have no fit, so removal plus cap compliance is not sufficient. Source quantization/residual/model gates remain; this audit does not assign an unproven single cause for those six cases.

`boundary_summary.json` and `boundary_results.json` contain the complete results; `boundary_fixture_oracles.json` names representative filtered PGM files with status/coordinate oracle. **These filtered success rates are a diagnostic upper opportunity under ideal synthetic optics, not production coverage claims.**
