# Active Schmitt camera-OE — bounded experimental native candidate

2026-10-30. **NOFAB / NOPOWER / provider NULL. Independent review required.**

This candidate replaces the passive NMOS OE edge generator with an AON-powered **TI SN74LVC1G14DCKR**. It addresses the passive RC mechanism only under **stable 3.0–3.6 V AON and controlled USB-JTAG mode**. It does not establish safe autonomous startup/brownout, maximum load or measured edge compliance. JP201/JP202 remain DNP commissioning links; JP301 remains OPEN. No bridge, camera power, charging, purchase or remote publication performed.

## Exact bounded changes

Frozen parent `hardware/camera_isolation_control_native_0628`, PCB SHA256 `63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c` is untouched.

Source is the independently built `hardware/camera_schmitt_source_0744` (manifest `805a1e8db326a59366f68e574808f12c2b2ca2ce5af6de3dcac33d155ec96c86`). Official decision evidence is `docs/electronics/camera_schmitt_candidate_0730`; earlier failure analysis is frozen0719.

- Remove Q201 PMV30UN2; add U205 exact TI part at **(3.0,69.0),0°,F.Cu**. NC1 deliberately has no routed copper; A2=ISO_GATE, GND3=GND, Y4=CAM_ISO_OE_N, VCC5=3V3_AON.
- Add C209 **100 nF 16 V X7R ±10%, KEMET C0402C104K4RACTU candidate**, 0402 at **(5.55,68.85),270°,F.Cu**. Pin1 AON (5.55,68.37), pin2 GND (5.55,69.33).
- R202 remains original0603 position/footprint/pads, changes100k→**10k1%, RC0603FR-0710KL candidate**. Manufacturer tempco100ppm/°C is NOT included in0730's simple1% screen; all-temperature input/VOH/load proof remains open.
- R20310k/R2011k/R107100k and every other old footprint placement/rotation/pad/net remain unchanged. PressureR50347k exact MPN retained.
- Remove six old Q201 fanout copper objects (including one old ground via); add15 copper objects, including four through vias. **1,201 total track/via objects**, 1,186 retained unchanged. New AON/GND tracks0.3mm; signal tracks0.15mm. No new In1/In4 signal routing, no additional In2 signal route; new ISO hop uses In3.
- Official custom DCK0005A example land: five **0.95×0.4mm** rect pads, row-center2.2mm, pitch0.65mm. Do not replace with the installed generic KiCad SC70 footprint. The custom courtyard is an explicitly documented engineering margin, not an official package keepout. No accurate assembled whole-pen3D/mechanical qualification is claimed.

Only native PCB, controls_sccb schematic, ISO symbol library and the new footprint differ from parent native. `native_forward.patch` contains actual forward delta; `replay_rollback.json` enumerates hashes. Native library properties use exact candidate part identifiers; ordering/stock/assembly cost are not approved.

## Actual checks

- KiCad real ERC: **0 errors /1 inherited VBUS_5V global_label_dangling warning**.
- KiCad real all-track/all-severity/schematic-parity DRC: **0 violations /96 unconnected /0 parity mismatches**. Exit5 is expected due unresolved board unconnected items. This is NOT a complete board, USB/boot-power closure, or ready-to-order product.
- Complete filled-copper physical components: **AON41/41**, **GND71/103**, **SENS12/12**. New U205 and C209 supply/ground physically join their intended cores. Other unresolved ground pads are not falsely marked connected.
- Exact OE component: U205.4,R203.1,U201.22,U202.14/U202.15,U203.14/U203.15. Exact input component: U205.2,R201.2,R202.1. MCU/JP201/R107 and JP201/R201 link components preserved.
- All previous functional components preserved using explicit mapping Q201.1→U205.2, Q201.2→U205.3, Q201.3→U205.4. IMU I2C/IRQ, pressure/contact/STRAP and complete head clock independently asserted. All other old copper objects and pad geometries unchanged.
- Four actual new through vias checked against all physical pads on all actual copper layers, **including same-net pads: zero overlap**. Finite-polygon foreign copper clearance, drill spacing, edge and rule-area checks pass.
- Actual refilled plane polygons compared: **no additional reference projection loss under retained old signal copper**. This does not remove inherited clock edge losses0.0017414094705mm² on each of In2/In4 or inherited CAM_ON edge loss0.001488810274mm² on In1. Neither zero added loss nor centerline continuity proves SI.
- Four new vias' real merged-hole contours, nearest actual core ground vias and courtyard intersections are reported in `physical.json`. All inherited reference/EP/mechanical/DFM gates remain.
- `native_negative.py`:14 **actual modified native** cut cases, each independently refilled, physically verified disconnected and checked by real KiCad DRC. Nine previous control-path cases plus new OE, input, supply and both ground paths. Pressure/STRAP/IMU I2C/IRQ and head clock remain connected in every cut. Negative folders are test specimens, never fabrication candidates.
- Independent materialization replay is byte-identical across all54 native files. A real reverse unified patch restores all53 parent native files byte-identically; restored board real DRC0/96/0. This is not a synthetic “rollback” that substitutes baseline PCB bytes.
- Normal and Python `-O` verification/physical/negative results must match; see `final_checks.json`. No test correctness depends on removable `assert` statements.

## Local layout/visual review and DFM conditions

`local_after.png/svg` renders actual pads and F/In3/B copper with actual via circles and engineering courtyards; source schematic rendering/review is in source0744. NC is visibly isolated, bypass reaches AON and GND separately, output reconnects to preserved OE trunk, input crosses via In3 without altering unrelated copper.

Two new GND vias intersect courtyard margins: one at(1.9,70.35) intersects U205 F courtyard; one at(4.9,69.0) intersects U205 and C209 F and C303 B courtyards. These are **not pad overlap**, but tenting/soldermask, component body/process clearance and assembly DFM must be checked with the actual manufacturer. This candidate does not silently waive them. No via-in-pad fill assumption. Full body/3D assembly collision review remains open. The input escape is tight to the0.15mm rule;0DRC is not manufacturing tolerance validation.

The first same-center research screen was not drop-in. This implementation made one bounded local topology, adjusting via sites for actual multilayer obstacles and retaining all unrelated routes; it did not search or rearrange the whole board. Intermediate `trial` files were only scratch and are excluded from deliverable.

## Functional / safety gates NOT closed

1. **Startup/brownout:** AXC may operate below LVC's1.65V minimum. The approximate0.65–1.65V window and VIO independently remaining powered are unresolved. Stable-power commissioning only; a future supervisor/power-good path or enforced default-off sensor-VIO sequencing needs its own exact source decision.
2. **GPIO42 mode:** only the documented GPIO/USB-JTAG mode; no pad-JTAG, pull-up, alternate output or hold that asserts enable. An intentional high and debugger-driven high are indistinguishable. No eFuse changes. The normal reset IE observation does not establish every reset mode's behavior.
3. **Dynamic compliance:** measure both edges at the farthest/all five OE terminals across actual interconnect/probe/load/rail/temperature envelope. AXC10ns/V requirement is not waived. LVC CL50pF propagation delay is not output rise/fall maximum; AXC typicalCi is not maximum. Official LVC IBIS waveform load/temperature limits are stated in0730, not hidden.
4. **DC/thermal:** loaded ESP GPIO VOH, total OE/input leakage at temperature/power-loss conditions, resistor tolerance+tempco, input transition current, output current/overshoot, supply bypass and temperatures need qualification. Neither typical model capacitance nor nominal divider arithmetic is a full worst-case guarantee.
5. **Unknown camera / whole product:** purchased module pinout and voltage uncertainty remain; no direct connection. Pressure contact/ESD/debounce, charging/electrical safety, battery, thermal/EP via processing, mechanical diameter/body placement, all96 open routes, cost and fabrication gates remain. Provider stays NULL.

## Reproduction

Use `/usr/bin/python3` with pcbnew; `kicad-cli` on PATH. Run from project root:

1. `.../materialize.py` (or set `SCHMITT_NATIVE_OUTPUT` to another independent output).
2. `.../run_checks.py`, `.../verify.py`, `.../physical_native.py`.
3. `.../native_negative.py` (normal and`-O`, sequential: writes separate test directories).
4. `.../replay_rollback.py`; `.../render_local.py`.

`geometry_native.py` and finite_copper/native_polygon dependencies preserve exact finite geometry/one-shot native-hole normalization. `dependencies.json` pins external local scripts/source inputs. Do not edit frozen parent/source to make checks pass.
