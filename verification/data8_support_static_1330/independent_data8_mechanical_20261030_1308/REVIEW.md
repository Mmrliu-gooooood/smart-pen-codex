# Independent eight-bias mechanical review

**ACCEPT exact4d7d95d2 at bounded nominal geometry scope, with explicit endpoint/own-courtyard exit classifications. No coupled-bank SI, electrical/reference, process or global assembly acceptance. NOFAB / NO POWER.**

Exact PCB4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad. Frozen mechanical manifest8613efbde985e92fc644e32a24984b32cc046c5615fd7e0200e59fa8c99b4403. Hardware whole-package manifest remains NOT_YET_FROZEN at review; acceptance binds only this exact PCB and frozen mechanical evidence. Final author manifest binding requires separate evidence, not a silent rewrite here.

## Reproduction and invariants

Independent copied finite screen and four-context placement tests pass normally and under -O. Results/placements/explicit verification JSON match frozen author exactly. Only R210F(10.5,28),0° and R217F(2.5,29),−90° change relative to accepted dcbd footprint contracts; all103 full stated contracts match expected rigid transforms. Independent additional pad attribute/drill/offset/roundrect checks match parent. Independent six closed straight Edge.Cuts confirm14×99.8mm. Reference zone definitions unchanged (not a filled-zone/SI certification).

39new tracks=32exterior+7inner,11new vias. All104 retained static budgets and actual complete courtyards/Fab graphic bounds are screened with finite copper width. No unrelated body/Fab/courtyard projection intersections. All11via discs have no full-envelope/Fab/courtyard intersections on either face; minimum reported full-envelope gap.255mm. All new front-track projections independently checked against U201 Fab bbox:0 hits. Endpoint lead/body-union/courtyard intersections stay visible, not process-qualified.

## Two narrow own-resistor courtyard continuations

Independent native finite-polygon and physical endpoint checks reproduce:
- D7 R217: actual same-net pad(2.5,28.49)→(2.95,28.95), then exact continuation→(3.55,28.975). Continuation courtyard area.011091455283mm²; full-body area0, Fab area0.
- D5 R215: actual same-net pad(3.675,28)→(4.75,28.8), then exact continuation→(4.85,29.075). Continuation outward-approximation courtyard area2.4833e−8mm²; full-body area0, Fab area0.

Each continuation is directly connected to one unique same-net pad-ended segment; neither has a pad endpoint itself. This justifies only the named resistor-exit classification—not a blanket courtyard or same-net exception. The D5 tiny value is retained explicitly rather than rounded away. Copper/mask/lead/solder/assembly compatibility remains unqualified. Native polygon ERROR_OUTSIDE50nm approximation and1e−8mm² reporting threshold remain explicit; no analytic-zero claim is made for the courtyard intersections.

## Four current CAD contexts

RevC exact outline plus three accepted raised-tongue support contexts: all104 full installation entities retained; only R210/R217 full bodies translated. Zero moved-body collisions. Nearest R217/R215.455mm and R210/R216.55mm. R210−3X negative collides with R216 and is detected in every context. Frozen CAD documents are not silently rewritten to the electrical successor.

## Remaining gates

Final hardware manifest binding; all electrical/refill/reference and coupled-bank SI evidence; endpoint copper/lead/mask/solder process; actual service/probe/FPC/tool motion; six operational/DNP envelopes; support strength/tolerance/material/preload/fatigue; inherited ACCESS19/C103 small gap; board finished-outline≤100mm tolerance; cell/final pen target. Nominal distances are not measured supplier allowances. No powering, fabrication, purchase or publication authorized.

## Frozen mechanical artifact SHA256

```
8d4c40c7b2f239c313ed6d36551a951a587d196138136c03d82b24ad40cd9f34  assembly_data8_review_20261030_1256/README.md
8613efbde985e92fc644e32a24984b32cc046c5615fd7e0200e59fa8c99b4403  assembly_data8_review_20261030_1256/manifest.json
ec6caa23c4eed38d049c027e8724c0ff48e21a8dde3abcba805b9c4aecf8c333  assembly_data8_review_20261030_1256/optimized.log
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  assembly_data8_review_20261030_1256/placement.log
78fbe862d7f6f820c138729c0c80f1bbad8ffe8c9505522ba1e1a25067132234  assembly_data8_review_20261030_1256/placement.py
b6cce12a04758f68682bbe6a02ea4a1158bdb37342f9823f7572336cd402d5fa  assembly_data8_review_20261030_1256/placement_normal.json
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  assembly_data8_review_20261030_1256/placement_optimized.log
b6cce12a04758f68682bbe6a02ea4a1158bdb37342f9823f7572336cd402d5fa  assembly_data8_review_20261030_1256/placement_results.json
b8ed5d04a90d9cb0f7a883d99cafec5a85f8fa583cd8fb86e8ba620bd6752aed  assembly_data8_review_20261030_1256/results.json
b8ed5d04a90d9cb0f7a883d99cafec5a85f8fa583cd8fb86e8ba620bd6752aed  assembly_data8_review_20261030_1256/results_normal.json
b3a52f2e406d9e7c3884cd3f7b8917fe798220b57f620f7a7796b35929132c67  assembly_data8_review_20261030_1256/run.log
03fa386e1a4ac74b0417f6c9baf0bab959559727c056b6d46fed253d14e8d907  assembly_data8_review_20261030_1256/screen.py
87bb10fa25e67dc89d13ef80e4d9d1568b2da40ab1940c2948be4b2095b4be83  assembly_data8_review_20261030_1256/verification.json
c0111caf743507ddb3d649dceeab2faa341021f8f96d55504169b37f02dd1fcc  assembly_data8_review_20261030_1256/verify.py
```

Evidence: screen/placement/verify normal and optimized logs/results, independent_exits_native.py/json for actual unique-pad connectivity and finite polygons, native_extra.py/json. Earlier mixed-library independent_exits.py trial produced no result and is not relied upon. Source/frozen artifacts unchanged.
