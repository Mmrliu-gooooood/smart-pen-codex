# Actual active decoder probe — 2026-10-31

Read-only active source; new research output only. NOT camera, lens, physical tilt, or handwriting qualification. No V3/V4 code adopted or executed.

## Results

| Dataset | Correct accepts | Wrong accepts | Rejects |
|---|---:|---:|---:|
| 45 pinhole tilt/offset + 7 spacing boundaries | 11 | 0 | 41 |
| 18 affine/no-perspective controls | 11 | 0 | 7 |
| Combined finite observations | 22 | 0 | 48 |

Every accepted coordinate and all36 directions matched an independent frozen valid encoder vector (index2; section0,0; window156,51). Every rejection preserved output bytes. Wrong-accept count0 is an observation, not a probability/safety bound.

Primary52 cases: center pitch8.5714286/10/12px × tilt0/15/30/45/60deg × displacement.10/1/6/.25cell, plus pitch7/8/9/16/20/32/33 at zero tilt and1/6 displacement. All36 nonzero pinhole-tilt cases rejected; zero-tilt1/6 and.25 accepted at all three pitches, while .10 rejected. Pitch-only8/9/16/20/32 accepted;7/33 rejected.

IMPORTANT: those rejections do not establish a universal physical tilt threshold. Controls with no perspective also rejected all cos15 and cos30 anisotropy cases (six NO_GRID results). Exact searched ratios.9/.8/.7 accepted at all three pitches. Ratio cos45 accepted at10/12px, but8.571px rejected at detection. This shows coarse active search and raster/component effects matter, rather than proving perspective alone caused every failure. We did not instrument or uniquely attribute each NO_GRID failure.

## Actual executable and images

The compiled source is `publication_20261031/target_repo/firmware/vision/roi_opt.c` plus `firmware/codec/anoto.c`, called through `pen_roi_decode_opt` with prior=NULL. This matches the decoder called at active `firmware/application/pipeline.c:62–63`; it is NOT the continuousV3 wrapper. Workspace21888bytes on this host. C receives only immutable Gray8 bytes, dimensions/stride, and paper width710/height1000/section0,0; truth, angle and pitch are not decoder inputs.

Existing independent `tests/roi_opt_fixture.py` renders36 known code dots with4×4 subpixel sampling, complete disk projection, no noise, no motion blur, no lens distortion and no handwriting. All images are200×200 raw pixels. Pixel phase is fixed(100.35,99.65), so results are NOT phase/coordinate coverage. Only one isolated6×6 code patch is rendered: unlike continuous paper, it cannot supply neighboring alternative windows.

Pinhole mapping: rotation about X; Z=12mm+y*sin(theta), paperpitch.3mm, focal_px=center_pitch_px*12/.3. The renderer has yscale=cos(theta), denominator=1+cell_y*.3/12*sin(theta). Radius1/6cell=.05mm (diameter.1mm); displacement is .03/.05/.075mm. Focal pixel scale varies with selected pitch and is not a measured lens. Affine controls replace perspective with0 and use only specified axis ratio; these controls are NOT claimed physical tilt images.

No scaling/cropping into V3's96px policy occurs. Input200px with pitch10 implies6mm nominal paper coverage, not that full640pxVGA covers6mm.

## Reproduce

`PYTHONDONTWRITEBYTECODE=1 python sweep_active.py`

`PYTHONDONTWRITEBYTECODE=1 python controls_active.py`

Both compile the actual active C with native cc/O2 in an automatically removed temporary directory. No network/device operations; no active writes. They bind eleven source/input hashes and check unchanged bytes afterward. Output files belong only here. This is ordinary host execution, NOT ASan/UBSan, MCU execution, or runtime/FPS qualification. Temporary compile paths in saved commands are provenance, not persistent artifacts.

`results.json`, `controls_results.json`: per-image render parameters, exact classifications/status/output, image hashes. `summary.json`, `controls_summary.json`: source hashes, vector and counts. `run.log`, `controls.log`: fresh runs.70PGM files are actual decoder inputs. `MANIFEST.json` binds this output set.

## Recommended next bottleneck, not an automatic code change

First replay this SAME byte-frozen image set through the already-archived continuousV3 implementation in an isolated candidate, preserving its actual96/80 crop policy and ABI, to distinguish coarse-search recovery from missing-window/projective failure. Do not write a second refinement algorithm or silently replace the active decoder. V3 already refines orthogonal/nonuniform geometry but cannot be advertised as a perspective solver; report changed crop/FOV evidence separately rather than claiming a like-for-like full200px decoder comparison.

If genuine projective coverage remains necessary, repair and independently re-review the existing NOT_ADOPTED V4 experiment before adoption—not a duplicate projective decoder or relaxed residual gates. V4's three legacy edge_stroke negatives decoded correct coordinates after writing ink was cropped away; those are quality-contract violations and must remain failures until fixed. Preserve the full older negative corpus, observed complete6×6 requirement, rejected-output safety, and diagnostic failure history; do not select successful ROIs after seeing decode results to hide bad evidence.

None of this grants physical-tip coordinates. Failures must propagate as invalid observations/GAP; no stale coordinate reuse or interpolation across a GAP, pen-up, page/session change or missing qualification. Existing stable OV5640 visible-black-dot capture is a future empirical input source, not proof that these ideal SC031GS-like sampling or IR assumptions hold. No actual camera images were supplied or measured in this probe.
