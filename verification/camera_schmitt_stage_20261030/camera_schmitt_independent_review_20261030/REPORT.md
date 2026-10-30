# 0745 Schmitt native independent review — NO FAB / NO POWER

## Disposition
**The bounded native topology, source synchronization, geometry and reproducibility claims reproduce. This is not dynamic OE qualification, autonomous safe-off approval, production DFM, maximum-load closure or permission to power/fabricate.** All 96 unresolved board connections remain. JP201/JP202 DNP/open and JP301 OPEN; provider NULL.

Candidate PCB `3276f04433c8ee3759f963fdc133200aee0b398ec6009e31a82fd595ab2f4328`; frozen manifest `c81b547513a3b815d7c619ec2ae7fc5dcf751d32d8df75333adf205113c5264c`, all 168 entries match. Source0744, parent0628, frozen0719 and frozen0730 manifests match. Tests run only in this new isolated mirror; all original files rehashed at completion. No remote writes, purchases, actual power, bridges or fabrication.

## Independent evidence and fresh execution
- Fresh KiCad9.0.2 all-track/all-severity/schematic-parity DRC: candidate and parent **0 violations /96 unconnected /0 parity**. ERC both zero errors and one inherited global_label_dangling warning. No rule suppression or project-rule replacement.
- Rerun supplied verifiers after reading their logic: **41/41 AON, 71/103 GND, 12/12 SENS**. Physical OE seven-terminal and input three-terminal components complete. Prior components preserved with explicit Q201 functional-pin replacement mapping. Unconnected source NC1 remains isolated with no trace.
- Six old copper objects removed, 15 added, including four vias; 1186 old copper objects retained, 1201 total. All unrelated footprints/pads/net/value/pose/rules preserved; R202 only retained-part value change.
- **Separate review algorithms** in `independent_inventory.py` and `independent_delta.py`: embedded lib_symbols + exported libparts/node functions cross-checked with physical pads, zero mismatches; 828 actual retained old signal/reference projections tested, no additional area loss above the recorded 1e-8mm² reporting threshold. Native filled polygons only, copied and Unfractured once with explicit-hole/material-area guards; no enlarged-hole exclusion masks. Native file differences independently enumerated: PCB, controls_sccb source, ISO symbol library, new custom land only.
- Guarded native refill comparisons preserve the historical CAM_ON In1 0.001488810274mm² and clock In2/In4 0.0017414094705mm² each as inherited gates. Zero added loss does not erase these and is not an SI proof.

## Exact source/land checks and visual inspection
U205 value SN74LVC1G14DCKR at (3,69)mm, F.Cu 0°. Pads: 1 NC (1.9,68.35), 2 ISO_GATE (1.9,69), 3 GND (1.9,69.65), 4 OE (4.1,69.65), 5 AON (4.1,68.35). Every pad **0.95×0.4mm**, row spacing **2.2mm**, pitch **0.65mm**, matching frozen official-land evidence, not the generic installed SC70 land. Engineering courtyard is not asserted to be an official TI keepout.

C209 at (5.55,68.85)mm, -90° equivalent to270°: 100nF16V X7R±10%, pad1 AON at (5.55,68.37), pad2 GND at (5.55,69.33). R202=10k1%, unchanged original0603 pads/location. Fresh source netlist contains exact `MPN_candidate` values U205 SN74LVC1G14DCKR, C209 C0402C104K4RACTU, R202 RC0603FR-0710KL. These are candidate identifiers, not a procurement-approved `MPN` export: current BOM command selects MPN, not MPN_candidate; do not mistake blank exported MPN fields for absent source identifiers or an orderable BOM.

Actual frozen source-sheet render and local F/In3/B geometry render visually inspected: NC marker isolated, bypass separately joins AON/GND, OE output reaches preserved trunk, input uses local In3 hop, no intentional jumper bridge. Visual images are supporting evidence; connectivity conclusions come from native geometry and exported source. Render is not full-body 3D assembly proof.

All four new through vias have no physical pad-copper overlap on any actual layer, including same-net. Static finite copper/drill spacing/edge/rule-area checks pass. Four **courtyard overlap records remain**: driver GND via intersects U205 F courtyard; cap GND via intersects U205 F, C209 F and C303 B courtyards. This is two via sites/four overlaps, not four pad collisions. Tenting/mask/body/process clearance and tight0.15mm input escape remain DFM gates. Historical EP/underbody/merged-hole/mechanical gates are retained.

## Actual native negatives, replay and rollback
Each cut is made on native copied PCB, refilled, physical terminal disconnection checked, and real CLI DRC run. No report-only or graph-only pretend negative.

| Cases | Violations / unconnected / parity |
|---|---|
| r203_supply, oe_pair202, oe_pair203, oe_upper, oe_middle, oe_lower, io_mcu, io_long, io_link | each 0/97/0 |
| new_oe |1/97/0|
| new_input |2/97/0|
| new_supply |1/97/0|
| new_driver_ground |1/97/0|
| new_cap_ground |1/97/0|

New negative violations are expected dangling track/via findings, not falsely reported as zero. All 14 preserve unrelated pressure, STRAP, IMU I2C/IRQ and head-clock physical components. Normal/`-O` equality and final exact counts are recorded in `raw/completion.json`.

Fresh materialization rebuilds **54 native files byte-identically**. A real generated reverse unified patch, applied to a candidate tree (not replacement with parent board bytes), restores **53 parent files byte-identically**, then real rollback DRC gives **0/96/0**. Both normal and `-O` rerun replay/rollback. See raw reports and copied actual negative specimens, replay and inverse-patch log.

## Safety boundary from frozen0719/0730
The passive-Q201 RC release mechanism is replaced, but the following remain unresolved:
1. AXC OE transition requirement **≤10ns/V** at3.0–3.6V: LVC propagation-delay CL50pF data is not a maximum output-edge specification. Five typical4.5pF inputs are not a maximum total board/probe load. IBIS fixtures/corners are not the actual five-terminal circuit, and cited model ambient range does not cover125°C. Both edges at all/farthest OE terminals, interconnect/probe loading, PVT, overshoot/current remain qualification work.
2. AON approximately **0.65–1.65V** with VIO present: AXC may be operational below LVC recommended minimum. Neither startup nor brownout/power-down safe-off is guaranteed by this static topology. External J202.23 VIO sequencing is not under an established hardware interlock.
3. Loaded GPIO VOH and leakage/temperature: high-impedance GPIO VOH and25°C leakage are not full-temperature guarantees under the10k pulldown load; R2021% excludes additional100ppm/°C tempco. Nominal divider and leakage allocations are screens, not worst-case board guarantees.
4. GPIO42/package48 source mapping is correct, but pad-JTAG/alternate high drive/hold/pull-up are unsupported; Schmitt cannot distinguish intentional enable from debugger-driven high. No eFuse changes authorized.
5. Unknown camera module, whole-head backpower, 96 gaps, charging/battery, mechanical/thermal/EP/tenting, measurement, firmware provider and manufacturing release all remain open.

Thus only a **bounded stable-AON controlled-mode experimental routing candidate** is supported; even that is not permission to energize it now.

## Provenance caveats and execution notes
The full historical translator_domain_candidate_0130 directory manifest has a pre-existing plan.json mismatch. This plan is not executed or imported here. **All six actual dependencies pinned by0745 match their expected hashes**, including finite_copper.py and native_polygon.py. Record the historical drift; do not describe that entire old directory as pristine. Original files remained unchanged during this review.

Initial mirror setup encountered the older0318 manifest's list format rather than dictionary format, causing an incomplete copy; first physical run then lacked the copied provider file. Both failures are preserved/acknowledged and were confined to review setup. The source input was not altered: setup was completed, manifest schema handled explicitly, process completion checked, and fresh full tests rerun successfully. No denied/uncertain writes were retried.

Supplied author scripts are identified as **fresh reruns**, not independently authored proofs. Separately authored inventory and polygon-delta scripts provide additional independent crosschecks. All evidence is available under this directory; scratch trials are not fabrication outputs.

Parent-provided author investigation (received during review, not independently reconstructed here):0130 plan.json mtime03:59 precedes0745 at07:44; plan.py has a top-level write without a main guard; three r17 backups match original manifest SHA `f367c1346f4bff0cdc2359a7dbd6c9b9aad071ea36f5c6d19375c8657065946f`. Reported difference is temporary object UUIDs in local_via_attempts only, with objects/base_sha/unresolved equal. Exact triggering operation remains unknown. No automatic repair or expanded historical audit performed.
