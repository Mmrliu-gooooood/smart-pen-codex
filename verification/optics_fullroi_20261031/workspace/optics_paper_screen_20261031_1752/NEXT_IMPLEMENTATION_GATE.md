# Next isolated implementation gate (proposal, not adoption)

## Evidence-led bottleneck

Active cold orthogonal search rejects all36 tested nonzero-tilt ideal-pinhole cases in this bounded fixed-code probe, despite some purely geometric screen candidates remaining inside sampling/window support. Affine controls must be read before attributing failure exclusively to perspective: coarse pitch/axis search and phase/displacement quantization also affect acceptance. Do not declare a universal tilt limit or promote V4 to solve this.

The affine control found cos15/cos30 anisotropy rejected even without perspective, while exact search ratios .9/.8/.7 accepted across three pitches. Therefore the next smallest executable step is to replay the SAME70 frozen images through existing V3, with its actual96/80 crop policy, before commissioning new perspective code. This isolates how much coarse quantization is already solved by archived refinement.

Reuse existing code and failures rather than duplicate a new vision stack:
1. Keep active orthogonal source unchanged as comparator.
2. Reuse accepted V3 continuous orthogonal refinement/crop bookkeeping as the seed/reference, not as active production software.
3. Reuse V4 projective model, synthetic renderer, and its exact three quality-contract-violation fixtures **as failing tests**, not as an accepted algorithm. First close the evidence-loss boundary: a selected/rectified crop must not erase source ink/occlusion evidence that the existing full-input quality contract requires to reject.
4. Separate support selection and projective rectification from input-quality acceptance. Preserve source-to-ROI provenance, valid-pixel masks and all examined/unexamined regions; record what cannot be decided. No invented dots or extrapolated missing6×6 window. A successful answer or low residual cannot override must_reject.
5. Then add bounded perspective-normalized detector/refiner candidate behind defaultOFF, with finite-homography/conditioning and observed-complete-window guards. Avoid loosening current quality thresholds merely to increase acceptance.

## Required next candidate acceptance matrix

- Exact old408 contract including225correct,3previous violating accepts restored to rejection,180previous rejects; publish per-case denominators, not just aggregate accuracy.
- Existing positive/negative active and V3 regressions; missing complete window, ink/occlusion, wrong paper/page, ambiguous code, malformed input and evidence-outside-crop negatives.
- This new70-image probe as additional finite regression only; extend to independent codewords/phase/in-plane rotations and held-out perspective before any general claim.
- Split correct acceptance / wrong acceptance / rejection; compare with untouched active and archived V3. Freeze quality contract before selecting candidate improvements; no hidden tuning to held-out answers.
- No production provider, real calibration or hardware activation; no performance/FPS guarantee from desktop wall time. Report sanitizer/SDK tests separately and only if executed.
- Downstream must emit/retain explicit GAP on rejection, missing frame or unqualified pose. **No coordinate interpolation across unqualified GAP, stale-coordinate fill, or retiming to conceal dropped observations.** Any later interpolation is a separately authorized, labeled visualization policy, not measured trajectory evidence.

Stopping condition: an independent reviewer can reproduce the isolated candidate and show all prior must_reject cases remain rejected while a bounded new positive set improves. Even then it remains software research, not physical-tip/IR acceptance. If preserving evidence requires a new quality contract, pause adoption and review that change explicitly rather than replacing the old expected result.
