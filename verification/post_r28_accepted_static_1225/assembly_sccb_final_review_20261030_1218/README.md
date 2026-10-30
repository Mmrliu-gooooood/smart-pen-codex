# Exact local SCCB repair dcbd2e65 — bounded mechanical verification

**NOFAB / NO POWER.** Native `sccb_local_reference_1216/native/mainboard_revD.kicad_pcb` SHA256 **dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697**, compared to accepted8312. This is the shorter original SCCB topology plus the C301 corner and local inner PRELINK jog, not the longer diagnosticb4c41 comparison. Native0/67, reference/SI and adoption verdicts belong to separate electrical review; this package makes no dynamic or manufacturing acceptance claim.

## Exact geometry and contracts

All103 FP/pad contracts match exactly three expected rigid transforms, with other values/nets/pad sizes/shapes/layers/identities/DNP/poses unchanged:
- R240F(11,70.5),180°; full2.45×.95×.70mm retained.
- R241F(11.85,73.35),90°; full union rotated to.95×2.45×1.45mm, not narrowed.
- C207F(10.85,65),−90°; full.95×2.45×1.45mm retained.

Actual outline remains14×99.8mm. Source CAD hashes checked. Four current-context static tests replace the three old bodies simultaneously and retain all other available ledger geometry plus provisional U205/C209: **0 moved-budget intersections**. Nominal minima.55mm R240/R203,.65mm R241/R203,.93mm C207/oppositeC301/U301. Deliberate additional R240+1mm nativeY reproduces a collision with R203; no blanket collision exclusion. Known ACCESS alternate-harness/global-assembly uncertainties remain.

## Finite changed-copper screen

26 new tracks comprise **15 exterior +11 inner**, plus5vias. Inner tracks are counted but not assigned invented exterior volume. Every exterior track's full width and both-face via discs are tested against retained full installation budgets, provisional U205/C209, native Fab graphical bounds and actual courtyard polygons. **No non-target intersections** after explicit per-segment endpoint/source classification. All five discs have0 full-budget/Fab/courtyard hits.

Nominal via-to-full-budget gaps include:
- GND(12,65.775),Ø.6 →C207 .375mm.
- AON(12.05,64.875),Ø.6 →C207 .425mm, C301 .53441596mm.
- BiasAON(10.325,69.475),Ø.45 →R240 .325mm, oppositeU301 .475mm.
- SDA(6.25,67.65),Ø.45 →provisionalC209 .36296258mm, R301 .475mm.
- SDA(12.125,77.025),Ø.45 →R243 .45507353mm.

None is a selected supplier/tool/assembly tolerance allowance. Native DNP courtyard checks do not qualify commissioning operations.

## Source-junction repair, without blanket same-net waivers

The .5mm B corner is exactly **(10.9,64.875)→(11.125,65.025)→(12.05,64.875)**. Native finite polygon intersection is.039832019873mm² with fullC301 budget and.000217537407mm² with fullU301 budget. Subtraction of the **exact parent same-net B copper**, without expansion, leaves **0 new projection in both**. Faf291's.0077775877065mm² genuinely additional C301 underbody projection is eliminated. This does not imply real soldermask/underside/seating qualification.

All supply exceptions are segment-specific, enumerated in the checker/results: U204.8→C207.1→AONvia; C207.2→GNDvia; R203.2→R241.2; R240.2→biasvia; the named C301/U301 retained-source corner. CAM_SCL/SDA only use their explicit U204/R240/R241 endpoint bodies. Intersection areas remain reported, not removed. No all-AON/all-GND body exemption is used.

## Unchanged limits and next actual gate

Internal In2AON patch is explicit: zone outlines are **not** falsely called invariant. Source-side SDA foreign-hole transitions and local inner jog are electrical/reference review matters; this mechanical package neither hides nor approves them. C207 actual decoupling/return behavior, loaded edges, timing and thermal/current response require separate evidence.

98 provisional/static refs do not become103 manufacturing-qualified installations. Four DNP and J104 full operation budgets remain open; J108 remains mixed-side service, not a fictitious fitted passive. Actual preassembly service fixture/tool/stroke/runout, FPC insertion/bend, J103 strain relief/solder, materials and finished-outline≤100mm tolerance remain unqualified.15–18mm final pen target, qualified-cell absence andCNY760 two-pen budget persist. No power, manufacture, purchase or source publication is authorized by these results.

Reproduce in an independent copy: `screen.py` (normal and−O), `placement_screen.py`, `source_junction.py`. All paths are relative to the review directory; no input design is saved. Final verification/manifest bind exact native and available frozen author evidence.
