# V3 independent source and synthetic regression review

## Decision

**No blocking defect found for the stated local research slice.** This is not
camera/physical-nib VALID, real-ink classification, global continuous-model
uniqueness, physical tilt, or ESP32-S3 timing qualification. Only the source
snapshot named below was reviewed; the implementation tree was not modified.

- roi_opt.c: `508f6fb7d7b96e51be47eed75f44f17a768a725a7516ac0354456c8fd44b996a`
- roi_opt.h: `ccadb210be379f3fce8e2ae8e02b4b6521a37804c2a48b9f6a3f02689a8dbe18`
- roi_continuous.c: `12b165125e32454a7252c8eaca510870bda149585af055c380c22d9c6f21aa7c`
- roi_continuous.h: `fa0e6be6b4df4752d948f6222e06c21303c847f1b59b9cdd798ccc9f827ed062`

`SNAPSHOT.sha256` also freezes supporting codec and headers. V2 comparison was
against the separately frozen `smart_pen_continuous_roi_candidate_20261028`.

## Standards axis

No blocking architecture/interface issue found. Shared `coordinates()` keeps
phase normalization in one place; the original opt result/workspace ABI remains
unchanged. V3 has a distinct continuous-result size (192 bytes versus V2's184),
explicitly documented as incompatible with a V2 binding. Caller-owned seed
storage is bounded, no heap dependency or recursive traversal is introduced.
The existing wrapper's final output assignment is retained, so errors do not
publish partial grid/transform data.

Nonblocking clarity suggestions, not required source churn for this snapshot:

1. The API comment's no-alias rule should explicitly name **diagnostics,
   result, transform, seeds, input, config and workspace** together. Diagnostics
   are deliberately overwritten even on argument failure; this is not the
   untouched-result contract. Callers must not overlap those output objects.
2. The design's phrase "subtract the fixed1/6 directional offset" is shorthand:
   implementation lines203–205 actually fits measured pixels against inferred
   integer cells **plus** their directional offsets. This is mathematically the
   intended observation model, not interpolation or point repair.
3. Capture constants .45/.25/1/64 and five iterations are visible in one local
   implementation but could be named alongside the64-seed budget when policy
   configuration is next revised. They are initializer bounds, not validation
   thresholds or a guaranteed convergence basin.

## Spec axis: reviewed invariants

References below are in the frozen `snapshot/firmware/vision/roi_opt.c`.

- **Original coarse validation retained:** lines101–112 use the wider envelope
  only to nominate seeds. The strict `.10.. .30` major and `.065` minor gate
  still controls `good`; line112 rejects a model failing it. Every strict-valid
  model is inside the wider early-return envelope. Distinct-cell checks,
  complete6x6 windows, codec bounds/section checks and window-translation
  consensus remain at lines113–131. Codec source is unchanged and bounds the
  decoded origin to the declared paper.
- **No success shortcut or seed truncation:** the whole61x49x9 coarse pass is
  lines242–251; only rejection can return early. The65th seed returns AMBIGUOUS
  before writing beyond64 entries. Lines253–259 examine every retained refined
  model and merge with all coarse successes. Final output is assigned only at
  lines263–264. Every accepted independently replayed V3 case reported
  `candidates - refined_models == 26901`.
- **No truth/codeword fit:** lines194–225 use every detected point, inferred
  cell/residual direction, fixed nominal1/6 offset and a centered orthogonal
  least-squares model. No decoded symbols, oracle geometry, point deletion,
  replacement, image synthesis, RANSAC or homography enters the refinement.
- **Numerical and model bounds:** lines215–224 reject nonfinite/degenerate
  second moments/eigenvalue gap and out-of-range pitch/ratio/angle. Positive
  pitch>=8 and ratio>=.6 imply a positive orthogonal determinant>=38.4px²;
  the wrapper independently checks determinant before inversion. Refined
  models are passed through the same strict candidate function, not accepted
  based on fit objective alone.
- **Failure contracts:** original prior clearing remains; the new cold API has
  no prior. Result/transform are untouched on nonzero status under the stated
  no-alias contract. Diagnostic counters are explicitly different: they are
  overwritten each call. Input frame bytes stay unchanged in replay tests.

The finite explored-model consensus is **not a proof of uniqueness over all
continuous models**. A seed outside the capture envelope or a refinement that
fails to converge may leave a continuous alternative unexamined. The design
already states this; no stronger safety claim is justified.

## Independent replay results

The reviewer built the frozen source directly, without the developer's link
wrapper. Production C received only raw pixels, shape, paper bounds/section and
caller storage; truth was used only after return.

- **Original opt44 fixtures:** all cold statuses and complete result bytes
  match V2. For their successful images, warm result bytes and updated prior
  bytes also match V2 exactly (`legacy44.json`).
- **Old independent72 images:**54 clean probes improve from29 to49 accepted,
  with no lost V2 acceptance and no wrong accepted symbols/coordinates.
  The other5 clean cases are all5mm near32-degree views. Independent component
  extraction plus post-hoc true-cell mapping confirms that each lacks a
  complete observed6x6 window; all49 returned windows consist entirely of
  actual observed components (`observed_support54.json`).
- All18 negative/edge-policy probe statuses match V2: excluded paper bounds,
  wrong section, invalid bounds, blank/noise/connected ink still reject;
  the explicitly allowed4px-deep small fragment still decodes, while8/11/12px
  and deeper strokes reject. This does not establish ink classification.
- **48 exact fractional-phase images:** regenerated by the prior independent
  inverse rasterizer, raw hashes match V2,48/48 correctly decode. Combined
  independent clean set: **97 correct accepted /102 attempted**,5 NO_GRID,
  **0 wrong among97 accepted**. Full forward/inverse transforms and exact
 36-direction codewords were checked. Max grid-model discrepancy across the
  accepted replay/phase/fragment sets is0.156436px against synthetic truth only.
- **Six thin/half-dot/corner probes:** all statuses remain unchanged; the
  merged deeper corner rejects, the five supported small-fragment cases pass.
- **Twenty parent diagnostic no-window images:** independently replayed raw
  pixels remain NO_GRID; no missing point was fabricated to recover them.

## Default64-seed overflow counterexample and sanitizer

Added a separate deterministic malformed-dot fixture:36 isolated three-pixel
triangles on a3px-spacing6x6 array. This is not a legitimate paper pattern.
With the actual default64 budget (not a reduced-cap test build), it reaches
seed65 after864 coarse hypotheses and returns AMBIGUOUS, with zero refinement
iterations/models. The output/transform and canaries immediately before/after
seed storage remain unchanged. `overflow_pitch3.pgm` and `overflow_probe.json`
freeze it; this directly tests the real overflow branch.

Native ASan+UBSan, strict no-recovery mode, passes320 randomized malformed
traversal cases plus this default65th-seed case. Workspace/seed guards and
failure output preservation hold (`safety.log`). Leak scanning is disabled for
the environment's known ptrace incompatibility; no leak qualification is made.

## Resource observations, not target qualification

C `sizeof` independently confirms32,640-byte continuous workspace,
21,888-byte original core workspace and192-byte V3 result. A200x200 Gray8 frame
adds40,000 bytes: input plus workspace alone is72,640 bytes, before result,
call stack, application, RTOS, DMA or transport storage.

Host GCC14.2 `-O2 -fstack-usage` individual-function estimates (`stack/*.su`):

| Function | Bytes |
|---|---:|
| continuous wrapper |496|
| refined transform entry |560|
| strict candidate |416|
| shared coordinates |128|
| phase |80|
| original opt transform entry |432|
| original opt forwarding wrapper |48|

The refinement helper was inlined into its entry in this host build. These are
not stack high-water measurements or a target call-chain total. Original opt
ABI compatibility does not mean identical code size/stack/cost. No target
execution, FPS extrapolation or real-time qualification was performed.

## Reproduction

From workspace root:

```sh
PYTHONDONTWRITEBYTECODE=1 smart_pen_host_venv_20261028/bin/python smart_pen_continuous_v3_independent_review_20261029/review.py
PYTHONDONTWRITEBYTECODE=1 smart_pen_host_venv_20261028/bin/python smart_pen_continuous_v3_independent_review_20261029/verify_observed_support.py
PYTHONDONTWRITEBYTECODE=1 smart_pen_host_venv_20261028/bin/python smart_pen_continuous_v3_independent_review_20261029/overflow_probe.py
```

Sanitizer command from this artifact directory:

```sh
cc -O1 -g -std=c11 -Wall -Wextra -Werror -pedantic -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -Isnapshot/firmware/vision safety.c snapshot/firmware/vision/roi_continuous.c snapshot/firmware/vision/roi_opt.c snapshot/firmware/codec/anoto.c -lm -o safety
ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 UBSAN_OPTIONS=halt_on_error=1 ./safety
```

No source edit, hardware access, upload, push or app VALID change occurred.
