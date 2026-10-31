# Independent final7522 control/service mechanics

**ACCEPT bounded nominal geometry only.** Exact PCB `7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1`. This is not service/probe/camera-off, strength, process, SI/PDN or global assembly qualification. NOFAB / NO POWER.

## Hash-bound independent replay
Author manifest `bec167d27945b9d4af03171fd7f0c457315ffc82333d178ececc6063f2f86614` all192files verified; mechanical `767f9b90fac6214d1dc45ed15f817281f616d27770f4468c8e42025ee05ceb58` all28files; saved d855 `ff2bcd61da8522d983eb23e7874ab5ca34fdf029f09e0e45a7005a8481dbc880` all28files. Reverified unchanged after execution. Own copies ran screen/keepouts/checks/margins/service/refinement/binding normal/-O, exactly matching author outputs. Independent additional actual native sides/terminals/retained copper/via margins also match normal/-O. Frozen sources untouched.

476 added tracks(359 exterior/117 inner),7vias,zero removed or changed old copper. Only RESET/PWDN added nets; USB/PDN old conductors exact. All103 native contracts/poses/values/pad nets/sides unchanged, supplemental pad attributes/drills/offsets/roundrect checks pass. Full104 masks retain all original sizes/heights/sides/uncertainties, maximum U1017.5 included. Actual outline14×99.8/native thickness unchanged; CAD.93 remains budget.

Whole finite exterior paths and both via faces checked against full occupied budgets/Fab/actual native court polygons; no nonterminal intrusion and no via body/Fab intersection. Actual native six-layer track/via prohibitions pass; three center-body negatives and prohibited-area negative detected. Replayed12,494 disjoint finite/full-budget pairs. Only static-body terminal overlaps are actual U101.49 F(6.2,6.575)→(6.2,5.9) and U101.50 F(5.8,6.575)→(5.8,5.9), .15mm. Four exact terminal scopes including J104 Fab exits independently verified; no target-net blanket waiver.

## J104 is NOT an ordinary-courtyard waiver
Independent native inspection confirms pads1/2 are B-only and uniquely match their nets/centers. Actual polygon-vertex bounds are [9.005,51.805,10.995,57.795]mm. Separate conservative planning rectangle [8.955,51.755,11.045,57.845] is actual bounds plus.05mm—not the actual polygon and not a measured probe/operating envelope.

Only these two exact added .15B straight pad-ended segments may overlap either region:
- RESET pad1 (10,53)→(8.6,53): actual area .158089514346mm²; planning .165589514346.
- PWDN pad2 (10,54.8)→(11.9,55.5): actual .167896642702mm²; planning .175889462390.
Each intersection is one connected polygon; start at actual matching pad center inside, endpoint outside both convex regions, hence a single straight exit, not re-entry. Complete added B tracks/through-vias tested: no other overlap. Deliberate same-net nonterminal crossing (8,56)→(12,56) intersects .2985/.3135mm² and fails the exact terminal guard. This is a narrow routing geometry screen; actual probe/access, fixture/contact, service sequencing and camera-off operation remain unqualified. Missing service/tool envelopes are not silently set to zero.

## Precision correction and process margins
C202-near PWDN via(13.35,37.025), diameter .45mm: independently computed full-envelope gap **.15mm**, actual via edge gap **.425mm**. The **.325mm** global finite new-copper edge minimum belongs instead to a PWDN B track near stepped x12 edge, including (11.575,4.1)→(11.6,4.125). Initial supplemental assumption conflating these failed and was corrected before normal/-O pass. Author report's global minimum is correct.

Via ordinary C202 courtyard projection .0263236263165mm² and two R227 track/court projections remain explicit; not manufacturing/tenting/registration guarantees. J104 is separately constrained above, never covered by ordinary-court policy. Final one-endpoint PWDN refinement from6902 diagnostic was independently replayed and full final geometry rescreened, not assumed copper-union equivalent.

## CAD applicability and unresolved gates
No poses/support/fullbudget/outline change: accepted four saved d855 CAD contexts remain geometrically applicable and hashes unchanged. Saved metadata remains **d855**, not7522; no newly saved7522 claim. Six operation/DNP/tool/service gates remain J104/J108/JP201/JP202/C106/C107. Inherited ACCESS19/C103 .0679812684mm print/tolerance, provisional package/solder assumptions, actual sensor/power/camera-off sequence, battery, material/strength, return-plane/loading/ringing/coupling/timing remain unresolved. External bench is not pen enclosure. No backup/upload by reviewer. **NOFAB / NO POWER.**
