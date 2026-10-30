# V3 continuous-fit research slice

V2 and original opt worktrees remain frozen. No push, app integration, physical
nib VALID, tilt, camera or S3 real-time claim. V3 retains V2 pixel ROI/edge policy.

Diagnostic evidence: every fractional-scale rejection died at coarse geometry
residuals despite correct detected directions and complete observed windows.
Of36 rotated rejects,20 lacked any complete observed6x6; only16 can be repaired
by fitting. Applying original phase estimation to render geometry ONLY in
post-hoc analysis passes all132 scale/rotation probes. That truth never seeds
this algorithm. Blind nearest-vector modes were unstable; not adopted.

V3 keeps every original26,901 coarse model and the original strict validators.
During the same current-pixel coarse pass, collect geometrically plausible
initializers (all points, major<=.45, minor<=.25, RMS residual to a1/6-offset
cross <=1/8 cell). These are a capture envelope ONLY, not acceptance gates.
Coarse angle/pitch errors accumulate across the finite ROI, motivating a wider
initializer basin than the final .10.. .30 major/.065 minor acceptance gates.
No calibrated coverage guarantee is implied by the envelope. Collect ALL
qualified coarse seeds: >64 immediately rejects as AMBIGUOUS; never truncate
or choose the first successful model. Store3 doubles/seed in caller scratch.

Each seed gets at most5 iterations: phase/current-pixel cell and direction
assignment; form nominal cells plus their fixed1/6 directional offsets; fit one orthogonal,
nonuniform affine basis by an analytic2x2 principal-axis solution using every
point. Do not discard outliers, synthesize points, or use decoded symbols to
fit. Degenerate/nonfinite/out-of-range refinements are discarded; the retained
old coarse hypotheses still participate. No shear/projective model is added.

Every refined model is revalidated with unchanged original residual, distinct
cell, complete-window, codec and cross-model consensus checks. A conflict or
seed overflow rejects even when an earlier model decoded. Success means only
finite explored model consistency, not uniqueness over all continuous models.

Workspace adds1536B (64x3 doubles), totaling32640B <=32KiB; original128 core
points and36..100 wrapper policy remain. Cold candidates<=26901+64, refinement
iterations<=320. Phase evaluations within those iterations cost more than the
candidate counter alone shows. Report actual seed/iteration/model counts and
host CPU; target timing remains unqualified. No heap/recursion.

Original opt API/result/workspace ABI and search behavior stay intact. V3's
separate continuous result appends refinement telemetry and requires its own
matching header/binding; never cast it into V2 or the app mapper ABI.

Optional diagnostic counters deliberately overwrite on failure; result/transform
do not. Diagnostics, result, transform, seeds, input, config and workspace must
not overlap. Finite captured-model agreement is not global continuous uniqueness.
