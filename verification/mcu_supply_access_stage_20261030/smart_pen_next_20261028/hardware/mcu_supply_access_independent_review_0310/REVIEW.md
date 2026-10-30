# Independent MCU VDD3P3 access review

**NOFAB / NOPOWER. Courtyard and short supply-escape qualification gates remain OPEN. No waiver and no release. Formal accepted 9a03 is not replaced.**

Source `hardware/mcu_supply_access_candidate_0300`,432-file manifest `e9acdb544f97f52771e6c79e7d8eeaf9ea0e4776fb3ebd18cb88d74e618f0625`; PCB `8fe809b685633dd86dddc36ec33961d61ef7fad9fca52286bc47bd72a4f614e5`. Source study28-file manifest `596bc4a249bec1d935ebc66690e262c74ac3b250a8b9db690c942e6066e8b41a`. All immutable file/dependency hashes checked before/after. No candidate edits, upload, procurement, fabrication or power operation.

## Reproduced and independent results

- Fresh bound KiCad9.0.2 full CLI `--all-track-errors --schematic-parity --severity-all --exit-code-violations`: **0 violations /134 unconnected /0 parity; exit5**. Not finished hardware.
- Independent finite physical-pad UUID graph with actual six layers, annulus minus drill and guarded raw-native one-shot zone Unfracture then all physical via drill subtraction: **AON28/39, GND61/102, SENS12/12**. Physical same-number MCU EP islands stay separate. U101.2/.3 actual PCB net AON and actual embedded schematic function VDD3P3 confirmed. C103.1 joins AON; C103.2 remains core ground.
- All780 old copper objects retained byte-geometrically; nine added objects (7 tracks,2 standard0.60/0.30 through-vias),789 total. Exact plan object geometry reproduced. Only C103 F(1.2,7.025)→(.8,7.025) and R503 B(2.5,7.5)→(2.5,11.5); orientation/package/net identities preserved,100 other FP poses unchanged. R503 is100k pressure-contact pullup, pad1=AON, pad2=NIB_CONTACT_N, not RF component. Move preserves old component relationships but does not connect its still-isolated endpoints.
- Reproduced all-prior-pad component preservation, unchanged source/rules and noncopper except exact two poses. Original schematic source is not changed to match routing. Independent SENS cross-rail and JP301 PRELINK/SW copper separation checks retain previous domains; JP301 stays OPEN.
- Both new via annuli AND drills checked independently against every actual pad on every actual layer, including same-net and relocated C103/R503: no pad overlap. Controlled via-to-C103.1 same-net drill fault detected. Reproduced new/old copper, hole/edge, rule clearance checks have no route errors.
- Normal/-O independent graph, reproduced author verification and five actual native counterfactual results are byte-identical. Exact independent replay returns8fe809; fresh-fill stability reproduced. Actual native_view.png viewed.

## Manufacturing and supply gates remain open

Actual courtyard overlaps reproduced, not hidden by DRC0: via object5 intersects U101 F courtyard0.0287694271705mm² and C103 F courtyard0.0040350770455mm²; via8 intersects C103 F courtyard0.011259537403mm². No actual pad contact does not settle package underside, soldermask, paste, tenting, registration or assembly tolerances.

Short0.25mm escape paths pin2=.775mm, pin3=.975mm remain below cited generic20mil branch guidance.0.635mm merged path≈2.170824mm and dual standard vias are geometry, not SiP transient/IR-drop/current/thermal qualification or a granted manufacturer exception. Generic recommendation applicability and physical validation remain open.

Actual post-fill reference planes, guarded normalized once and every drill removed: In1/In4 main GND each loses1.220222845666mm²; physical AON loses0.133615691533mm² despite same-net native fill not automatically representing drill voids. Each0.25mm-eroded physical plane remains one component. Reproduced F→In1, B→In4 and In3→In2/In4 prior signal projection checks find no added reference loss; this is not impedance or current qualification.

Four inherited CAD contexts/full installation budgets are hash-linked unchanged by mechanics_linked.json: C103 nominal.95×1.45×2.45mm; R5032.45×1.45×.95mm. This review verifies linkage/preservation, not an independent new whole-pen FreeCAD collision simulation. MPN heights, solder, tolerance and final assembly remain unqualified. Earlier8 MCU EP in-pad vias,23.8µm drill-edge margin, inherited.05mm gate margin, external SENS/back-power/sequence and unknown camera/battery/charging gates persist.

## Five actual native counterfactuals

Every case copied, UUID-native block removed, saved/refilled and fullCLI checked in isolated process; repeated normal/-O:

|Case|DRC/unconnected/parity|Physical result|
|---|---|---|
|Remove pin2 escape|0/135/0|U101.2 disconnected from AON core|
|Remove pin3 escape|0/135/0|U101.3 disconnected|
|Remove both supply vias|1/135/0|U101.2/.3/C103.1 disconnected; only track_dangling warning|
|Remove C103 ground reinforcer|0/134/0|C103.2 STILL connected through inherited stub; new segment is not unique return|
|Remove all9 and restore C103/R503 positions|0/137/0|Exact parent66d5343409eaf0cf58458759f033e9eea74865e1ea85b83ecc0c3068d2032141|

Independent graph omission separately checks the first four outcomes. No hypothetical result replaces native negatives. Author historical SWIG/multi-board and expected-dangling failures are in immutable author evidence; review used isolated case process implementation. Review harness initially encountered manifest-shape/path assumptions before analysis, corrected without changing source.

## Reproduction / stageability

Only review_manifest.json allowlist is this review deliverable. Native/support duplicate copies excluded. Reconstruct at hardware/<review> in same repo root; copy immutable author native/, verify.py, finite_copper.py, native_polygon.py, materialization.json, drc.json, native_negative.py, materialize.py, noncopper.py, physical.py, plan_and_planes.py, geometry.py, mechanics_linked.json. Preserve author dependencies (paths are rooted at workspace parent, including mechanical contexts). Run /usr/bin/python3 independent.py, verify.py and native_negative.py normal/-O; noncopper.py, physical.py, plan_and_planes.py; replay with MCU_ACCESS_NATIVE_OUTPUT=<review>/replay/native. Keep same-basename project/rules/source for fresh fullCLI. Do not publish whole experimental/native_negative directories as completed hardware.
