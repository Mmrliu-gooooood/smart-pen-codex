# Twenty-ground recovery — independent experimental native

2026-10-30. **NOFAB / NOPOWER / independent review pending.** No source, component, footprint, rule, layer-stack or old copper change. All JP commissioning states and provider NULL remain unchanged. This is a bounded GND-only successor to independently checked0745, not a completed pen or fabrication release.

## Exact delta

Parent0745 PCB SHA `3276f04433c8ee3759f963fdc133200aee0b398ec6009e31a82fd595ab2f4328`.
Candidate PCB SHA `abd8a388a606582e80ebe5f59da7579f7020cd44be6af494e032b8f69fde8ca0`.
Model `docs/electronics/ground_recovery_plan_0807/selected20_final.json`, SHA `0eff8ad9adbcb5ad77e16f09ebf352cf72d478f4f64df8eed1aacfd687159274`.

Add28 copper objects:22 F/B ground tracks, all0.3mm, and6 through vias0.45/0.2mm. Retain all1,201 old objects; total1,229. No In1/In4 or In2 signal routing, no source changes or component moves, no new devices. Final GND targets:

`R216.2 R214.2 R224.2 R228.2 R230.2 R231.2 R225.2 R226.2 R227.2 R220.2 R206.2 R233.2 R234.2 R232.2 R221.2 R222.2 J104.3 R223.2 R235.2 R237.2`.

R104.2 RF-end GPIO45 strap ground, all six J202 grounds and R229/R218/R219/J105/J107 grounds remain explicitly unresolved. R235.2 ground is connected, **not R235.1 clock bias**. No other resistor signal terminals, NC outputs or camera-control nets were altered. U205/C209 protected area remains untouched.

## Real evidence

- Actual ERC **0 errors /1 inherited dangling VBUS_5V warning**.
- Actual all-track/all-severity/schematic-parity DRC **0 violations /76 unconnected /0 parity mismatches**. Old0/96/0 reduces by exactly20; no claim all USB/boot/control or power return is complete.
- Actual finite-copper cores: **AON41/41**, **GND91/103**, **SENS12/12**. All prior physical components, every old footprint pose/pad/net and old track/via geometry retained. All20 targets verified in core, all12 excluded grounds still singleton components.
- All actual new via annuli versus every physical pad on every copper layer, including same-net pads: **0 overlaps**. Finite foreign-copper, actual drill, outline and rule-area checks pass.
- All retained signal reference projections compared with actual refilled normalized plane polygons: **0 additional loss**. Actual plane erosion and merged-hole reports remain numerical research checks, not SI/EMI or current/thermal qualification. Inherited clock0.0017414094705mm² per In2/In4 and CAM_ON0.001488810274mm² In1 losses remain.
- Twenty real native cuts, each refilled and run through physical graph + real DRC. All non-GND components preserved, including pressure/STRAP/IMU/I²C/head clock.17 cuts yield0/77/0; three shared-via/branch cuts yield1/78/0 with the single exact predicted dangling UUID, not a blanket warning waiver. R224 cut leaves R224+R228 together as one floating island. Shared dependencies and exact lost sets were declared before tests; see `NEGATIVE_TESTS.md` and declaration.
- Normal/`-O` cut output byte-identical. Verification and physical reports likewise match. No correctness relies on removable Python assertions.
- Independent reconstruction: all54 native files byte-identical. Actual inverse unified patch restores parent54 files byte-identically; real rollback DRC0/96/0. Only PCB differs in `native_forward.patch`, not a hidden source change.

## Layout refinement and remaining DFM / mechanical gate

The first local plan was improved rather than accepting13 courtyard overlaps. The selected final geometry removes the proposed U202-body via by reusing R220's ground branch; R234's via is moved clear of its courtyard. All old copper remains complete; no same-net pad-overlap shortcut.

Only one **new** courtyard intersection remains: shared J104/R223 via(9.35,57.25) intersects `SmartPenInterfaces:Probe3_P1.8_NoPaste` probe-access rectangle. It is not an approved fitted-connector body. Actual J104.3 is a1.0mm circular B.Cu/B.Mask pad without paste. New via annulus0.45mm and drill0.2mm have **0.1942388mm nominal copper-edge separation** from that pad; the probe copper itself is neither overlapped nor shorted to another net. `probe_access.json`, `probe_detail.png` and `group_views.png/svg` show the actual geometry.

Remaining: probe tip size, placement tolerance, fixture/enclosure approach, contact force, soldermask expansion and via tenting/registration/process capability. Default CAD mask/tenting intent is NOT proof of actual manufacturing process. No via-in-pad waiver or assumption of copper filling. Existing parent courtyard/EP/thermal/mechanical gates remain, even though this group adds only one such new intersection.

Outline remains x0..14,y−6.5..95mm (14×101.5mm); no mechanical enlargement or component move. This is not shaft diameter/3D body/weight/thermal approval. RF R104 and tail J202 require separate evidence and are not hidden inside this version's progress count.

## BOM transparency

`checks/candidate/bom.csv` now explicitly exports both **MPN** and **MPN_candidate**, avoiding the previous export's blank candidate fields. `bom_qualification.csv` adds conservative derived status and NOFAB/NOPOWER. The source fields themselves are unchanged. A candidate part is not automatically promoted to approved/available/purchased/qualified MPN. Existing MPN identifiers also do not establish manufacturing release; no quote or380CNY total-cost certification.

## Reproduce / files

Use `/usr/bin/python3` with pcbnew9 and `kicad-cli`, GNU diff/patch. Materialize from the hash-pinned final model, run `run_checks.py`, `verify.py`, `physical_native.py`, `negative_ground.py` normal and`-O` sequentially, `replay_rollback.py`, `probe_access.py`, `export_bom_status.py`, `render_group.py`. Set `GROUND_NATIVE_OUTPUT` for independent reconstruction; do not edit frozen inputs.

The only legacy0130 helpers imported are read-only `finite_copper.py` and `native_polygon.py`, pinned in dependencies; historical0130 `plan.py/plan.json` are neither imported nor executed. The separately reported historical diagnostic UUID drift is not silently repaired or used as a source of geometry.

Manifest excludes regenerable full negative/replay/rollback native copies but includes actual test DRC reports, hashes, inverse patch and reproducible scripts. Negative boards are intentionally broken test specimens, not candidates. No upload, procurement, power or fabrication performed.
