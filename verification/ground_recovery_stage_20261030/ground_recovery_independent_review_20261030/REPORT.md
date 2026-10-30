# 0818 twenty-ground recovery — independent review

**Bounded GND routing claims reproduce; NO FAB / NO POWER remains.** This is a20-connection improvement, not a completed pen or dynamic/supply-sequence qualification. All commissioning jumpers remain OPEN, firmware provider NULL.

## Identity and scope
- Candidate PCB `abd8a388a606582e80ebe5f59da7579f7020cd44be6af494e032b8f69fde8ca0`.
- Frozen199-entry manifest `d034dfd57630c6c0d3b44527e8142a2ceaa86b904c20c82117a9c2840e277858`: all match.
- Parent0745 manifest168 entries and0807 plan manifest23 entries match. Selected model `0eff8ad9adbcb5ad77e16f09ebf352cf72d478f4f64df8eed1aacfd687159274` pinned. All8 explicitly pinned dependency files match, including read-only finite_copper/native_polygon.
- Original files unchanged at terminal rehash. No source/FP/rule/old-copper changes, remote writes, purchases, bridges, fabrication or power operations. All mutating tests confined to an isolated copied tree.

## Fresh actual checks
KiCad9.0.2 all-track/all-severity/schematic-parity DRC: parent **0/96/0**, candidate **0/76/0**. ERC zero errors/one inherited global_label_dangling warning. No hidden rule suppression. Fresh finite-copper core graph: **AON41/41, GND91/103, SENS12/12**. All20 named ground targets enter the core and all pre-existing components are preserved. Schmitt protected local area/control source unchanged.

28 added copper objects:22 F/B tracks0.3mm and6 through vias0.45mm/0.2mm drill;1201 retained,1229 total. A separately written balanced-block parser confirms every old copper and footprint raw block byte-identical, with exactly28 added blocks. Independent native-tree hashes show **PCB is the sole changed file**. No component/source/rule changes are hidden by equivalent net names.

Fresh all-layer finite checks report zero pad overlap for all6 vias, including same-net physical pads; foreign copper/drill/outline/rule-area checks pass. These nominal CAD checks do not establish fabrication tolerances, thermal/current capacity, mask or assembly process.

Separate independently written source/physical inventory cross-checks embedded lib_symbols against netlist libparts/node functions, zero mismatches, with actual physical-pad UUIDs. Separate native filled-plane computation tests **836 retained signal/reference projections**, zero additional projected loss at1e-8mm² reporting threshold. It copies raw fractured polygons, guards explicit-hole input and material-area drift, Unfractures exactly once, and uses no enlarged-hole/masked exclusions. Historical clock loss0.0017414094705mm² each In2/In4 and CAM_ON loss0.001488810274mm² In1 remain inherited; no new loss is not an SI pass.

## Remaining76 correctly scoped
The12 GND singletons still unresolved are:
`R104.2; J202.1/.4/.7/.10/.13/.17; R218.2, R219.2, R229.2, J105.2, J107.3`.

Thus76 =12 ground +64 other missing connections. R104 RF-end strap ground and six J202 grounds were not silently included in the20. R235.2 ground is now connected, **R235.1 clock-bias signal is still disconnected**. Existing clock trunk remains connected; those statements are compatible. All non-GND defects remain exactly as before. `inventory.json` contains all per-net physical components and original DRC-edge UUIDs, not just totals.

## Twenty actual cut controls — shared branches matter
Each selected target's new copper is deleted in a separate native board, refilled, reloaded, graph-checked and run through real CLI. Exact expected lost core-pad sets derive from the selected anchor graph, not a blanket dangling-warning waiver:

| Cut target | Pads leaving core | Result |
|---|---|---|
|R224.2|R224.2 + R228.2|Together one floating connected island: **0/77/0**, not78|
|R226.2|R226.2 + R206.2|Two newly isolated components: **1/78/0**|
|J104.3|J104.3 + R223.2|Two newly isolated components: **1/78/0**|
|R220.2|R220.2 + R225.2|Two newly isolated components: **1/78/0**|
|Other16 cuts|Only selected target|Each **0/77/0**|

Overall17 cuts0/77/0 and3 cuts1/78/0. Each of the3 violations is the exact predicted partner track_dangling UUID, checked by `exact_negative_comparison.json`. Non-GND physical graphs remain exactly equal in every cut, including pressure/STRAP/IMU I2C/IRQ/head clock. Normal/`-O` cut bytes match, as do verification, physical, probe and replay reports. These negative specimens are intentionally broken tests, never fabrication candidates.

Fresh reconstruction reproduces **all54 native files byte-identically**. Actual reverse unified patch against a candidate copy restores **all54 parent native files byte-identically**; rollback real DRC **0/96/0**. Patch changes PCB only. No synthetic rollback by substituting baseline board bytes. Normal and`-O` independently execute this path. `raw/completion.json` records terminal evidence.

## J104 probe-access geometry: retain process gate
Only **one new** ordinary-courtyard intersection remains, at shared J104/R223 via(9.35,57.25)mm. Existing parent intersections remain unaffected. This envelope belongs to **SmartPenInterfaces:Probe3_P1.8_NoPaste**, not an approved fitted-connector body.

Separately extracted native geometry: J104.3 is a circular1.0mm B.Cu pad centered(10.0,56.6), B.Paste absent. Via diameter0.45mm/drill0.2mm, center distance0.9192388155mm; actual nominal copper-edge gap **0.1942388155mm**. No pad/annulus copper overlap. Frozen probe-detail render visually inspected and consistent with native extraction.

This is NOT mask/tenting/fixture approval: probe tip diameter, approach, enclosure access, placement/registration tolerance, contact force, soldermask expansion and tenting/process capability remain undefined. Do not use adjacent same-net via as an alternative probe aim point. No assumption of via fill or body clearance. Whole-pen mechanical/EP/thermal/underbody gates remain.

## BOM and inherited safety limits
Fresh BOM exports both MPN and MPN_candidate. U205/C209/R202 exact candidate identifiers survive separately; candidate fields are not promoted to MPN or purchasing/qualification status. Native source unchanged. Conservative derived BOM labels are metadata, not manufacturer approval, stock/price evidence or a380CNY finished-product cost guarantee.

Ground completion does not close Schmitt0745/frozen0719/0730 dynamic gates: actual maximum five-OE+interconnect/probe load, ≤10ns/V edges at all/farthest terminals, loaded GPIO VOH and leakage/tempco/temperature, unsupported IBIS corners, AON0.65–1.65V/VIO-present startup/brownout window, reset/JTAG/hold states and whole-head backpower remain unresolved. Unknown camera, external VIO sequencing, battery/charging safety,96→76 remaining routes, firmware and manufacturing/bench authorization remain blocked. **NO FAB / NO POWER; all JP OPEN.**

## Provenance and execution limits
Supplied verifiers were read and freshly rerun, not misrepresented as independent algorithms. Additional independently authored raw-block/probe, source-inventory and filled-plane scripts crosscheck the results.

Historical0130 plan.json drift remains the previously reported nonblocking old-directory warning; it is neither executed nor imported and was not repaired. All actual pinned dependencies match. Initial isolated setup missed0744 handoff.json; verifier stopped on FileNotFoundError before a result. Error retained; copied the exact pinned dependency and restarted full tests successfully. This was reviewer setup failure, not a candidate pass or design failure; no source modification, permission bypass or uncertain mutation retry.
