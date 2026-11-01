# Full-input refinement candidate: independent replay

Host-only synthetic evidence, not adopted firmware, camera qualification, nib pose, or motion continuity. `run.py` never passes renderer truth, cell origin, geometry, prior, or crop selection to C. Inputs are always the full 200×200 Gray8 images, stride200. OFF is compared against the original active cold decoder in the same native library: exact return status **and every OptResult byte** on every case. ON uses the candidate interface. No changes were made to active or archived engineering sources.

## Reproduction

From workspace root (ordinary O2 host build, **not sanitizer/SDK**):

```
PYTHONDONTWRITEBYTECODE=1 python orthogonal_refine_fullroi_candidate_20261031_1806/regression/run.py --enabled 1 --targeted
PYTHONDONTWRITEBYTECODE=1 python orthogonal_refine_fullroi_candidate_20261031_1806/regression/run.py --enabled 0
PYTHONDONTWRITEBYTECODE=1 python orthogonal_refine_fullroi_candidate_20261031_1806/regression/run.py --enabled 1
```

Each command writes only this new regression directory; native library/object files go to automatically removed temporary directories. `*_summary.json` records exact source/input SHA256 and candidate-at-build SHA256. `*_results.json` records all cases and diagnostics. Compiler implementation/configuration lives in parent-owned `../build.py`; source at build is pinned by hash rather than fabricated git provenance.

## Red/green and safeguards

`targeted_red.log` and `targeted_red_{results,summary}.json` preserve the actual enabled=1 run before ON implementation: exit1, six expected recovery failures. `targeted_green.log` and `targeted_on_*` preserve the actual run after implementation: exit0, six affine cos15/cos30 recoveries, two pitch20/32 retained accepts, three .10-cell offset rejects (11 cases). No threshold changed in this harness to make these pass.

Every call checks aligned pre/post canaries around input, workspace, output, and diagnostics. Input bytes remain unchanged; every rejected output remains the exact A5 prefill. Diagnostics are allowed to change. Bounds/alias/sanitizer unit tests are separately owned by the parent and are not implied by this replay.

## Inputs and independent acceptance oracle

- Frozen70: exact PGMs from `optics_paper_screen_20261031_1752/decoder_probe`, verified both PGM and pixel SHA against frozen results. Isolated valid6×6 patches; exact fixed truth coordinates and36symbols checked **after return**. This is not continuous paper.
- Exact408: archived V3 `verification/continuous/results.json`340 plus `verification/v3_adversarial/results.json`68. Reuses unchanged archived renderer and saved case specs, including seeded corruption/fake dots, isolated two-window controls, mirrors and quarter turns. **Every regenerated pixel SHA must equal its historical SHA**. No images are silently replaced or dropped.
- Every legacy accept must decode matching36symbols from pinned direction table, and all projected dot bounding-square corners must lie within full input with no omitted lattice dot. All50 saved `must_reject` quality negatives remain forbidden even if coordinate is correct. This is a conservative full-dot support check, stronger than historical center-only support, but not a physical visibility guarantee.
- Candidate OptResult has no full pose/translation transform. We therefore **do not claim** the old continuousV3 transform-error oracle was exercised; exact symbols/support/quality negatives are checked instead. This is coordinate-window acquisition, not pen pose.

## Semantics and limitations

V3's archived 96/conditional80 crop is deliberately NOT reproduced. Full200 input keeps all edge-touching components and uses bounded128-component core; dense continuous pages can reject before refinement. Thus historical V3 positive statuses are context, not automatically required positives for this candidate. Rejecting dense inputs is an unresolved functional limitation, not proof that continuous writing works. The full negative quality contract is retained. No inferred/interpolated coordinates across GAP are produced here.

`intermediate_off_*` is pre-ON-implementation evidence only; final `off_*`/`on_*` are the implementation review evidence. All failed subprocesses and red expectations are disclosed; no exit substitution.

## Recorded outcomes

| Dataset | OFF correct / wrong-quality / reject | ON correct / wrong-quality / reject |
|---|---:|---:|
| Frozen isolated70 |22 /0 /48|31 /0 /39|
| Archived continuous340, full input |0 /0 /340|0 /0 /340|
| Archived adversarial68, full input |1 /0 /67|1 /0 /67|
| Total478 |23 /0 /455|32 /0 /446|

ON recovers nine isolated cases without losing the active pitch20/32 accepts. The only accepted legacy case is adversarial66, nonconflicting `two_windows`. All50 explicitly labelled must-reject cases reject. **All340 dense continuous images reject in both modes**: this candidate is not continuous-paper acceptance, and its incremental isolated-patch improvement must not be presented that way.
