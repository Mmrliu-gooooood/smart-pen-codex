# Continuous ROI: application and target gates (not integrated)

The current `smart_pen_app_pipeline_20261028` interface is deliberately **not
changed** by this research fork. `pen_app_step` still calls the old opt decoder;
its `pen_tip_mapper` receives `pen_roi_opt_result` and must independently solve
physical tip pose. This candidate is not a drop-in camera/VALID/ink fix.

## Candidate boundary

`pen_roi_decode_continuous(frame,...,&workspace,&diagnostic)` owns only image
selection, conservative bounded edge filtering, current-pixel cold decode,
and a fitted grid transform. Input canonicalization is the caller's job. The
returned integer crop is in the unchanged frame; it is not a rescaled image.
`roi.decoded.(x,y)` remains the decoded 6x6 window origin in paper cells.
The two affine matrices map the FITTED grid, not lens distortion or a nib.

V3 appends refinement telemetry to its diagnostic result (192B host ABI versus
V2 184B); use the matching V3 header/binding, never a V2 result pointer.

A future explicit application adapter must preserve original immutable frame
bytes and timestamp/frame_id/source_id, carry `pen_continuous_result` as its
own type to a calibrated mapper, and propagate every nonzero status as an
invalid observation (break an active stroke rather than reusing coordinates).
Do not cast the new result to the old callback ABI; do not multiply the
window origin by .3 mm to create a tip solution. Do not bypass contact,
`camera_qualified`, calibration revision, frame freshness, or `pose_valid`.

The mapper must know `frame = crop + (left,top)` and the integer pixel-center
convention: the center of array element [0,0] is coordinate (0,0), not (.5,.5).
Paper coordinates are continuous encoded-cell coordinates; any mm conversion
and physical tip intersection require separately validated calibration.

## Edge/ink limitation callers must retain

Only small clipped threshold-connected components may be discarded, <=24
pixels, <=6px extent, <=4px inward depth. These are empirical size-envelope
limits, **not** proof that a component is printed dot rather than writing ink.
A dot-sized ink fragment can still disappear. Result exposes counts of removed
components/pixels; success means the remaining selected ROI decoded, not that
the full frame was clean. Pixels outside it are deliberately unexamined.
No paper/pen security or anti-spoofing claim is made.

## Resource/performance gates

- Workspace: 32,640 bytes on the tested host ABI (21,888 core + 1,536 seed scratch + 9,216 copy),
  compile-time <=32 KiB; frame storage (40,000 bytes for 200x200) is additional.
- Two <=96x96 traversals maximum; 256-entry BFS queue, 128 core points,
  36..100 selected dots, no heap or recursion. Too much connected ink rejects.
- One full cold search of 26,901 geometric hypotheses plus <=64 final refined
  models, with <=320 additional all-point fitting iterations per frame;
  no warm-only uniqueness shortcut. This is intentionally not a real-time claim.
- New transform bookkeeping raises stack use even through the old opt API;
  see `verification/v3_host_stack_usage.txt`. Host `.su` values are
  per-function compiler estimates, not target task high-water measurements.
- Dedicated S3 build, runtime stack high-water, heap min-free, watchdog behavior,
  camera DMA/PSRAM contention, and real capture timing still required. Do not
  extrapolate host milliseconds into S3 FPS or silently replace benchmark v1.

## Evidence needed before integration

Real SC035HGS camera frames with validated FOV, focus, illumination, pitch,
printed profile, motion blur and handwriting; global search ambiguity checks;
coverage over fractional scales and angles (current finite sweep still lacks complete windows in20 rotated views);
calibrated lens/axis/physical nib solver including actual pen tilt; and
end-to-end invalid-observation/contact/recording safety tests. Until then keep
this candidate separate and camera qualification disabled by default.
