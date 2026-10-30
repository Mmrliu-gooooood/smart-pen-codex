# Independent continuous-ROI candidate review — 2026-10-29

## Scope and decision

Read-only review of the author's explicitly frozen source hashes, copied into `snapshot/`. No frozen baseline, candidate, hardware, GitHub or external state modified. **Do not promote this as physical nib/VALID qualification.**

The wrapper fixes the specific full-field dot-count mismatch for some synthetic views and preserves the old API on the frozen regression set. Memory traversal and failure-output contracts passed the independent checks below. However the current edge policy **can delete a stroke extending 12 pixels into the ROI**. It only limits component dimensions/area; it is not a clipped-dot classifier or conservative ink gate. This finding has been sent to the author and root for disposition before promotion.

## Snapshot

- `roi_continuous.c`: `1ffdbfe2bdaab3fa7ff9ea19741e2aa9c60d8799bcc0beceacca30860c7f724f`
- `roi_continuous.h`: `219080c18c2807366c35d60880784e3fde8bf75c2b871e0e70ee9279d143e910`
- `roi_opt.c`: `23ebd10a60167b64f5540895653c6c56ffc2b4a1aa3574728e9a57be25bf07ab`
- `roi_opt.h`: `5eb1c0340702007469ec83bb275c9a632f0ec70a423e86cf2a6346fd29b418e0`

`SNAPSHOT.sha256` and copied sources allow independent replay even if the author's candidate changes. Results below apply only to this snapshot.

## Independent tests and measured results

1. **Old API: 44/44 frozen PGM fixtures passed**, cold prior=NULL. Status and accepted coordinate oracles match baseline; all failures retain poisoned output bytes. `old_api_regression.json`.
2. **54 newly rendered positive views**: 29 OK, 25 NO_GRID, no detection/ambiguity rejects. All **29/29 accepted outputs** match exact upstream symbols and a genuinely visible 6×6 window. Zero incorrect coordinates observed among these 29; not a universal false-positive guarantee.
3. Positions are new random cells near x275–365/y470–620, fixed seed29100351, section10,2. FOV5/6/7mm, angle targets0/7/−19/32/−46/58° with ±.4° jitter, bounded noise0/5/12 and selected 3×3 box-blur cases. This is a finite interleaved probe set, **not a full Cartesian coverage matrix**. Full per-case parameters and pixels saved.
4. Rasterizer independently inverse-maps each of 4×4 subpixel samples into the continuous actual upstream direction matrix. It does not reuse author's rasterizer/selection. Physical profile C pitch/offset/radius=.3/.05/.05mm. Geometry and symbols enter only output oracle, not decoder input.
5. For each accepted view, all 36 decoded grid coordinates were projected through fitted paper_to_frame and compared with independent rendering geometry (pixel-center −.5 convention); maximum error **0.416903px** across accepted cases. Inverse roundtrips <1e−8 cells. This validates transform bookkeeping on those synthetic cases, **not physical accuracy**. Cases outside fitted orthogonal model are not certified.
6. Wrong section, excluded x paper range, excluded y range, invalid minimum paper dimension: **4/4 reject**, output unchanged.
7. Pure black, pure white, checkerboard, random pixel noise: **4/4 reject**. Central 11×11 ink, >256 connected boundary pixels, diagonal ink: **3/3 reject**.
8. Border-stroke probes: depth4/8/11/12px accepted after filtering, depth13/20/50px rejected. All four accepted windows still have correct coordinates/symbols; these are **ink-policy acceptance findings**, not false-coordinate outputs.
9. Separate native **ASan+UBSan 320/320** randomized dimension/stride negative traversal cases passed (black/white/checker/stripe/random pixel images), including workspace guards and unchanged failure output. No sanitizer diagnostic. Leak scanning disabled (`detect_leaks=0`), not claimed. Workspace31104B. This is not exhaustive memory proof or target-stack evidence.

## Finding F1: boundary ink can be erased deeply

At 200px/6mm, pitch10px, center96 crop begins x52. Injecting a 3px-high black stroke at rows93–95 from x52 through x63 gives a depth12px (1.2 pitch, .36mm in this *synthetic* scale) component that is silently erased; decoding then returns OK. Neighboring actual dots can be erased with it. The selected surviving window remains correctly encoded, but this contradicts a stronger claim that filtering only discards clipped dot fragments or never swallows deep ink.

Repro fixtures: `case_063.pgm` (8px), `case_064.pgm` (11px), `case_065.pgm` (12px); entries in `results.json`. `case_066.pgm` (13px) rejects. The implementation's stated >12px/>100pixel protection does work at that threshold; it just does not establish dot-vs-ink semantics. Author should either tighten the policy with new measured coverage or explicitly retain this as an unresolved safety limitation and not grant app-level VALID based on this stage.

## Source inspection

- Crop selection uses only current image component counts:96 first,80 only when count>100. It does not access encoded coordinates, true pitch, truth origin or decoder success to retry. No retry after NO_GRID/AMBIGUOUS. Evidence outside selected crop intentionally ignored.
- `prepare()` never stores dense points in the 128-point array. Traversal queue has256 entries, checked before enqueue; seen bitmap and crop buffers cover max96×96. A giant component fails boundedly. Full black has low contrast and fails before traversal.
- Selected count36..100; strict core retains128 ceiling. Recomputed-threshold decoded count is checked again<=100. Count loops are bounded by9216pixels; edge-pixel16bit counter cannot overflow for this crop.
- Wrapper passes prior=NULL and provides no warm-start input. Accepted results assert used_warm_start=0.
- Wrapper writes user result only at final success. Core optional transform writes only after success; old output contract unchanged. Input aliases/concurrent workspace use are explicitly unsupported by contract.
- Transform anchor uses the first decoded window's lattice indices and fitted phase; wrapper adds crop(left,top) and subtracts decoded paper origin. This avoids treating ROI origin as decoded window origin. Independent point and inverse tests support the implementation.
- No affine shear/projective/lens/nib calibration added. Original orthogonal model and residual gates still constrain acquisition. High NO_GRID rate in these new positive probes must not be hidden by the clean-axis108/108 author result.

## Reproduce

From workspace root, only this review directory is written:

```sh
smart_pen_host_venv_20261028/bin/python smart_pen_continuous_independent_review_20261029/review.py
cc -std=c11 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer \
 -I smart_pen_continuous_independent_review_20261029/snapshot/firmware/vision \
 smart_pen_continuous_independent_review_20261029/safety.c \
 smart_pen_continuous_independent_review_20261029/snapshot/firmware/vision/roi_continuous.c \
 smart_pen_continuous_independent_review_20261029/snapshot/firmware/vision/roi_opt.c \
 smart_pen_continuous_independent_review_20261029/snapshot/firmware/codec/anoto.c \
 -lm -o smart_pen_continuous_independent_review_20261029/safety
ASAN_OPTIONS=detect_leaks=0 smart_pen_continuous_independent_review_20261029/safety
```

Inputs: existing installed NumPy, frozen upstream direction matrix and 44-case baseline manifest. No download/new dependency. `results.json`, `summary.json`,PGMs,`safety.log` are actual observed artifacts.
