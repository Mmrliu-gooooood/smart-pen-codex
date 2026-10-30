# Continuous-paper ROI candidate v2 — local verification

## Decision and important limits

**A separate bounded pixel-only ROI candidate repairs the ideal full-field
integration mismatch, not the whole camera/pen problem.** In the exact frozen
upstream Profile-C 200px / 5,6,7mm / 36-phase sweep: **108/108** decode correctly,
versus 0/108 direct full-field calls to the original decoder.

**Major coverage limits remain:** fractional FOV **17/36**, in-plane rotation
**60/96**. These gaps prevent claiming general continuous-scale/rotation
support, let alone real physical pen tilt. Across all340 synthetic cases,
**0 wrong OK among218 accepted**,122 rejected. This finite result is not a
population false-positive bound and must not be hidden by a total success rate.
No hardware, nib VALID, physical accuracy, real handwriting classification,
S3 performance/FPS, or application integration is claimed. No push occurred.

## What changed

Fork of frozen `685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00` in a separate local tree,
with its git remote removed. Original source trees stay clean.

- `pen_roi_decode_continuous`: current pixels select centered96px, then80px
  only if too many interior components. Select36..100 dots; never choose a crop
  by its decoded answer. One full cold search, no prior, no retry after NO_GRID
  or ambiguity. Original128-point cap, residual gates and sliding6x6 consensus
  remain unchanged. Rolling windows never required tile alignment.
- Eight-connected border components may be removed only if area<=24px,
  bbox<=6x6px, inward depth<=4px for **each** touched edge. Oversized/complex
  components reject. No missing-dot synthesis or interpolation.
- Additive `pen_roi_decode_opt_transform` exposes the winning model anchor and
  basis vectors without changing old result/API ABI. New wrapper returns exact
  crop rectangle and mutually inverse paper-cell/frame-pixel affine matrices.
  Frame=crop+(left,top); integer coordinates denote pixel centers. These are
  fitted orthogonal-grid diagnostics, **not physical nib coordinates**.
- All nonzero statuses preserve every output byte. Input stays unchanged.
  Argument and input-range validation precedes image access. No malloc/recursion.

## Independent ink finding and closure

V1's12x12/100px border gate was too permissive: 3px-high strokes reaching8,
11 or12px into the crop were erased, allowing correct remaining-grid decoding.
Correct coordinates did **not** make that ink policy safe. V1 source/results
remain in `continuous_v1_permissive_edge`; independent case063–065 PGMs became
permanent rejection regressions.

V2's stricter24px/6px/4px gate rejects all three. The independent reviewer
replayed72 original images: all29 clean accepted views remain accepted; only
these three deep-stroke statuses change to DETECTION. An extra48 exact-phase
views passed independent symbols/support/forward/inverse transform checks.
Combined independent clean set:77 accepted/102 attempted,0 wrong among77.

**Remaining limit:** dot-sized ink (including a4px-deep fragment) can still
be erased, and outside-ROI pixels are not checked. Output exposes removed
component/pixel counts, not a claim that the whole frame is clean. Half-dot,
sliver and isolated corner probes pass; an injected corner merged with a paper
dot to depth6 correctly rejects. See external independent report
`smart_pen_continuous_independent_review_20261029/v2/REVIEW.md` and its frozen
hashes. The policy is a size envelope, not an ink classifier or anti-spoofing.

## Full synthetic sweep

Actual upstream direction matrix from pinned paper commit
`0f8b569176c77dad34aaf83bb008eb118c9f1208`, section(10,2), ProfileC .3mm pitch,
.05mm offset/radius. No FOV, coordinates, angle, matrix, or prior enters C.
Baseline render raw-byte hashes match all108 original audit frames exactly.
Independent oracles require exact36 symbols, supported observed window, and
fitted grid error<=0.1 pitch at all36 cell centers (diagnostic tolerance, not
physical accuracy). Per-frame parameters, hashes and outcomes are retained.

| Group | Accepted / attempted | Rejections | Wrong accepted |
|---|---:|---|---:|
| FOV5/6/7, all36 phases each |108/108|0|0/108|
| In-plane rotation,8 angles x3 FOV x4 phases |60/96|36 NO_GRID|0/60|
| Fractional FOV5.1..6.9,9 values x4 phases |17/36|19 NO_GRID|0/17|
| Gaussian blur sigma .4/.8/1.2/1.6px |20/24|4 DETECTION|0/20|
| Additive bounded noise amplitudes8/20/40 |9/9|0|0/9|
| Stroke, large blob, erasure, black/blank/checker/random/low-contrast |0/27|24 DETECTION,3 NO_GRID|—|
| Independent random direction grids |0/16|16 NO_GRID|—|
| Wrong section |0/3|3 NO_GRID|—|
| Shear/projective/anisotropic/out-of-range angle probes |4/21|2 DETECTION,15 NO_GRID|0/4|

The4 accepted model-boundary cases are **only modeled orthogonal anisotropy**:
FOV5 ratio.6, FOV6 ratio.6, FOV6 ratio1.4, FOV7 ratio1.4. No tested shear or
projective case passed. This does not support homography/perspective. All
+/-45-degree probes rejected; even search-grid angles are not uniformly
covered. Fractional FOV5.1/6.1/6.5/6.9 all rejected in these four phases each.
Coarse discrete pitch/angle search and strict model gates are known limits;
this experiment does not assign every rejection a single proved cause. No
threshold was relaxed to inflate coverage.

Max accepted grid-model discrepancy was0.422px for baseline,0.911px overall
(fractional FOV). These are errors against synthetic raster truth only.
V2 rejected two additional heavy-blur images relative to V1; this conservative
coverage loss was retained rather than weakening the corrected edge gate.

## Regression, safety and compatibility

- Baseline full host gate:72 tests, no skipped tests.
- Final full host gate:80 tests, no skipped tests; see `continuous_host.log`.
- Old public API independently replays44 frozen original audit fixtures with
  identical statuses/coordinates and failure preservation. Original strict
  border policy is not relaxed by its new optional-transform implementation.
- New fixed regression set includes6 full-frame Profile-C PGMs,10 extended
  rotation/scale/blur/ink/fake/shear/density PGMs, and3 independent deep-ink PGMs.
  Test inputs are raw pixels; metadata is used only after C returns.
- Native400 randomized malformed traversals plus buffer/size/state contracts
  pass ASan+UBSan with no recovery allowed. Independent320 negative traversals
  also pass workspace guards and failure output-preservation checks.
- LeakSanitizer could not run under this environment's ptrace conditions;
  original error log retained. Only leak scanning was disabled on successful
  ASan+UBSan runs. Both production objects have no heap-allocation symbols.
- Strict C11 `-Wall -Wextra -Werror -pedantic`; `git diff --check` clean.

## Memory and performance: not a real-time result

Workspace measured31,104B =21,888B old core +9,216B crop; compile-time<=32KiB.
The immutable200x200 input adds40,000B, so input+workspace alone is71,104B;
application/RTOS/DMA buffers and call stack are additional. Core128-point
capacity unchanged. Traversal is bounded to2 crops, <=9216 pixels per crop,
and a256-entry queue. One cold search tests up to26,901 hypotheses.

Host GCC14.2 `.su` estimates changed: original opt400B and candidate352B;
new transform entry496B, candidate400B, old-API forwarding wrapper48B;
continuous wrapper464B. These are individual function estimates, not maximum
call-chain totals or S3 task high-water. The old API's stack cost increased,
so previous target-stack figures must not be reused unqualified.

Exploratory wall-clock host baseline median238ms/max642ms; whole sweep max
1478ms while other agents/tests shared the machine. Timing is deliberately
not a benchmark guarantee and must not be converted to S3 FPS. No target
execution was performed. A separate RAM-only benchmark variant/build and
then physical timing/resource measurements remain required.

## Reproduction and next gate

See `README_CONTINUOUS_CANDIDATE.md` and `continuous/provenance.json` for
commands, compiler and source hashes; `continuous/results.json` contains all
340 records. `CONTINUOUS_SNAPSHOT.json`/`CONTINUOUS_SHA256SUMS` freeze the tree.
The independent review has its own frozen V1/V2 sources and reproduction steps.

The current application pipeline is unchanged. Before any integration, address
scale/angle acquisition coverage without sacrificing rejection, qualify real
camera and handwritten frames, measure S3 timing/stack/memory, and supply a
calibrated physical nib mapper. See
`docs/software/continuous_roi_integration_gate.md`. No recording/contact,
calibration, or default camera_qualified gates may be bypassed.
