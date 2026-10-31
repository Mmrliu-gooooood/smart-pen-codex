# NEW RESET/PWDN service candidate — nominal mechanics only

Exact7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1 versus accepted688. Author manifest bec167d27945b9d4af03171fd7f0c457315ffc82333d178ececc6063f2f86614 frozen; all192 files hash/size verified. Independent electrical acceptance remains separate. Four intended joins: MCU49/50 and J104.1/.2 into existing control cores. No service/probe/camera-off or dynamic electrical acceptance.

Native difference:476 tracks(359 exterior/117 inner),7 vias,zero removed or changed old copper. All103 footprint/pad/net/value/pose contracts and104 retained full installation entities unchanged. Actual14×99.8 outline/native thickness unchanged; .93 CAD budget retained. No power/USB change. Whole finite exterior widths and both via faces screened against full budgets and conservative native Fab bounds; no new nonterminal occupied-envelope intrusion. Native explicit track/via prohibitions checked across actual six-layer stack. Three deliberate full-body center-via negatives and forbidden-zone negative detected.

Two U101 straight north pad-ended exits are the only full static-body intersections:49 (6.2,6.575)→(6.2,5.9);50 (5.8,6.575)→(5.8,5.9),.15F. J104 Fab/service terminal escapes are separately guarded, not included as ordinary courtyard permission. All12,494 disjoint finite/full-envelope pairs checked; minimum .15 mm at PWDN via(13.35,37.025) vs C202. That via has ordinary C202court projection .0263236263165 mm². Two R227 track/court projections also explicit. Minimum finite added copper-to-edge .325 mm. These are nominal distances, not manufacturing margins.

## Narrow J104 service screen
Actual cached B court bounds [9.005,51.805,10.995,57.795] mm. Separately test conservative historical planning rectangle [8.955,51.755,11.045,57.845], derived by +.05 each side. The latter is NOT actual cached court and NOT a measured tool/probe/operating envelope.

Only allowed added intersections are exact .15B pad-ended straight segments:
- RESET J104.1 (10,53)→(8.6,53): actual court area .158089514346 mm²; expanded planning area .165589514346.
- PWDN J104.2 (10,54.8)→(11.9,55.5): actual court area .167896642702 mm²; expanded planning area .175889462390.

Each intersection is one connected polygon from the actual matching pad center to outside both regions. No other new B track or through-via intersects either; no continuation/re-entry or net-wide exception. Deliberate nonterminal horizontal crossing intersects .2985/.3135 mm² and is classified as forbidden, demonstrating that a same-net-looking route is not automatically exempt. J104 probe/tool/commissioning accessibility, camera-off state, fixture/contact and process gates remain unqualified.

Run screen.py, keepouts.py, checks.py, margins.py, service.py, refinement.py, author_binding.py with /usr/bin/python3 and -O; reports match byte-for-byte. Every source input is snapshotted and frozen predecessors untouched.

No pose/support/outline changes: accepted saved d855 four-context geometry remains applicable nominally; saved metadata still binds d855, no new saved metadata claimed. Six unresolved operation/DNP refs remain J104/J108/JP201/JP202/C106/C107. External bench fixture is not pen enclosure. Existing print/contact/access limitations remain.

NOFAB / NO POWER / no unqualified cell / two pens CNY760. No global assembly, SI/PDN, return-plane or clock/capture qualification.

Selected752 successor independently differs from preserved6902 diagnostic at exactly one PWDN F endpoint: (10.475,56.9)→(10.462785,56.924530), no other native copper UUID geometry change. Whole final screen and service guards rerun, not assumed equivalent from a rounded contact. refinement.py proves this bounded change; plane/reference implications remain electrical evidence.
