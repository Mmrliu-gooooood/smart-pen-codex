# MCU local power and ground clearance successor — NOFAB

**Bounded native research result, not a manufacturing release or a powered MCU.** PCB SHA77537f15c2beff27ec3098c0ccd9d3dd5cd10ac335b74c4909954f2fedcf4a24; full same-project KiCadDRC **0 violations /181 unconnected /0 parity, exit5**. Formal accepted baseline9a03 is not replaced by this partial research branch.

## Concrete change from ead39

- Restore eight whole AON subgraphs,41 original objects from9a03. Their exact identities remain in the bounded2318 plan.
- Widen ten F.Cu tracks in groups0/5/6 from0.15 to0.254mm. These are the short RTC/CPU-IO/VDDA and local capacitor branches, not a claimed qualified whole-chip power trunk.
- Restore nine0.60mm diameter/0.30mm drill ground vias for the nine physical U101.57 EP copper islands. One is relocated from(4.5,10) to(4.25,10.75), with a0.5mm-wide F ground link back to the original EP point.
- All630 prior copper objects, all102 footprints/366 physical pads, source net assignments, net domains, rule files and JP301 OPEN condition remain. There are681 copper objects:630+41+9+1. No signal or existing ground route was narrowed or removed.

The plan restored a local return network at the same time as these supply branches. It does not complete the power system: pins2/3 and other AON branches remain missing; C207.2 and C504.2 are still not core-connected. No power-up test is authorized.

## Why the first candidate was rejected

In the rejected0043 version, original EP via(4.5,10) drills into B-side capacitor C504.2. Ordinary native DRC stays0 because both are GND. The finite-copper graph's unexpected extra C504 ground connection exposed this defect. `clearance.py` checks all nine vias against every actual pad on its actual copper layers, including same-net objects; it records the rejected via/pad overlap and verifies no non-EP pad overlap in this successor.

The full C504 pad-union XY envelope is retained:2.45×0.95mm centered(4.25,9.75). The relocated0.60mm disk is nominally0.225mm away; its0.30mm drill is0.375mm away. The enclosure/body/solder budget was not shrunk to a selected copper pad.

**Open manufacturing gate:** the relocated drill fits between two top EP copper-square edges with only23.8µm nominal edge clearance. That is not a proven drill/mask registration margin. The other eight vias still lie inside EP solder lands. Filling/capping/tenting, solder wicking/voiding, stencil design, assembly inspection and thermal grounding require a real manufacturer/assembler decision and applicable package guidance. No special process or zero extra cost is assumed. If the process cannot guarantee this construction, this local layout must change before fabrication.

## Actual verification

- FullCLI includes `--all-track-errors --schematic-parity --severity-all --exit-code-violations`, with the same basename project/rules and native source. Exit5 is correctly retained for181 unconnected items.
- Normal and optimized independent finite-copper checks agree. Actual AON core terminals increase1→14/39; GND30→39/102. All nine physical U101.57 pads reach J106.3 through copper and filled reference planes. Every previously connected physical-pad component is preserved, encompassing the existing12 DVP chains and19 restored nets.
- Eight whole-AON deletion counterfactuals disconnect their terminals. Deleting all nine EP vias disconnects all nine EP terminals. Individual EP deletions can retain a pad through the new redundant F ground link; they are recorded rather than falsely required to isolate every pad.
- Four actual saved/reloaded native counterfactuals: remove all51 added objects restores ead39 exact SHA and0/203/0; remove nine EP vias plus link gives0/190/0; removeRTC group gives0/183/0; revert the via/link returns the rejected0043 board exact SHA and0/180/0. The last case is a deliberate example of a manufacturing conflict invisible to same-net DRC.
- Exact independent replay of the materialization reproduces77537f15. Native F/B comparison PNG was generated from actual pad/track polygons and visually inspected.

## Plane and return bounds

Fresh filled geometry, not old cached polygons, is used. Relative to ead39, each main GND layer loses6.417850085mm² and AON loses5.743167145mm² to the new antipads/holes; retained small GND zones do not change. Actual normalized0.25mm erosion remains one component for each plane. The guarded one-shot fractured conversion is imported from the authoritative2327v2 correction: never repeat Unfracture on an existing-hole result.

All prior signal-track nearest-reference projection comparisons show no additional loss in this model. This does not certify return impedance, continuous useful width, via inductance, load capability, RF behavior, decoupling effectiveness or temperature. The new holes and source-path geometry still need physical and power-integrity qualification.

## Supply guidance scope

The bounded source assessment `mcu_supply_path_assessment_2338` measures only0.775/1.775/0.975mm local routes; their small estimated DC drops are not current ratings. Pin46 is CPU IO supply, not a500mA-per-pad specification. The0.254mm choice follows general ESP32-S3 guidance conservatively, while SiP-specific applicability and the larger missing supply path remain open. [Espressif layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#power-supply) and [PICO datasheet](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf).

## Reproduction / exclusions

Run materialize.py, full native CLI, verify.py and -O, clearance.py and -O, then native_counterfactual.py with one of its four case names. `MCU_NATIVE_OUTPUT` selects a separate replay directory for materialization. Inputs are explicitly hashed in dependencies.json. Failed Python API exploratory outputs are not accepted verification: UUID assignment was replaced by exact native-text editing, and removal tests use exact UUID text blocks to avoid the observed PCB_ITEM ownership/segfault problem. Counterfactual native duplicates and editor.prl files are excluded from the publication manifest; the scripts recreate them. The actual reports and each counterfactual DRC are retained.

The scope stops here: no other AON/GND branches, firmware, cell, charging commissioning, procurement, PCB ordering or hardware execution changed. **NOFAB; do not energize.**
