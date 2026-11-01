# Independent V3 comparison review

Frozen author stage `optics_v3_comparison_20261031_1759`: 20 entries, MANIFEST SHA256 `3e1b8b27b3862985b93d994eefcc6eabfd32ed7a885712cc5a5c779296a01bcc`. All verified. Source hashes match historical f92911bc bytes; reviewed original source, wrapper and harness. No author files or active code modified.

## Standards

No blocking implementation defect in bounded replay. Minor report overclaim: README_ZH says workspace boundaries checked by replay, but replay verifies C/Python sizes and allocates matching storage; it does not surround the workspace with canaries or execute sanitizers. Change this claim only via successor erratum; retain frozen run evidence. Direct/wrapped equality does not establish general memory safety. Prior-screen metadata erratum correctly fixes fixed affine offsets without changing frozen evidence.

## Spec and actual comparison

Independent recompilation/run reproduces all 70 per-case results exactly except wall time: V3 29 correct / 0 wrong / 41 rejected, against active 22 / 0 / 48. Nine recoveries (three 15-degree ideal projective, six affine cos15/cos30), two losses (pitch20/32), 20 common accepts, 39 common rejects. Source and pixel hashes remain identical. No rescaling/recentering/ground-truth pose enters C. Separate direct and passive-wrapped libraries agree on return plus all192 output bytes on all70. Failure output/input integrity checks execute on both paths.

All29 successes return central96 crop, with post-return whole-dot-square support true. 24 rejects reach96 core;17 reject before core. Pre-core crop count remains honestly unobserved. No80 fallback demonstrated by this sparse set. Source policy only tries80 after96 retains>100 components, not after decoding failure. Pixel sampling unchanged but effective FOV differs; two lost positives prevent any claim V3 is a drop-in win. Host ABI is32640 workspace/192 result, not active21888 workspace.

## Old408 negative contract

Source review confirms340 continuous+68 adversarial specifications, strict per-image SHA equality and per-case baseline status equality. Historical acceptance oracle checks exact symbols, observed dot-center support, transform error and must_reject. All50 explicit must_reject are included (43+7), all60 corrupt-code cases, and all154 historical rejects. Exact V4 forbidden edge-stroke images252/280/308 match SHA and require rejection. Legacy408 harness is trace-wrapped; direct/unwrapped equality was checked for70, NOT asserted for408. Historical oracle remains center-based; the 70-image stronger dot-square oracle does not silently upgrade it. Python assert integrity checks apply to the normal (non-O) legacy run.

## Recommendation

Minimal default-off isolated orthogonal-refinement reuse at the active ROI seam is justified as research. Preserve active full-input evidence/quality checks, caps, complete observed window, failure semantics and original search bounds; do NOT wholesale adopt96/80 crop wrapper. Require six affine recovered positives and preserved active pitch20/32 positives, all old must_reject including V4 three edge strokes, active regressions, malformed/alias/guard tests and measured ABI/workspace. No gate relaxation to improve counts. No V4/general-projective adoption; no production provider, FPS/physical-tip/IR claim; rejection stays GAP without invented interpolation.

## Final execution result and erratum disposition

Independent legacy408 rerun completed exit0:254 correct accepts,0 wrong/quality-invalid accepts,154 rejects,0 status changes; all408 regenerated pixel hashes match. All408 semantic result records match author results excluding seconds. Full20-entry author manifest still matches after review. Successor `optics_v3_comparison_erratum_20261031_1804/ERRATUM.md` was inspected and correctly narrows workspace claim to ABI/allocation-size checks; this resolves the minor report issue without modifying frozen results. Independent70 and408 logs/scripts/JSON are retained in this review directory. No further blocker to authorized isolated candidate experiment, not active adoption.
