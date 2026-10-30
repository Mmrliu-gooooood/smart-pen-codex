# 14 mm mainboard prelayout mechanical gate — FAIL current stacked19 mm screen

2026-10-28. **NOFAB. Do not begin large-scale routing on the assumption that the previous19 mm shell still fits.** No source PCB was modified. Numerical comparison only; no new final outer diameter is selected.

## Authoritative input and datum

`hardware/mainboard_width14_preplacement/mainboard_revD.kicad_pcb`, SHA256 `f27cd35dcaf51fd33078b60a7029f6f63fba9c58f1d2791488e8a1721330080c`:79 native footprints, actual F/B side and fabrication/pad bounds extracted. Not the earlier78-footprint proposal. J109 is now present, with copper-pad outer X12.3..13.7 and sourceY18.3..24.9. Its proposed wire+solder envelope is2.0 mm **above the F copper face**, without adding another0.15 solder allowance.

B-side substrate face is fixed at chosen penY. Front surface isY+0.93; therefore at previousY2.74 J109 top is5.67. Treating2.74/2.9 as a centre plane and adding half-thickness silently would produce a different, incorrect assembly. Backside R105/R214/R220 use the1.3 body +0.15 solder sensitivity bound. R112/R113 use the requested1.0+0.15; known package maxima remain; AE101 uses maximum1.4+0.15. Other unknown bodies use1.3+0.15. Fabrication/pad envelopes are conservative prisms, not exact manufacturer3D solids; courtyard lines are not treated as physical bodies.

J106/J107 actual connected-wire shapes and final service-connector heights are still unqualified. The generic placeholder for these items is not evidence of a finished harness. Any passing fallback below is conditional on completing those geometries and the remaining missing schematic parts.

Right extension starts sourceY6 and reachesX14, while the upper RF end remainsX12. The optional left RF extension toX−1 overY1..7 is **only an additional outline hypothesis**, not an already integrated RF layout. It overlaps the right extension forY6..7. Every case uses one fixed global transformX=sourceX−offset for the entire board, never a different centre at each axial section. Separate axial positions still share the same cylindrical shell.

## Budget used for the gate

19 OD /1.2 nominal wall gives8.3 nominal inner radius. Worst+0.1 wall and0.2 outward assembly/bow leave an8.0 radius bound. Requiring an explicit0.10 residual gives maximum represented radius**7.9**. OD tolerance is unspecified. These are conditional design-screen assumptions, not qualified manufacturing tolerances.

The14×4.15 power budget remains X±7, Z82..127. The mainboard's backside component lower plane isY−1.45. Power top followsY−1.45−0.30, preserving0.30 nominal spacing and0.10 after the stated0.20 relative-spacing loss. Mainboard and power radial positions were optimized together; space was not gained by reducing this gap.

## Optimized stacked results

All requested variants fail the19 mm residual screen. Numerical Y search resolution0.001 mm is calculation resolution, not manufacturing accuracy.

| Optional left expansion | Fixed X offset | J109 sourceX | Main B-faceY | Maximum radius | Limiting envelope | Worst radial remainder at19 | OD for0.10 remainder |
|---|---:|---:|---:|---:|---|---:|---:|
|no|6.0|13.0|0.902|8.6012|power|-0.6012|20.4023|
|no|6.0|12.5|1.324|8.3630|power|-0.3630|19.9260|
|no|6.5|13.0|1.324|8.3630|power|-0.3630|19.9260|
|no|6.5|12.5|1.718|8.1544|J109|-0.1544|19.5088|
|no|7.0|13.0|1.718|8.1544|J109|-0.1544|19.5088|
|no|7.0|12.5|1.988|8.0190|R240|-0.0190|19.2381|
|yes|6.0|13.0|0.902|8.6012|power|-0.6012|20.4023|
|yes|6.0|12.5|1.324|8.3630|power|-0.3630|19.9260|
|yes|6.5|13.0|1.324|8.3630|power|-0.3630|19.9260|
|yes|6.5|12.5|1.718|8.1544|J109|-0.1544|19.5088|
|yes|7.0|13.0|1.387|8.3288|outline_left_addition|-0.3288|19.8575|
|yes|7.0|12.5|1.387|8.3288|outline_left_addition|-0.3288|19.8575|

The best of the requested no-left-extension cases is offset7 /J109X12.5, but its optimized radius8.019 exceeds even the8.0 non-penetration budget. It would require about19.238 mm to preserve the explicit0.10 remainder. **This is not permission to choose19.238/20 mm**; it demonstrates a redesign requirement. Moving J109 still farther inward does not improve this case because left-edge components including R240 become limiting.

At unchanged mainY2.74 and offset7, J109X13 gives radius~8.777; moving toX12.5 gives~8.402. Both exceed the nominal8.3 cavity even before tolerance allowances. A misleading board-centre interpretation had understated this height; this report uses the actual B-face convention.

## Necessary adjustments if continuing the stacked19 mm branch

A diagnostic no-left-expansion configuration uses global offset7 and mainB-faceY2.240, power bottomY−3.660. To stay inside radius7.9:
- Power requires mainY≥2.23803.
- J109 centre must be at or inside sourceX**12.27337** for the same2.0 height envelope; X12.25 is a numerical trial, not an electrically approved move.
- Multiple left-edge component envelopes also need inward movement or qualified lower heights. Moving J109 alone is insufficient.

At Y2.240/J109X12.25 the following necessary source-coordinate limits result. These moves have **not** been checked for electrical spacing, fanout, return current, new component collisions or routing. They are inputs for a new prelayout gate, not edit instructions that override an electrical review.

| Reference | Current minimum sourceX | Required minimum sourceX | Minimum rightward translation |
|---|---:|---:|---:|
|R221|0.2750|0.5918|0.3168|
|C103|0.5750|0.5918|0.0168|
|C203|0.5250|0.5918|0.0668|
|R224|0.2750|0.5918|0.3168|
|R233|0.2750|0.5918|0.3168|
|R104|0.5250|0.5918|0.0668|
|R218|0.2750|0.5918|0.3168|
|R210|0.2750|0.5918|0.3168|
|R228|0.2750|0.5918|0.3168|
|C201|0.5250|0.5918|0.0668|
|R236|0.2750|0.5918|0.3168|
|R240|0.2750|0.5918|0.3168|
|C205|0.5250|0.5918|0.0668|

The optional left extension is excluded from this diagnostic adjustment list: offset7 makes its left board edgeX−8 and introduces a different outline limit. SourceY overlap/antenna matching geometry must be resolved jointly rather than calling it a default15 mm board or independently re-centering each region.

## Alternative: separate power axially instead of stacking

A conditional mainboard B-faceY−0.5 maintains0.30 nominal vertical clearance above the required contact-cassette topY−0.8. The bare refill ends atZ67; the contact budget endsZ80; current backside components are farther back. This is a geometric budget, not a completed contact mechanism or support design.

Power is returned toZ192..237 and USB toZ239..259, restoring the260 mm length comparison rather than213. Camera/refill/battery assumptions and all missing full harness/fastener/RF details remain open.

| Optional left expansion | Fixed X offset | J109 sourceX | Largest radius incl separate power | Worst radial remainder at19 |0.10 screen|
|---|---:|---:|---:|---:|---|
|no|6.0|13.0|8.0743|-0.0743|fail|
|no|6.0|12.5|8.0156|-0.0156|fail|
|no|6.5|13.0|7.5990|0.4010|conditional pass|
|no|6.5|12.5|7.5166|0.4834|conditional pass|
|no|7.0|13.0|7.3011|0.6989|conditional pass|
|no|7.0|12.5|7.3011|0.6989|conditional pass|
|yes|6.0|13.0|8.0743|-0.0743|fail|
|yes|6.0|12.5|8.0156|-0.0156|fail|
|yes|6.5|13.0|7.5990|0.4010|conditional pass|
|yes|6.5|12.5|7.5166|0.4834|conditional pass|
|yes|7.0|13.0|8.0156|-0.0156|fail|
|yes|7.0|12.5|8.0156|-0.0156|fail|

Without optional left expansion, offset7's separate-power configuration is limited by the power radius7.3011; even18 OD would retain0.1989 under the same radial allowances. With the left outline expansion, offset6.5 permits the19 mm conditional screen; offset7 does not. Neither is a selected prototype design, and the added47 mm length is a substantial ergonomic tradeoff.

## Reproduction and release boundary

Run `extract.py`, `screen.py`, `followup_options.py`, then `verify.py` under normal Python and `-O`. The extractor aborts if the native PCB hash changes. Checks cover79 footprints, native J109 bounds, correct B/F thickness, fixed coordinate transforms, preserved board spacing, all failing stacked cases and explicitly conditional axial alternatives.

No routed candidate, housing CAD, procurement, board order or manufacturing approval was changed or issued. Re-run actual full native component and harness checks after any layout, height, thickness, antenna or centering decision. Keep the prior18/19 studies as historical alternatives rather than silently inheriting their results.
