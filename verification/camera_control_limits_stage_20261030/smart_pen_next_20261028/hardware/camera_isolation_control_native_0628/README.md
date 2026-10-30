# Camera isolation control native candidate — independent review pending

**NO FAB / NO POWER. Not a finished pen, safe-power authorization, or manufacturing release.**

- Exact parent `imu_control_native_0522`: PCB `5ed5f0ad90f5f15830f50479e0ecc48fe0685ffaff1819ff642a300f9550a1e9`.
- Candidate PCB **`63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c`**.
-209new copper objects,16through vias, **zero old copper removals**, zero footprint/pad-net/value/source/rule edits.1192total copper objects. R503 remains47k1% YAGEO RC0603FR-0747KL.
- Real CLI with all-track-errors/parity: **0violations /96unconnected /0parity**, parent0/106/0. ERC0errors/1unchangedwarning. AON core**39/39**, GND70/102, SENS12/12.

## Scope and static contract

See `SAFE_OFF_CONTRACT.md`. The originally described seven gaps are the six OE joins and R203 AON source. Completing the MCU-to-commissioning-control graph additionally closes two CAM_IO_EN and one IO_ENABLE_LINK gaps, thus ten. Actual source GPIO42 package48 → R107100k/JP201 OPEN → R2011k/Q201 gate with R202100k ground default → active-low OE with R20310k AON pull-up. All five AXC OE inputs reference AON VCCA. TCA9517 active-high EN is a separate net referenced to AON VCCB, with R2054.7k pulldown overriding its internal pull-up at the documented component screening condition.

JP201,JP202,JP301 remain OPEN. The camera VIO is external J202.23. No NC outputs are connected. No firmware board provider exists, so no operational enable or camera power behavior is claimed. OE pull-up rise time/slew, hot leakage, MCU reset/JTAG internal pulls and whole-head backpower remain unqualified. Source values were not changed to conceal these issues.

## Actual native checks

- Complete physical seven-pad OE, three-pad MCU control and two-pad IO link graphs.
- All prior physical pad-UUID components preserved, including all MCU57physicalEP pads, IMU/pressure/STRAP/source rail/clock and head DVP components.
- New finite copper checked against all old copper, **all physical pads including same-net**, every actual layer, drill spacing, board edges and actual rule areas. New via/pad overlaps0.
- Ten explicit native cut negatives each produce0/97/0 and disconnect intended actual terminal groups; fullbackout0/106/0 exactly restores raw parentPCB bytes. Replay native resource files and materialization map byte-identical. Normal/-O reports agree.
- Manufacturer-dependent static contract separately checked against actual exported source, not PCB pinfunction fields.

## New reference/DFM gates retained, not hidden

The unchanged CAM_ON F track `f50aa801-170b-4339-91cd-374a0faa5f75` loses an additional **0.001488810274mm²** projected coverage on In1. Loss bbox `(6.926610,70.539509,.109401,.066232)`mm. It does not cross that track's centerline. The native merged hole bbox `(6.1495,69.8495,1.551,1.501)`mm contains old CAM_ON via(6.65,70.9) plus new OE vias(6.525,70.225) and(7.325,70.8). Their nearest coreGND via is(7.6,74), distances3.925080mm/3.211795mm. This remains a review/SI gate, not an impedance pass. `reference_delta.json` records exact contour and tested centerline predicates; `reference.png` was visually inspected.

Existing EXTCLK IMU-induced reference loss **0.0017414094705mm² each on In2/In4** remains inherited; this tranche adds0further clock projection loss. Do not reset historicalloss tozero. Existing BOOT/NIB and MCU-SDA mergedholes, thermalEP23.8µm edge, via-in-pad/tenting and U203underbody gates remain.

All16newvia native holes, nearestactualcoreGND observations and ordinarycourtyard overlaps are in `physical.json`. Overlaps include U201/U202/U203 ordinarycourtyards, R107/R203/R204/R230/R231/R234/R241, J105/JP201 and B R219/R303. Pad-copper nonintersection is not a blanket assembly/tenting waiver.

AON guarded native hole normalization retains the prior .25mm erosion tinyisland0.005835438mm²; principal topology/screens unchanged. No current/thermal rating inferred from area.

## Native route metrics

| Net | Planar length mm | Segments | Vias | Segments<.1mm |
|---|---:|---:|---:|---:|
| CAM_ISO_OE_N |46.641418|90|9|68|
| CAM_IO_EN |83.268088|76|4|55|
| IO_ENABLE_LINK |8.959913|26|2|18|

141short signal segments remain because actual pad/branch contact anchors were retained during exact compaction. No production elegance claim. Signals use F/In3/B; no new long GND-plane signals, no thin main-power rescue. `layers.png` visual check shows routing region; not a complete mechanical/board-outline drawing.

Independent review must validate these facts and gates before any claim of a completed candidate review. The unknown purchased camera and all charging/assembly/measurement gates still prohibit powering or fabrication release.
