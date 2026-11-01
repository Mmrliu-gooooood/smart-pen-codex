# Actual archived V3 versus frozen active-decoder probe

2026-10-31. SYNTHETIC ONLY / NOFAB / NOPOWER. Read-only original sources and all earlier optical-screen artifacts. This directory owns only the replay code/log/results. No new decoder, no active adoption, no V4 or physical camera execution.

## Result

| Same70 input PGMs | Correct coordinate+symbols | Wrong coordinate/symbol accepts | Rejects |
|---|---:|---:|---:|
| Prior active cold roi_opt on full200×200 |22|0|48|
| Archived V3 continuous wrapper, unchanged96/80crop policy |29|0|41|

20 accepts retained,9 rejections recovered,2 prior accepts lost,39 rejected by both. The9 recoveries are three ideal15deg pinhole images at nominal1/6 displacement (center pitches8.5714/10/12px) plus six no-perspective affine cos15/cos30 controls. The two lost cases are20px and32px lattice pitch: V3 returns DETECTION before calling its core, unlike the full-frame active decoder. Do not describe V3 as universally better or a drop-in acceptance improvement.

All29 V3 successes return central96×96(left52,top52), one crop attempt.17 rejects do not reach the decoder core;24 reach the96px core and return NO_GRID. The returned result stays untouched on every rejection, so the script does NOT read fictitious crop/coordinates from rejected output. For those24 core-stage rejections the passive link wrapper records actual width/height/stride at core entry. For17 pre-core failures, actual crop-attempt count is not exposed: JSON explicitly leaves it unknown. No80px core entry observed in this sparse isolated36-dot input set; this does not test or disable the conditional80px density fallback.

## Exact implementation/ABI

Source root:
`publication_20261031/target_repo/verification/continuous_v3_experiments_20261029/smart_pen_continuous_roi_v3_candidate_20261029/`

Compiled unchanged: `firmware/vision/roi_continuous.c`, `firmware/vision/roi_opt.c`, `firmware/codec/anoto.c`, with their actual headers. `tests/test_roi_continuous.py` supplies the matching ctypes FrameResult; native sizeof checks require **192B result /32640B workspace**. No V2 ABI casting. Source files/harness imports and every input PGM/results file are SHA256-bound and verified unchanged after execution.

One direct library and one host-only passive linker-wrapper library are built. The wrapper passes the original arguments and return through unchanged and records only core dimensions/refinement diagnostics. Every status and all192result bytes are equal between direct and trace libraries on all70 inputs. The direct result is authoritative. Unchanged input bytes and unchanged rejected output bytes are checked on both paths.

## Preserved sampling / oracle limits

Inputs are the exact70 previously generated PGMs under `optics_paper_screen_20261031_1752/decoder_probe/`, verified against both PGM and pixel hashes. No rerender, resize, crop override, recentering, successful-ROI selection or pose seed is performed before C. The same fixed section0,0 and code window156,51 apply. C receives pixels, dimensions, paper bounds/section only—not true pitch/tilt/origin/codewords. Truth is used only after return to score coordinates and36symbols. These are isolated6×6 images, not continuous paper, with one raster phase and no noise/motion/ink; original physical/pinhole assumptions remain in the frozen probe README.

Successful outputs additionally record an independent post-return conservative full-dot support check: project all actual dot bounding-square corners using the frozen input-generation parameters and compare to returned crop. All29 accepted images passed; minimum conservative square-support margin was2.3166667px. Positive margin is sufficient full-circle support in this ideal homography model. This extra oracle is not used to select seeds, crops or decoder hypotheses and is not a physical lens/pose qualification. Legacy408 regression is separately owned by the parent; this replay makes no claim to upgrade that older oracle or replace its negative-quality gates.

## Reproduce

`PYTHONDONTWRITEBYTECODE=1 python replay_v3.py > run.log 2>&1`

Requires existing local source/input tree, Python and cc; no downloads. Builds ordinary native O2 shared libraries in an automatically deleted temporary directory. No sanitizers, SDK, hardware or realtime/FPS claims. `summary.json` stores exact commands/source/input hashes and per-status counts; `results.json` stores active/V3 comparison, crop observability, raw transform/refinement output and postdecode support per image. `MANIFEST.json` binds this new replay output only.

## Decision boundary

These results justify reusing V3 as the next isolated software research baseline, not adopting it into the application. V3 still fits only an orthogonal/nonuniform model; it is not a homography or physical-tip solver. The nonzero-tilt recovery at15deg is finite synthetic evidence, not a guaranteed angular operating range. Do not interpolate/reuse coordinates across GAP or relax the observed-window, dot/ink, ambiguity and full negative-quality contract to obtain more passes. Any V4 projective repair remains NOT_ADOPTED until its known forbidden edge-stroke acceptances and regression gates are resolved independently.
