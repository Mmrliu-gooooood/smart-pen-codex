# V3 continuous-fit candidate — final local evidence (2026-10-29)

## Decision

**The root cause is repaired for all recoverable cases in the frozen340-frame
synthetic sweep, without relaxing final validation.** Fractional FOV improves
**17→36/36**, in-plane rotation **60→76/96**. Exactly35 NO_GRID statuses become
correct OK; no other main-sweep status changes. All20 remaining rotated views
lack an actual complete6x6 window in their96px crop and remain rejected.

There are **0 wrong OK among253 accepted** in the340-frame sweep, with87
rejections. An independent held-out clean set accepts97/102 correctly; its
remaining5 also lack complete observed windows. These are finite synthetic
results, not physical reliability or global continuous-model uniqueness.

No original/V2 worktree, hardware, application VALID path or remote repository
was changed. No push, sensor qualification, real handwriting classification,
physical nib pose/accuracy, pen-tilt support, or ESP32-S3 real-time/FPS claim.

## Root cause, not test-ID selection

Sibling diagnostic artifact `smart_pen_continuous_fit_diagnostic_20261029`
instruments132 V2 scale/rotation calls and preserves every pixel hash, point
and stage count. All19 fractional rejects and16 recoverable rotation rejects
fail every coarse residual hypothesis. Their detected points are correct and
complete observed windows exist. True renderer geometry is used only **after
C returns** to diagnose that the existing phase estimator/strict gates are
otherwise sufficient. The20 no-window cases cannot be fixed by geometry
optimization; all are5mm/96px, not an accidental96→80 shrink.

The new fitter never reads FOV, angle, true coordinates, expected codewords,
known lattice cells, oracle matrix, or a previous/fake prior. Initializers come
only from measured current-pixel residuals over the same coarse search.

## Narrow implementation

- Keep V2's single pixel-selected ROI and bounded small-edge-fragment policy,
 128 core points and36..100 wrapper dots. No ROI retries by decode success.
- Keep every original61x49x9=26,901 coarse hypothesis. Wider **initializer-only**
  bounds (major<=.45, minor<=.25, RMS<=1/8 cell) nominate seeds; they do not make
  a model valid. Original acceptance remains major.10.. .30, minor<=.065,
  distinct cell occupancy, observed complete6x6, actual codec/paper bounds,
  within-model window agreement and cross-model coordinate agreement.
- Capture **all** qualified seeds, not a ranked top-k or first successful seed.
  The65th seed rejects AMBIGUOUS before any out-of-bounds write; earlier coarse
  success cannot hide overflow or a later conflicting interpretation.
- At most5 iterations/seed use every point: assign nearest cell and residual
  direction, form nominal cell+fixed1/6 displacement, then fit one orthogonal
  anisotropic basis using centered second moments and an analytic2x2 solution.
  No outlier removal, point repair, codeword-guided fitting, shear, homography,
  spline or new runtime dependency. Nonfinite/degenerate/out-of-range fits are
  discarded, not published. All resulting models run the unchanged validators.
- All coarse and refined successes participate in the final consensus. Only
  rejection can short-circuit; no early OK. Failed refinements cannot remove a
  valid existing coarse interpretation.

This finite initializer envelope and bounded convergence are **not** exhaustive
search of all continuous models. An alternative outside the envelope may be
unexamined. No stronger uniqueness or adversarial security claim is justified.

## Full340 V2 comparison

| Group | V2 accepted | V3 accepted | V3 remaining rejects |
|---|---:|---:|---|
| Profile-C5/6/7mm,36 phases each |108/108|108/108|0|
| Fractional FOV5.1..6.9mm |17/36|36/36|0|
| In-plane angles−60..60° discrete probes |60/96|76/96|20 NO_GRID, actual missing window|
| Gaussian blur .4/.8/1.2/1.6px |20/24|20/24|4 DETECTION|
| Bounded noise8/20/40 |9/9|9/9|0|
| Ink/blob/erasure/blank/random/low contrast |0/27|0/27|24 DETECTION,3 NO_GRID|
| Random direction grids |0/16|0/16|16 NO_GRID|
| Wrong section |0/3|0/3|3 NO_GRID|
| Model-boundary probes |4/21|4/21|2 DETECTION,15 NO_GRID|

All4 accepted model-boundary cases are modeled orthogonal anisotropy (ratio.6
or1.4); no tested shear/projective probe passes. No physical tilt claim follows.
Every OK is checked against exact upstream symbols, actual projected support
and all36 synthetic grid centers. Maximum accepted main-sweep grid discrepancy
is0.272212px; not a physical accuracy measurement. Raw frames match V2 hashes.
`continuous/results.json` and `v3_comparison.json` retain all outcomes/counters.

## Independent and adversarial evidence

Independent reviewer snapshot/report:
`smart_pen_continuous_v3_independent_review_20261029/REVIEW.md`, SHA256
`bd3060e24a05cc87dd0fdf3adf34b00ac752718d3dd79f7670db6fc23bd5e49b`.
No blocking issue found for this research slice, not deployment approval.

- Original opt44 frozen fixtures: cold complete result bytes and successful
  warm result/prior bytes match V2 **exactly**. Original opt result/workspace ABI
  and search behavior remain; code size/stack cost need not be identical.
- Independent54 clean views:29→49 correct OK;5 NO_GRID confirmed to have no
  complete observed window. Returned windows have actual component support.
- Independent48 exact-phase views:48/48 correct. Combined97/102 clean,
 0 wrong among97 accepted; max independent grid discrepancy0.156436px.
- Original18 negative/edge-policy cases and6 thin/half-dot/corner cases unchanged.
  The previously fixed8/11/12px deep-ink fragments still reject. Dot-sized4px
  fragments may still be erased: consistent remaining ROI is not ink
  classification, full-frame health or physical nib VALID.
- New68 adversarial probes:60 deliberately corrupted central code patterns and
 6 mirror/90° images all NO_GRID. A genuine7-window strip decodes correctly;
  a strip containing conflicting independently encoded windows is AMBIGUOUS,
  not the first locally successful coordinate. No false OK.
- Independent **actual default64** overflow image:36 malformed3px triangles,
 3px spacing, reaches seed65 after864 coarse hypotheses, returns AMBIGUOUS,
 0 iterations/0 refined models. Output/transform/seed guards are intact. This
  fixed PGM is a permanent regression, in addition to a compiled cap1 branch test.
- Native unit tests cover nonfinite seeds, degenerate all-point fits, default
  and cap1 overflow, failure output preservation and illegal paper config.

## Host verification and resources

Final full host gate: **85/85 tests, no skips**, plus portable core verification.
Strict C11 warnings-as-errors passes. ASan+UBSan no-recovery runs pass default64
and cap1 fitter tests plus400 malformed traversals; independent320 malformed
traversals and actual65th-seed guards also pass. Only LeakSanitizer is disabled
due the previously documented environment ptrace incompatibility; no leak
qualification is claimed. Production objects have no heap-allocation symbols.

Workspace **32,640B** =21,888 core+9,216 crop+1,536 seed scratch, compile-time
<=32KiB. Input200x200 Gray8 adds40,000B: input+workspace alone **72,640B**, before
result, stack, RTOS, DMA, application and transport. V3 continuous result is
192B versus V2 184B; matching header/binding is mandatory. The original opt
result/workspace ABI is unchanged. Never cast V3 into the application mapper.

| Work bound | Hard limit | Observed in main340 |
|---|---:|---:|
| Cold hypotheses |26,901|median/max26,901;0 for pre-detection rejection|
| Captured seeds |64;65th rejects|median3,max15|
| All-point refinement iterations |320|median15,max75|
| Additional strict model checks |64|median3,max15|

A separate direct-core geometry stress probe at pitch18/24/30/32px used up to
32 seeds/160 iterations; it is outside this continuous5–7mm wrapper coverage
study, not a new FOV qualification. Hard limits remain unchanged. Refits repeat
phase work and seed capture may examine more residuals than the old early
failure loop; a candidate count alone is not a CPU budget.

Host GCC14.2 `-O2 -fstack-usage` individual estimates: continuous wrapper496B,
refined entry560B, candidate416B, shared coordinates128B, phase80B, original opt
entry432B and forwarding wrapper48B. The fitter helper is inlined. These are
not S3 task high-water measurements or a summed target call-chain guarantee.

Eight paired alternating host calls/fixture recorded median process-CPU
V3/V2 ratios0.80..1.21. Results are environment/compiler sensitive; no speedup
or real-time claim is made. The original expensive cold search is retained.
No ESP32-S3 execution or60FPS inference is justified by fitting32KiB.

## Failure/API integration contract

Every nonzero decode result preserves result and transform bytes; input is
immutable. Optional refine **diagnostics** intentionally reset/overwrite each
call, including failure. Diagnostics, result, transform, seeds, input, config
and workspace must not overlap. Scratch cannot be concurrently/reentrantly
shared or placed on an unqualified small task stack.

The current application, calibration/contact/camera-qualified gates and physical
nib mapper remain untouched. Remaining no-window cases need a separately
justified optical/ROI support design, not synthetic dots. Real printed/camera,
handwriting, blur, calibrated lens/axis/nib and S3 timing/resource tests remain
necessary before integration. See the design/integration docs and reproducible
commands in `README_CONTINUOUS_CANDIDATE.md`.
