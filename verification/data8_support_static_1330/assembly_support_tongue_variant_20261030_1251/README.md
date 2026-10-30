# Raised head-tongue exploratory successor — NOFAB / NO POWER

Separate from frozen first proposal (`assembly_support_proposal_20261030_1238`, manifest d79df91e37b18b61a2f6b7c0939b5583df83e42ddc4c24fd59106272ffee3bbb) and its frozen zero-J202-margin diagnostic supplement (e3c7fc39272c6036d262c73fa27622201fbd49887462fc410f00e63c644b2dca).

## Exact changes
Preserve accepted dcbd 99.8 mm outline, transform and full .93 mm thickness; do not alter any component envelope or six operation gates. Same right lateral finger Z131→119 and same source-sized additional pockets/secondary catch as prior connected proposal. Preserve old catch material to avoid severing its legacy structural junction.

ACCESS head tongue: X[−7.2,−5], Y[B+.2,B+.6], Z[31.5,33.7]. Same .4 mm height and2.2 mm X span, raised .2 mm relative to first trial. It overlaps surviving old head-root height rather than floating above it. Final source actual head face was Z31.75, not inherited nominal32.

RevD bench: **retain original common base unchanged**, fuse only tongue X[−7.2,−5], Y[B+.2,B+.6], Z[30.5,33.7]. Do not extend the old full-height post into J202's service budget. RevD is an external bench fixture, not a pen enclosure.

Purpose: preserve nominal board-face contact while obtaining .2 mm geometric separation from J202 full budget Y≤B. This is an exploratory design margin, NOT manufacturer/tool/FPC/process qualification. Actual whole-part nearest distances and full-budget checks are required; do not infer clearance from zero common volume.

`patch_supports.apply` acts only on caller-owned synchronized derivative docs. Build/export via `test_exact_contexts.py`; `test_contacts.py`, `check_preservation.py`, `check_preserved_interfaces.py` and `clearances.py` provide reproducible evidence. Only `corrected_connected/` contains generated candidates. No historical frozen source edited.

## Native geometry evidence
- Modified parts valid and **one solid each**, with no positive-volume collision against any of104 installation solids or other mechanical parts. Board and all104 solids preserved by symmetric-volume/bounds comparison (103 retained contracts).
- Actual coplanar board/head-face area is **.8 mm² in each of the three derivatives**, measured across the entire .93 board band, not clipped to the former lower head band. Head distance0, common solid volume0.
- Actual added-tongue / surviving-source root overlap: **.242 mm³** in ACCESS19/20, **1.32 mm³** in bench. ACCESS overlap happens to equal the first trial because final source anchor/root geometry extends into the raised Y band; no assumed halving or strength conclusion.
- Three primary B patches remain **.5 mm² each**, right lateral toe distance0, secondary catch gap.1 with.5 mm² projected footprint, tail toe distance0. All six unqualified operation Evidence records unchanged. Both anchor channels and final front tool channel remain void before/after.
- All four retainer states remain valid single solids, same source deflection dimensions; only second lateral station moved. No dynamic/insertion/probe/solder/FPC/material/process waiver.
- STEP reopens valid with matching solids (bench164, ACCESS137 each). Exchange residuals are approximately −.000005793/−.001299177/−.001082523 mm³, explicitly nonzero and within .005 mm³ serialization bound. Native BRep—not STEP tolerance—determines contact values.

J202 full operating budget is never reduced: raised tongue targets **.2 mm nominal separation**. `clearances.json` reports exact full-part minima and all104 distances for each changed part. The inherited ACCESS19 upper-cover/C103 distance .0679812684 mm remains an uncertainty/process gate, not a newly granted practical clearance.

Final whole-part distance test: every changed part versus every104 retained solids (7×104) completed; **no touching installation envelope**. J202 distance is **0.20000000000000018 mm** from bench base and each ACCESS lower. Frame/J202 remains .5222307919. ACCESS19/20 upper/C103 margins were independently measured equal before/after (.0679812684/.5679812684), not presumed unchanged from placement. Normal and optimized explicit result gates pass. The .2 mm value is nominal exploratory clearance, not a manufacturing tolerance stack or qualified insertion path.
