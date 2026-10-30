> Historical V2 design. Current V3 adds bounded strict continuous refit; see
> `continuous_refine_v3_design.md` and `verification/CONTINUOUS_V3_REPORT.md`.

# Continuous-paper ROI candidate — narrow design (2026-10-28)

Local experimental candidate only, forked from frozen vision-opt commit
`685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00`. No push, camera qualification,
physical pen tilt, physical nib pose, VALID ink, or S3 FPS claims.

## Problem and chosen scope

A 200x200 Gray8 optical field with 5–7 mm FOV/.3 mm pitch holds more than
128 dots. Raw border clipping also violates the legacy detector contract.
Do not raise the 128-dot capacity or weaken its residual/code checks.
Instead introduce a distinct API for bounded, pixel-selected central ROIs.
The original API and its strict edge rejection stay available unchanged.

Input is a canonical Gray8 frame, 96..256 pixels per axis. Independently
inspect centered 96x96 then (only on excessive component count) 80x80
crops. Threshold is (min+max)/2 in each crop. Eight-connected components
are discovered from current pixels, using the existing bitset/256-entry
queue. Remove only small border-connected components from the copied ROI:
max 24 pixels, max 6x6 bounding box, and max 4-pixel depth inward from
each touched boundary; larger components fail closed. This tightened envelope
is specific to the tested Profile-C sizes, not an ink/dot classifier. Dot-sized
ink fragments remain indistinguishable and may be removed. Revision 1 allowed
100 pixels/12x12 and incorrectly admitted 8..12px deep strokes; preserved in
verification/continuous_v1_permissive_edge, never production-approved.
Interior components retain legacy >=3 pixels, <=100 pixels and 2:1 shape
checks. Select the first crop with 36..100 retained interior components.
More than 100 leads to the smaller crop; fewer than 36, malformed blobs,
queue overflow, low contrast, or no eligible crop reject. No decoding
attempt selects an ROI; no retry follows NO_GRID/AMBIGUOUS. The 100 cap
is a conservative selection cap, not a replacement for the 128 core cap.
This policy does not promise suitability for every supported pixel pitch.

Only one crop gets a full cold decode (prior=NULL). Do not use local-only
warm success, fake geometry priors, truth-selected phases, or inferred
missing dots. All complete observed sliding 6x6 windows participate in the
existing code consensus. Evidence outside the selected ROI is not validated;
ROI success does not assert whole-frame health or ink/pose validity.

## Coordinates and API

Add an optional transform output to a new core entrypoint; leave the old
entrypoint and result ABI intact. The winning fitted model records the
pixel location of its decoded paper-window origin and both lattice basis
vectors. Pixel center (0,0) is the center of the top-left pixel, consistent
with the detector's weighted integer-index centroids (raster sample
coordinates are therefore shifted -0.5 relative to a pixel-corner renderer).

The frame wrapper returns its exact integer crop rectangle plus inverse
2x3 affine matrices: paper cell coordinates -> full-frame pixel centers,
and frame pixel centers -> paper cells. Frame = crop + (left,top), without
resizing. Paper positions and transforms are grid-model diagnostics only,
not physical nib locations or calibrated metric measurements. The model
is orthogonal anisotropic, not shear/homography/lens distortion.

## Resource and failure contract

No heap, recursion, or frame-sized scratch. Caller-owned workspace consists
of existing core workspace + 96x96 byte copy. Target <=32 KiB total workspace;
report exact compiled size. Each crop scans <=9216 pixels, component queue
<=256, two crop attempts maximum, one bounded cold search maximum.
Input immutable; output/transform untouched on every failure. No stale
state or prior accepted by the frame wrapper. Statuses distinguish argument,
component/density selection rejection, no-grid, and ambiguity.
App integration is documentation only: current pipeline expects raw opt
results and a calibrated physical-tip mapper. Do not wire this diagnostic
candidate into recording or bypass camera_qualified/map_tip gates.

## Verification gates

1. Baseline full host suite, no skipped tests.
2. API negative tests, crop selection/edge limits, immutable input/output,
   deterministic replay; ASan/UBSan and no allocation symbol check.
3. All original regressions and independent frozen audit fixtures.
4. Full upstream continuous paper Profile C: all 36 origin mod-6 phases
   with fractional origins, FOV 5/6/7 mm; exact directions, supported window,
   independent projected point/transform checks.
5. Additional rotations, fractional FOV, blur, noise, omissions, occlusion,
   random/regular fake dots, wrong section, shear/projective boundary.
   Count rejects and any false-coordinate OK explicitly; do not turn
   finite synthetic acceptance into a hardware reliability assertion.
