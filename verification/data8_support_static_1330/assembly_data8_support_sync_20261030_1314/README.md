# Saved data8 / corrected-support integration — research only

Exact PCB `4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad`. **NOFAB / NO POWER. Electrical joint review remains a separate gate.**

## What is new
The earlier frozen `assembly_data8_review_20261030_1256/placement.py` already tested the two moved full bodies **in memory against the exact1251 corrected support CADs**. This package closes only the saved-artifact integration loop: four distinct editable FCStd assemblies and STEP exchanges now contain those exact poses. No historical/frozen source is edited.

- RevC source: `assembly_outline_sync_20261030_1239/RevC_exact_outline_NOFAB.FCStd`.
- Three supported contexts: `assembly_support_tongue_variant_20261030_1251/corrected_connected/{RevD_BENCH,ACCESS19,ACCESS20}_support_proposal_NOFAB.FCStd`.
- Source CAD hashes must equal the frozen data8 placement evidence. Exact native103contract comparison and final115-file hardware author binding remain in their existing frozen reports, not a duplicated research claim.
- Only full R210 and R217 installation solids move: R210 native(1.5,26)→(10.5,28), F0°; R217(1.1,21.81)→(2.5,29), F−90°. CAD translations are(+9,0,−2) and(+1.4,0,−7.19). No dimensions, heights, side or orientation budget is shrunk.
- All other shapes, exact14×99.8 stepped board, .93-mm thickness budget,104 full static entities/97refs and six unqualified-operation records remain unchanged, totaling103refs. Current4d7d hash is saved in the binding object and board property. Historical `Native_outline_dcbd...` object label is retained because the outline/datum is identical; it is not the current electrical revision identifier.

## Checks on saved artifacts
`build.py` checks exact source/native bindings; all103ref coverage; only two body changes; full-body collisions; then saves, reopens and checks every shape's dimensions/volume and all operation metadata. STEP is reimported for validity, identical solid count and explicit≤.005mm³ volume-exchange residual—not falsely exact spline exchange.

`check_saved.py` independently reopens the three supported saved assemblies, recomputes head face contacts and whole lower/base J202 clearance, checks all7changed support solids against all104 installation envelopes, and remeasures ACCESS right RF-side toe, recessed catch, tail toe and three primary B-face patches. Prior operation/tool/material gates are retained. RevC has no board-support system to qualify.

Run `/usr/bin/python3 build.py` then `/usr/bin/python3 check_saved.py` in an independent copy. For a non-mutating replay use `DATA8_CAD_OUTPUT=/tmp/chosen-output /usr/bin/python3 -O build.py`, then the same environment with `check_saved.py`. Normal and optimized geometric result comparisons exclude no dimensions or contact outcomes; generated file hashes are separately recorded in the manifest.

No manufacturer margin, finished-board tolerance, clamp strength, preload, creep/fatigue, print process, actual insertion/FPC/probe/tool motion, coupled-bank SI, cell qualification or final pen form-factor acceptance follows. The inherited ACCESS19/C103 small nominal gap remains open. Two pens/CNY760 unchanged.

## Completed saved-geometry outcomes
All four STEP exchanges are valid and preserve solid counts. Normal and independent optimized replay result/contact JSON are exactly equal. Saved head contacts are .8mm² in all three support contexts; whole-base/lower J202 gap .20000000000000018mm. ACCESS right toe and tail remain at zero intended contact gap; recessed catch remains .1mm; three primary B patches remain .5mm² each. All7support×104full-envelope distances remain positive (no touching component envelope). Moving R210/R217 does not alter these support outcomes. Minimum moved-body neighbor distance remains .455mm.

The embedded electrical-review-pending annotation records the generation state requested for this research derivative. A later separate electrical static verdict does not automatically qualify these CAD artifacts for fabrication or power, and is not silently rewritten into the source geometry.
