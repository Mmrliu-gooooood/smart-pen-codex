# Eight U201 A-port bias branches — scoped candidate, NOFAB / NO POWER

**Pending independent electrical/nominal-mechanical review; not a product, SI or fabrication qualification.**

PCB SHA256 `4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad`, built directly from accepted `sccb_local_reference_1216` / `dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697`.

## Implemented result
Fresh all-severity/all-track/parity DRC: **0 / 59 / 0**, versus parent **0 / 67 / 0**. All eight known U201 CAM_D0–D7 pins now connect to their existing R210–R217 100k pulldown terminals. **All eight U101 long links remain disconnected. No sensor is specified or attached, and this is not a completed functional data bus.**

Exact physical partition tests preserve all other nets and GND94 / AON41 / SENS12 core memberships. All1,182 retained-copper reference projections preserve their prior coverage. This is separate from, and does not waive, the new-path reference interaction below. ERC retains the same one `global_label_dangling` warning; schematic, values, netlist source, BOM source and project settings are unchanged.

## Exact bounded changes
- 50 copper objects added:39 tracks and11 vias. Nine signal vias use existing board sizeØ0.45/0.20mm; two GND vias useØ0.60/0.30mm.
- R210 moves F(1.5,26)→F(10.5,28),0° unchanged. R217 moves F(1.1,21.81)→F(2.5,29),−90° unchanged. No R212 rotation, other footprint move, value/net or component-envelope reduction.
- Exactly seven obsolete R210 GND branch tracks and two obsolete R217 GND branch tracks removed. Shared GND vias(5.3,27.15) and(0.8,24) retained. New .3F leads and GND vias(11.325,26.8) and(3.375,29.5) restore both moved ground terminals to the actual main plane core.
- Every other pre-existing copper object remains exact. All zone/rule/board outlines remain exact, including actual14×99.8mm and full RF exclusion.
- Full retained pose screening: R210/R216 .55mm, R217/R215 .455mm, R217/U201 .62mm nominal separation. Final exact native mechanical report is separate; these are not tolerance/tool margins.

Fixed-pose searches and different net orders failed to join all eight within bounded .025mm grids; that is not a global impossibility proof. Two passive moves plus source-port escape allocation resolved the bounded topology. The planner now handles J108's two **disjoint** native F courtyards separately rather than filling the empty gap with a single bounding rectangle. No courtyard polygon was shrunk; actual mixed-side service pads and unqualified service access remain explicit.

## Manufacturer applicability and electrical limits
TI **SN74AXC8T245**, SCES875C (January2024), PW24: A1–A8 are pins3–10. Both direction pins are physically in the GND core, so when enabled these A ports are **B→A outputs**, not permanently input-only pins. Disabled I/O input circuits remain active. The datasheet also describes typical288k internal pulldowns: the unchanged external100k resistors are additional existing bias, not proof the isolated design otherwise floats. Layout guidance recommends short traces to limit loading. [TI datasheet](https://www.ti.com/lit/ds/symlink/sn74axc8t245.pdf), §§4,7.3.4,7.4,8.4; local source hash is recorded in `source_roles.json`.

Connecting these branches adds actual output loading and stubs. At an assumed3.3V high, the external100k alone draws nominal33µA/channel; this arithmetic is **not** loaded-VOH/leakage/power qualification. CAM_D output transitions can be fast regardless of camera frame clock. Actual edge rate, bus capacitance, sensor/MCU load, coupling, return-current behavior and timing remain unqualified.

| Branch | New track length mm | Vias |
|---|---:|---:|
| CAM_D0 |3.536105496|0|
| CAM_D1 |8.805612427|2|
| CAM_D2 |12.386592933|2|
| CAM_D3 |11.030334495|2|
| CAM_D4 |6.105822750|1|
| CAM_D5 |3.702537754|0|
| CAM_D6 |5.321126101|2|
| CAM_D7 |3.574778020|0|

## Actual new-reference interaction — explicit exception for review
Whole-track simplification preferred actual pre-new-via GND coverage, with **zero fallback**. F is screened against In1 GND; B/In3 against In4 GND. Mixed-power In2 is disclosed separately, not assumed GND or imposed as an unjustified second zero-projection requirement. After actual refill:
- D0/D5/D7 are fully covered; D1's uncovered portions are isolated own-via holes.
- One shared hole contains NEW D2/D3/D4 source vias and the D6 sink via(6.275,29.025), with no old foreign via center. Actual hole area1.753234775742mm² on both In1/In4; bounding box[5.2995,28.6495]..[7.3505,30.1755]mm.
- `reference_classification.json` reports every absolute uncovered union. A whole merged-hole category is **not** identical to foreign incremental missing area.
- Matched-project counterfactuals remove only other NEW signal vias, first proving exact baseline refill bytes. Incremental coverage loss due to these neighbors: D2 B/In4 **0.001069411871mm²**; D3 B/In4 **0.000061716038mm²**; D6 In3/In4 **0.0004544951355mm²**. The four F/In1 cases and D4 B/In4 are0. These counterfactual specimens are diagnostics, never proposed copper deletions.
- Nearest GND-via center distances range1.020110–2.675117mm across the nine signal vias. They are descriptive, not acceptance limits or an inductance/current-path model.

This local mutually coupled transition region is submitted for bounded research acceptance versus further layout repair. It is **not a new-bundle SI pass**, and no threshold has been widened to call the residual zero.

## Exact mechanical qualification
Independent finite screening found no unrelated full-budget/Fab/courtyard intrusion; all vias clear actual pads/courtyards/full budgets and no F trace enters U201's actual Fab-body bounds. New GND-via nominal full-body gaps are.255mm to R217 and.425mm to R210; source signal-via/U201 full-budget gap is.375mm.

Two intended-own-resistor courtyard-only continuations are explicit exceptions, not a net-wide body waiver: D7(2.95,28.95)→(3.55,28.975) intersects R217 courtyard0.011091455283mm²; D5(4.75,28.8)→(4.85,29.075) intersects R215 courtyard2.4833e−8mm². Each directly continues its pad-ended first segment, without full-body/Fab overlap. These finite nominal intended-pad escapes do not qualify soldermask, tolerances, service/probe access or assembly process.

## Reproduction / exclusions
`materialize.py` pins exact parent/model, removes nine exact UUID tracks, applies two rigid translations and deterministic new copper, then checks fill/reload byte equality. `verify.py`, `physical.py`, `raw_delta.py`, `reference_classification.py`, `reference_interaction.py` and `source_check.py` provide native/physical/source evidence. Actual full54-file replay and applied inverse patch restore the parent with0/67/0. Eleven real cut tests remove each bias branch, all eight, and each rebuilt GND via; unrelated nets must remain unchanged. Normal/optimized Python outputs are compared before freeze. `dependencies.json` pins imported geometry helpers, datasheet, mask ledger, pose screen and firmware source.

Explicit manifest allowlist only. Partial planners, rejected via trials, prepared unconnected boards, negative-cut natives and counterfactual-native boards are forensic/test material, **not** validated release content. No automatic remote upload authority.

NOFAB / NO POWER; JP201/JP202/JP301 OPEN; provider NULL. All inherited FPC, RF/sensor, power/OE, loaded-VOH, SCCB-return, bypass-loop, clock/timing, battery/thermal, firmware and real manufacturing/assembly gates remain. Static0/59 is not product readiness.

Additional reproducible reference check: `pre_via_reference.py` removes exactly the nine new signal vias in a matched-project diagnostic copy, retaining both new GND vias and all tracks. All39 new finite-width tracks then have exactly zero uncovered area against their dominant GND reference. This independently confirms the new-path coverage issue comes from the introduced signal-via transition region, not an inherited dominant-plane grazing crossing. It does not erase the actual post-refill coverage/coupling exception.
