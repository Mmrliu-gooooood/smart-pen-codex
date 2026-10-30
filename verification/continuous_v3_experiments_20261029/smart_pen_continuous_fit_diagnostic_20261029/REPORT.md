# Continuous-fit diagnosis — 2026-10-29

## Proven root causes and decision

V2 remains frozen. The19 fractional-FOV rejections and16 of36 rotated
rejections can be repaired by continuous orthogonal fitting, without relaxing
acceptance gates. The other20 rotated images have **no complete observed6x6
window in their selected96px crop**. They must remain rejected unless a later,
separately qualified optical/ROI policy changes actual support; no missing-dot
prediction, codec guessing or success-driven ROI retries are justified.

| V2 rejected group | Cases | All26,901 models fail residual gates | Has a complete true observed window | Additional finding |
|---|---:|---:|---:|---|
| Fractional FOV |19|19|19|No candidate reaches codec validation|
| Rotation, recoverable |16|16|16|Angles+/-45 degrees lie between coarse samples|
| Rotation, no observed window |20|8|0|Other12 already have strict-fit models but zero windows|

For all132 scale/rotation probes (including successful controls), every detected
point has the correct direction when evaluated **after decoding** against the
independent renderer geometry. No duplicate true cells occur. At the true
render geometry, the existing three phase-correction iterations pass the
unchanged strict residual gates for all132. This is a post-hoc diagnostic only:
truth is never fed into the C production initializer, phase solver or prior.
Together with pixel-only refit recovery, this separates coarse-grid spacing
from centroid/phase/codec faults in these particular clean synthetic cases.
All20 unsupported rotations are FOV5mm,96px; the100-dot policy did not shrink
them to80px. Increasing that cap alone does not repair them.

## Diagnostic integrity

`diagnose.py` uses instrumented copies in this directory and verifies each
output status equals frozen V2. It reconstructs the exact132 frames from V2's
parameters and checks every raw-pixel SHA256. `results.json` retains every
point, crop, stage counter and separate `oracle_diagnosis_only` block. The
unmodified V2 source files in `snapshot/firmware` preserve original hashes;
`roi_opt_instrumented.c` is explicitly a different diagnostic source.

No rejected frame reaches code validation in this set: failures occur before
a complete candidate window exists. This does not mean codec ambiguity or
false detections cannot occur in real/corrupted images; separate negatives
remain required.

## Alternatives actually tested

1. **Near-neighbor vector histogram, then continuous refit.** Inspired by the
   original PC `vision/grid_fitter.py`: estimate basis from nearest-neighbor
   vector modes, estimate phase, subtract fixed directional offsets and refit.
   A bounded simplified8-peak prototype frequently chose diagonal or shifted
   neighbor clusters (only7/36 fractional and19/96 rotated proposals decoded).
   It is not adopted as the production initializer. Its failures are retained
   in `prototype_results.json`; no truth fallback hides them.
2. **Denser brute-force angle/pitch scan.** Not implemented: halving angle and
   pitch steps would roughly quadruple already expensive cold hypotheses,
   while arbitrary continuous scales would still lie between samples. It
   also cannot create an unobserved6x6 window. No real-time budget supports it.
3. **Reuse existing coarse geometry as bounded initializer, refine continuously.**
   The adopted V3 slice still checks all original26,901 models. It captures all
   coarse candidates in a global geometric initializer envelope, refits each
   using all current points and validates every result using the original
   strict gates and coordinate consensus. No decoded codeword guides fitting.
   >64 captured seeds rejects; it never truncates or returns the first success.

The initial diagnostic initializer envelope RMS.08 excluded eight true basins
whose nearest coarse model accumulated .08–.11-cell error across the ROI.
This was **not an acceptance threshold**. The final initializer envelope is
RMS<=1/8 cell, major<=.45, minor<=.25; it accommodates finite coarse-parameter
error across a small ROI. Its coverage is empirical, not a proven global
convergence guarantee. Final acceptance stays major.10.. .30, minor<=.065,
unique cells, complete6x6, actual codec, and all-found-model agreement.
Both envelope experiments are preserved. V3's independent held-out images
provide evidence beyond those used for diagnosis, not universal reliability.

## PC reference, deliberately not copied wholesale

Read pinned upstream `digital_pen_ov5640/pc/src/digital_pen/vision/grid_fitter.py`,
`grid_refinement.py`, `dot_detector.py`: PC basis uses near-neighbor modes;
phase uses residual clustering; projective fitting performs robust assignment,
directional-offset removal and refits; local models may join tiles and spline
warps. Photometric grid refinement can replace/synthesize fitted sources.
V3 adopts only the **all-point fixed-offset/continuous-refit concept**, with an
analytic two-by-two orthogonal solution. No OpenCV/NumPy runtime dependency,
RANSAC outlier dropping, homography, spline, photometric repair or missing-dot
addition enters C. Python/NumPy already available are diagnostic tools only.

## V3 result and resource budget

See sibling `smart_pen_continuous_roi_v3_candidate_20261029/verification/CONTINUOUS_V3_REPORT.md`.
The340-frame sweep changes exactly35 statuses:19 fractional and16 rotation
NO_GRID become correct OK. No prior successful/rejected category changes;
20 no-window views remain NO_GRID. All253 accepted outputs have correct
symbols, observed support and independent synthetic transforms.

Workspace32640B =21888 core+9216 crop+1536 seed storage, <=32KiB. Cold hypotheses
stay26901; additional strict models<=64 and all-point refit iterations<=320.
Main340 actually use at most15 seeds/75 iterations/15 refined model checks.
Phase computations during refit and extra capture scoring are additional CPU
work, not represented by candidate count alone. No S3 execution/timing exists.

`paired_cpu.py` compares eight alternating V2/V3 calls per fixture under the
same host compiler, recording process CPU as well as wall time. Observed
median CPU ratios range0.80..1.21 and are environment/compiler dependent;
**no speedup or real-time claim** follows. Raw paired data is retained. The
same original cold search dominates; small fixed workspace is not evidence
of60FPS. A later target benchmark variant and actual hardware measurements
remain separate gates.

## Reproduction

Use only the existing host venv; no installation/network step:

```sh
cc -O2 -std=c11 -shared -fPIC bridge.c snapshot/firmware/codec/anoto.c -lm -o diagnostic.so
PYTHONDONTWRITEBYTECODE=1 ../smart_pen_host_venv_20261028/bin/python diagnose.py
cc -O2 -std=c11 -shared -fPIC seed_bridge_envelope.c snapshot/firmware/codec/anoto.c -lm -o diagnostic_seeds_envelope.so
PYTHONDONTWRITEBYTECODE=1 ../smart_pen_host_venv_20261028/bin/python evaluate_coarse_refine_envelope.py
PYTHONDONTWRITEBYTECODE=1 ../smart_pen_host_venv_20261028/bin/python paired_cpu.py
```

Run reproductions in a separate copy to preserve this evidence snapshot.
Compiled`.so` files are disposable host outputs, not publication deliverables.
No original/V2 files, application VALID path, hardware or remote repository
were modified by this diagnostic work.
