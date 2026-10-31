# NEW reconstructed eight-data research candidate — NOFAB / NO POWER

## Exact scope
Native: `data8_review_native/mainboard_revD.kicad_pcb`, SHA256 `f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71`.
Parent is actually recovered `4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad`, not a reconstruction of missing later bytes.
Native KiCad 9.0.2 reports **0 violations / 51 unconnected / 0 schematic parity**. This NEW 59→51 closes eight CAM_D0–D7 MCU links. It is NOT the lost historical 51 state, which closed different receive/control links.

U101 pads12–19 (GPIO7–14) now join U201 A1–A8 pads3–10 and their existing100k R210–217 branches. Enabled U201 DIR-low operation is B→A; MCU pins must be configured as inputs. PCLK/VSYNC/HREF (both MCU and bias branches) and MCU CAM_SCL/SDA remain disconnected. No camera capture or functional bus claim.

## Declared changes and preserved constraints
- R503 **47k1%** moves B(2.5,11.5)→B(8,16.5); R101 **10k1%** F(2.5,20)→F(2.1,20). All values, pad nets, actual sides, full bodies/heights retained. No other footprint move.
- Restore NIB, PICKUP, R503/R101 AON and R101 CHIP_EN terminal connections; reroute existing AON_I2C_SDA locally via In2 and B to open the joint fanout. No logical pin reassignment.
- Exact original C104 2.55mm/.254mm direct capacitor-to-U101 path AND original GND lead/via/UUIDs preserved. AON stitch moves y14.2→14.75 on the retained feed: pin→plane surface length +.55mm, cap→plane −.55mm. No PDN improvement claim. Original stitch restoration was explicitly tested and conflicts with data fanout.
- Actual14×99.8mm outline, RF region, board thickness/stackup, rule files, native keepout outlines/flags, USB and BOOT conductors preserved. Provider NULL, JP201/202/301 OPEN; sensor/power-sequence/OE gates remain.
- All new data and known signal traces **.15mm**; no DRC reduction. Through signal vias .45/.20. Bias feed widths .25/.30 are explicit; MCU direct bypass feed .254 unchanged. Existing FineSignal127 class is not permission to lower this group's width.
- D1 and existing AON_I2C_SDA use bounded In2 signal crossovers. In2 is mixed AON, NOT ground; dominant adjacent reference is In1 GND. In3 dominant reference is In4 GND, with secondary In2 AON reported separately. No stackup/impedance qualification.

## Geometry, process and route quality
614 new track objects,23 new vias,16 baseline copper removals. One exact collinear PICKUP merge was made; native per-net/layer/width copper unions and filled planes were proven identical before the separate D2 gateway repair. Remaining407 segments under .1mm /304 under .05mm are real grid bends (minimum .025mm), not concealed duplicate straight pieces. No timing matching is claimed. Final metrics disclose layer sequences, lengths, direction runs and existing bias-network totals; conductor totals are not complete electromagnetic pad-to-pad flight time or pure branch-stub length.

Ordinary courtyard-only passages are expressly allowed under the new placement-versus-routing policy, not a waiver of full-body/Fab/tool/mating envelopes, actual pads/copper, rules or keepouts. All new vias remain outside full bodies/Fab. Mechanical report enumerates ordinary courtyard intersections, including small gaps and via projections. Native front/back tenting is intent, not supplier filling/capping/tenting qualification. Unqualified service/commissioning envelopes are not assumed zero.

PICKUP's retained subset beneath R213 has nonzero body/Fab projection, but subtracting exact original same-net copper gives zero NEW projection. It is an inherited process gate, not described as no overlap.

## Reference and power tradeoffs — explicitly NOT SI/PDN acceptance
All baseline physical pad partitions are preserved except the intended eight merges; GND94/AON41/SENS_VIO12 cores remain. Current local AON stitches belong to the same In2 mainland. The removed old R503 stitch coordinate(1.3,12.65) is obsolete, not an endpoint that must remain filled.

- Retained C104/AON F→In1 loss .1396999661545mm² is due to its own moved AON-via antipad; retained D2/D7 F losses .1122997903245/.112116525276mm² are their own destination-via antipads. These are disclosed, not erased by a blanket zero-regression claim.
- D2 B↔In3 gateway moved(4.275,19.325)→(4.275,19.2), only two incident segment endpoints changed. BOOT dominant-GND loss falls from≈.0010625mm² per plane to **2.29745e−8 /2.2976e−8mm²**, explicitly NONZERO numerical residuals. A secondary In2/AON BOOT patch increases .0003615545885→.0014399687805mm². This is a local dominant-return trade, not all-plane zero improvement.
- Other retained secondary-AON losses on BOOT/NIB, and small new-path foreign-hole grazings on several data channels, remain explicitly reported. Independent advisory localizes them; no requirement or claim of arbitrary zero projection on both adjacent layers.
- Original C104 GND corridors to lower U101 ground anchors remain clear. Current AON feed straight projected .15/.30mm corridors remain filled; .50mm corridor clips .010503842669mm². These widths are descriptive screens, NOT accepted current-density/inductance thresholds.
- Fast translator edges, loaded VOH, added100k loading/branch capacitance, through-via stubs, mutual coupling, edge-to-PCLK skew, setup/hold, real firmware GPIO ownership/read-port setup, physical sensor and actual power sequence remain unqualified.

## Reproducible evidence
`final_verification*.json`: explicit normal/-O native contracts, exact retained copper, all-net physical components and cores, declared deltas/metrics.
`final_native_contract.json`: unchanged edge/zone/native footprint keepout flags/project rules.
`final_validation/`: exact reversible native text replay and eight separate MCU-terminal cut negatives, normal/-O. Each negative is run in a fresh process to avoid observed KiCad SWIG lifetime corruption during repeated in-process board destruction; failed diagnostic attempts are not accepted test evidence.
`data8_review_native/drc.json`, `finite.json`, `reference.json`: actual final native report, three-object all-layer/pad/drill/full-budget repair check, and complete1333-retained-projection comparison.
`final_power_trade.json`, `final_bus_path_metrics.json`, `source_roles.json`: explicit electrical geometry/source-role context.
Independent mechanical/advisory packages bind exact native separately. Final full independent electrical review is still required. Freeze means immutable review target, NOT manufacturing or power approval.

Final D2 gateway actual ordinary R102 courtyard gap is .0360076627mm; full-body gap .3713430221mm. This is disclosed under the ordinary-courtyard policy, not a manufacturing margin. Source/full-body dimensions do not shrink to achieve it.

For replay, copy only the manifest allowlist into a NEW directory first; scripts intentionally regenerate reports in their own directory. Run `verify_final.py` normal and `-O`, `final_native_contract.py`, `final_power_trade.py`, `final_bus_path_metrics.py`, `source_role_check.py`, and `final_negatives_replay.py 0..7` each in a separate process, normal and `-O`. `final_validation/native_reversible.ndiff` restores exact baseline/final text with `difflib.restore(...,1/2)`. Run KiCad DRC against the project-matched native copy and compare hash. Do not run mutating report scripts inside the frozen author directory.

Independent causal advisory: `reference_advisory/ADVISORY.md` (SHA256511ab706fe0327160aa471babddd0cc0d6d5a7c8fa3c8ffd150727e1a7058492), original package manifest SHA256ee8458c079451e421dfa937f5d88ed3c5f6b3a35daca8be7eca4b7b2e2fff9f2. The copied advisory/results are an explicitly selected subset; original manifest also inventories its separate read-only counterfactual experiments, which are NOT proposed circuit candidates and are not silently bundled here. Primary final checks are self-contained; the advisory is independently retained separately.

Baseline→final filled-plane differences are also explicit: each GND plane loses9.4230489970765mm² and gains1.0027156232295mm²; AON In2 loses13.9818681924835mm² and gains .212684301506mm². These include new through-via clearances/crossovers, not only retained-trace projections; same-island DC continuity does not qualify PDN impedance. `final_drc_parity.json` was generated with BOTH `--schematic-parity` and `--all-track-errors`, yielding0/51/0; the earlier ordinary DRC report alone was not treated as a parity test.
