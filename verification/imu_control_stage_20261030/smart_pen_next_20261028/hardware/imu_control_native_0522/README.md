# IMU control native candidate — authored verification, independent review pending

**NO FAB / NO POWER. This is not a finished pen or released manufacturing layout.**

- Parent: `pressure_joint_native_0433`, PCB SHA `69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`.
- Exact authorized visibility model: manifest `9283c89b82521e7076ae2c5a29359b57ddad8105995380410e1c969d25735395`, serialized model SHA `25f8a55621a03cc5201c2186c7e29a8769c967a98886d16960825645fca34137`.
- Candidate PCB: **`5ed5f0ad90f5f15830f50479e0ecc48fe0685ffaff1819ff642a300f9550a1e9`**,983copper objects.
- Exact delta:137new objects including13through-vias;3specified old AON F tracks replaced with full source reconnection. No changed source/rules/footprints/pad nets/pressure STRAP/clock or existing DVP copper. Every new coordinate, layer, width and drill matches the model after native database serialization.

## Real CLI and physical results

| Check | Parent rerun | Candidate real result |
|---|---:|---:|
| Full DRC violations |0|0|
| Unconnected |113|**106**|
| Schematic parity |0|0|
| ERC |0errors/1existingwarning|0errors/1existingwarning|
| AON/GND/SENS core pads |36/70/12|**38/70/12**|

Commands include `--all-track-errors --schematic-parity --severity-all`; exit5is expected because106connections and the old ERC warning remain. `cli_results.json` and actual logs/JSON are retained, not just summary counts.

Complete physical graphs now include:
- SCL: R501.2 + U101.10(GPIO5) + U501.1(SCL).
- SDA: R502.2 + U101.11(GPIO6) + U501.4(SDA).
- IRQ: U101.6(GPIO1) + U501.12(INT1).
- R501/R502 remain actual10k1%; both AON sides join the real core. Source functions are read from exported netlist, not guessed PCB pin labels.

All old pad components, all IMU14power/ground, pressure4-pad NIB/2-pad CONTACT/STRAP graphs and all previous clock/DVP connections are retained. Actual finite clearance checks cover all added copper, all physical pads **including same-net**, all layers, drill spacing, actual rule areas and board edges. New via/pad intersections are zero. This does not clear the recorded courtyard/assembly risks.

## Important measured model→native reference difference

**The earlier conservative/model “zero reference loss” estimate is superseded by actual native evidence.** No route was moved or rule relaxed to hide this result.

The unchanged EXTCLK In3 segment UUID `eba5b185-27fd-57f9-b1a5-37b4fa4d4ec8`,x4.25/y79.7..89.4, has **additional uncovered strip projection0.0017414094705mm² on each of In2 and In4**.

- New IRQ via(4.7,80.125) and existing clock via(4.25,79.7) occupy one actual merged native hole.
- Hole bbox: `(3.8745,79.3245,1.201,1.176)`mm; both via centers and exact contour vertices recorded.
- Additional loss bbox: `(4.175,80.068649,.15,.107654)`mm. Longest y-projected band loss=.107654mm.
- Added loss does **not** cross the clock centerline. Existing and candidate centerline gaps remain79.7..80.0755and89.0245..89.4, each.3755mm at the endpoint holes.
- New IRQ via's nearest actual core-connected GND via is(2.65,83.3), center distance3.779302mm. This is geometry, not an impedance/return-path pass.

`reference_delta.json` records actual contours, bbox, centerline intervals and positive/negative predicate controls. `reference_delta.svg/png` is the rendered and visually inspected crop. **Area, centerline continuity or old-pad connectivity alone cannot determine SI acceptance.** This remains an explicit independent-review/physical-validation gate.

## Every new via and actual plane/return evidence

`physical.json` reports all13new vias, nearest actual core-connected GND via distances, all native In1/In2/In4 holes, included via centers and all courtyard overlaps. Do not replace merged holes with ideal individual circles.

Other retained observations:
- The AON/SDA MEMS-side vias share a ground-plane hole bbox(1.9995,81.6245,1.026,1.426)mm.
- MCU SDA via(2.575,13.1) belongs to an In2hole group containing7via centers, bbox(.8845,9.1245,3.866,11.326)mm.
- Guarded native polygon normalization is used once, not repeated on canonical polygons. Ground-plane .25mm erosion keeps one principal component.
- AON .25mm erosion count1→2includes a **tiny residual island**,.005835438mm² atbbox(2.7255,13.660878,.129029,.164881), while the main eroded component remains759.077mm². It is not evidence of the whole AON backbone splitting into two large regions. Actual un-eroded core connectivity remains38pads. Neither component count nor area certifies current capacity. `aon_neck_screen.json` includes parent/candidate .1/.15/.2/.25screens, including pre-existing tiny fragments.

Courtyard intersections involving U501 outer fanouts, U101, back C504, R501, J301, JP201 and back J105 remain open DFM/assembly/stress/tenting gates. New vias do not hit actual pad copper, but that is not a stencil or via-in-pad waiver. Preserve the earlier pressure BOOT/NIB merged-hole and underbody-via gates.

## Native route metrics

| Net | Actual planar length | Segments | Vias | Segments <.1mm |
|---|---:|---:|---:|---:|
| SCL |81.004717mm|35|4|21|
| SDA |83.185206mm|50|3|29|
| IRQ |77.440401mm|30|4|3|
| Existing EXTCLK |46.262500mm|7|3|0|

The53remaining tiny control segments are real and reported; no “consumer-grade elegance” certification is claimed. In1/In4 are not used for long signal routes.

## Native cuts, rollback and reproducibility

Ten meaningful cases each use a separate real native PCB, freshfill, physical graph check and full native DRC. They include3long-route cuts, GPIO1source cut,2pullup signal cuts,2pullup supply cuts, CS/SA0supply-via cut, and complete rollback. Every cut preserves pressure/STRAP and clock connections outside its intended targets.

- Nine functional cuts each produce107unconnected; only expected dangling-track/via violations occur where cuts leave stubs.
- Complete rollback restores real0/113/0and **raw parent PCB bytes exactly**.
- Inverse text materialization before refill also matches raw parent bytes.
- Repeated candidate freshfill is byte-stable. Independently rerun materialization reproduces every native/resource file and materialization map byte-for-byte.
- Verification, physical/hole, reference, neck-screen, source-contract and10native-negative JSONs agree under normal/optimized Python. No normalization-only or manually restored property-block caveat is needed for this parent.

## Not yet demonstrated

The pin name `PICKUP_INT_N` does not program active-low behavior. LIS2DW12 reset/default push-pull active-high nonlatched behavior must be configured/tested; the actual firmware provider still returnsNULL. Copper connectivity is not working prewake, first-stroke capture or coordinate accuracy.

No full-pen manufacture, battery/charging validation, MCU supply transient, optical focus, camera-module pinout safety, I²C capacitance/timing, clock SI, harness/strain, thermal, endurance or consumer compliance claim is made. Actual106airwires still remain. JP301 OPEN, unknown camera disconnected. No remote upload, purchase, physical powering or frozen-source modification was performed in this stage.
