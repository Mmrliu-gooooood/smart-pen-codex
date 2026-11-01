# Smallest regression-first candidate after comparison

Do not start a new projective decoder yet. The70-image comparison separates two effects: existingV3 continuous refinement recovers coarse-axis-search cases, while its fixed centralcrop loses high-pixel-pitch windows that activefull200 can see. Source/ABI/crop contracts differ; neither variant is a drop-in winner.

## Proposed bounded next seam (not implemented here)

An isolated defaultOFF **orthogonal-refinement adapter at the existing active ROI seam**, reusing the archived V3 refined core rather than adopting V3's96/80crop wrapper wholesale. Keep the original active full input quality/component checks, observed-complete6×6 requirement, input/output failure semantics and original search/cap bounds. No projective model, arbitrary crop retry, new paper geometry or real provider. This tests quantization improvement without silently removing source pixels or changing the ROI into a different ABI.

First write fixtures that FAIL the unmodified comparator where improvement is intended:
- the six recovered affine cos15/cos30 cases, all3pixelpitches, fixedδ/p=1/6;
- preserve active'spitch20/32 positive cases that V3crop lost;
- maintain every old must_reject case, especially the three V4quality-violation fixtures, before any acceptance improvement is allowed;
- include rejected offset-boundary and missing-complete-window cases, invalid inputs, full-input ink/occlusion and ambiguous/wrongpage examples.

Then minimally expose/reuse existing bounded refinement code behind a separate hostcandidate interface. Copy exact qualified source revisions/dependencies, not an unreviewed mix. Compare active, archivedV3 and candidate on identical inputs with per-case acceptance/rejection reasons; preserve unchanged original outputs on failure. If source reuse changes an ABI or workspace, state it explicitly and re-run exactsizeof/guards/aliasing tests. Do not claim old active21,888B workspace still holds refinedV3 state without measurement.

This candidate may still reject general perspective and dense continuous fullframes. Those limitations are acceptable for isolating quantization; do not loosen caps or quality thresholds to hide them. Any later perspective normalization must repair/replay the existing V4negative-quality contract and retain fullinput evidence, not branch into a duplicate unbounded model.

No activeintegration until independent review. Reject/missing/invalidframe remains GAP; no interpolation, stalecoordinate fallback or timestamp retiming across an unqualified GAP. No physicaltip, camera or IRclaim follows from hostpasses.
