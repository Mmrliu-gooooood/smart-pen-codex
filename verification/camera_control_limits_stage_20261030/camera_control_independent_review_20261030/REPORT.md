# Independent camera-isolation native board review — NO FAB / NO POWER

## Finding
The frozen candidate's routing/geometry claims reproduce. This is **not** fabrication release, safe-power authorization, functional camera approval, or SI/assembly qualification. 96 unconnected items and the documented hardware gates remain. JP201/JP202/JP301 must remain OPEN; firmware board provider remains NULL.

## Identity and boundary
- Candidate PCB: `63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c`.
- Manifest: `be6b0eabfd477ab6c3a932204f4b9f05b9e6cab9f8b7c5a41f79514e745f06c3`; all 799 entries checked with zero mismatch.
- Parent PCB: `5ed5f0ad90f5f15830f50479e0ecc48fe0685ffaff1819ff642a300f9550a1e9`.
- No AGENTS.md found by workspace traversal. No remote writes, source edits, actual power, purchases or fabrication operations performed. All test mutations occurred in an isolated copied tree.
- An initial create-process attempt was blocked by exec-server disconnection. After explicit environment restoration, read-only reconciliation established the output directory absent and no process running before work proceeded. No uncertain write was retried.

## Fresh evidence
KiCad 9.0.2 checks in the isolated copy, original `.kicad_pro`/`.kicad_dru`, `--all-track-errors --schematic-parity --severity-all`: parent **0 violations / 106 unconnected / 0 parity**, candidate **0 / 96 / 0**. ERC each **0 errors / 1 global_label_dangling warning**. Exit 5 is expected for these outstanding violations/warnings, not a clean manufacturing release.

Fresh supplied-verifier execution confirms all old physical pad-UUID components preserved, including multiple physical MCU EP pads. Seven-pad OE and three-pad CAM_IO_EN/two-pad IO_ENABLE_LINK finite-copper graphs are complete, with R203 supply incorporated into AON. AON **39/39**, GND **70/102**, SENS **12/12**. No old copper removals, no footprint/pad-net/value/project/rule/source changes. A separate review implementation also compared raw balanced old copper/footprint blocks: zero changes, **209 new objects / 16 vias**.

All 16 new vias checked against physical pad copper on every actual copper layer, including same-net pads: no intersection. Finite clearance/drill/edge/rule-area checks report no errors. These are static geometry checks, not process-qualified hole, soldermask/tenting, assembly or thermal approvals. Ordinary courtyard intersections remain: 16 reported via/courtyard overlap records. Existing MCU EP, under-U203 body, merged-hole, BOOT/NIB/MCU-SDA and assembly gates are not waived.

Lengths independently rerun from native tracks: OE 46.641418 mm / 90 segments / 9 vias; CAM_IO_EN 83.268088 mm / 76 / 4; IO_ENABLE_LINK 8.959913 mm / 26 / 2. Short segments below 0.1 mm: 68 + 55 + 18 = **141**. These are retained DFM/routing-quality concerns, not missing measurements.

## Actual filled-plane loss
A separately written review implementation loads historical, parent and candidate native PCBs and computes actual filled-polygon intersections without enlarged-hole exclusions or masks. Raw native fractured contours are copied and Unfractured exactly once, guarded against explicit-hole input and material-area changes. It reproduces:
- CAM_ON In1 additional projected edge loss **0.001488810274 mm²**.
- SENS_EXTCLK historical IMU-induced loss **0.0017414094705 mm² each on In2/In4**.
- Candidate adds **zero further clock loss**; the inherited loss is not reset to zero.
The fresh reference test finds no additional CAM_ON centerline gap. The merged three-via native hole and the visible edge notch were also visually reviewed in reference.png. Absence of a new centerline gap is not impedance/SI/EMI qualification. Nearest actual core-GND-via distances are observations only, not a return-path proof. AON erosion remains a geometric screen, not current/thermal capacity.

## Negative controls, reproducibility, provenance
`raw/completion.json` is the terminal result: normal and Python `-O` JSON equality; ten fresh native cuts each disconnect intended physical terminal groups and produce 0/97/0; whole-tranche rollback gives 0/106/0 and exact raw parent PCB bytes. Fresh materialization normal and `-O` reproduces native resource files and materialization map byte-for-byte. Frozen tree hashes are checked again at completion.

Author scripts were read and rerun in an isolated mirror; they are not represented as independently authored algorithms. `independent_geometry.py` is additional separately implemented raw-object and actual filled-plane evidence. Source reset/JTAG/transistor/OE slew qualification is assigned to another reviewer and is deliberately not duplicated here.

## Outstanding release gates
96 unrouted connections; incomplete overall GND graph; purchased camera identification and whole-head/backpower verification; safe-off reset/internal-pull and OE slew/leakage qualification; connector/mechanical alignment, tenting/assembly/EP/underbody DFM; charging/protection and bench measurement; actual firmware provider and end-to-end validation. Keep all commissioning jumpers OPEN and retain **NO FAB / NO POWER**.
