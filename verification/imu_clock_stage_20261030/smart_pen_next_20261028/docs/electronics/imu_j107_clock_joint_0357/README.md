# Joint J107 / IMU power-return / restored EXTCLK proposal

**PURE IN-MEMORY PLAN. NO NATIVE SAVED. NO FAB / NO POWER.** Parent review required before native candidate/refill/full DRC. Source remains pressure-corrected PCB `6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c` (R50347k). Inherited source DRC0/134/0 is not a proposal DRC.

## Final single proposal
- Move only J107 B origin from (3.2,84),180° to (5.2,84),180°. Pads USB_EN1(4,81.5), USB_EN2(4,83.9), GND(4,86.3). Their old components were isolated. No cap/IMU/MCU/RF/camera connector changes.
- IMU fourteen AON/GND pads all connected by the 28 planned objects in `normal.json`. Power tracks0.25mm, two0.60/0.30 through vias AON(2.65,79.9), GND(2.65,83.3). C501–503 and U501 unchanged. C503 AON takes left x1.8 path; no crossing the ground bus y83.3.
- Remove exactly old EXTCLK B segment UUID `2010858e-8edf-52c4-a3a5-f423a79bbfc8`, (4.25,78.6)→(4.25,90.5), width0.15mm. Restore it with B(78.6→79.7), standard signal through-via0.45/0.20 at(4.25,79.7), In3(79.7→89.4), same via at(4.25,89.4), B(89.4→90.5). All x4.25, all tracks0.15. No HREF/VSYNC changes. Clock projected length11.9mm unchanged, but two transitions and via electrical length/stubs added: **timing/impedance/crosstalk not qualified**.
- Final AON upper crossbar is (2.65,80.25)→(5.72,80.25), then (5.72,80.7). The existing planned AON vertical x2.65,y79.9..81.75 retains the left junction. No extra power widths reduced. All33 objects exact endpoint specs in `normal.json`.

## Evidence
Normal and optimized-Python models are byte-identical JSON. All33 objects simultaneously tested against all old copper/native pads, new objects, drill spacing, board edge, native rule areas. Moved J107 pad versus old foreign copper checked independently after removing only the identified EXTCLK segment. Native geometry caches explicitly cleared after pose/crossbar changes. Route errors0; movedpad errors0; J107 same-side footprint courtyard errors0. Every old pad-component set preserved.

Finite modeled plane/component counts: AON28→35/39; GND61→68/102; SENS12/12. All seven target AON and seven target GND pads reach their correct existing cores. Removing the respective IMU access via leaves that entire seven-pad group offcore. EXTCLK before/after remains U203.13↔J202.18, with R235.1 still independently isolated as in source. Removing only restored In3 middle segment splits those endpoints: causal negative passes.

Old signal reference projection loss0. Nominal new planes retain one component under guarded0.25mm erosion. New clock projection is covered by In4 GND everywhere except its OWN two necessary via antipads; exact uncovered residual outside those antipads0. In3 additionally overlaps In2AON reference projection, also no other gap. This is not a field solver or native refill: no timing/return-current certification. B and In3 can both reference In4 nominal GND; no arbitrary change to another reference-net assumed.

## Courtyard boundary correction
The initial clock upper via y79.0 hit JP201 copper; y79.2 avoided copper but invaded JP201 solder-bridge courtyard and is **REJECTED/NOT SELECTED** (`rejected_courtyard/`). The final y79.7 was derived from measured boundaries, not an unbounded search:
- JP201 F courtyard maxy79.295; J107 B courtyard miny80.355.
- Complete0.45mm via ring outside both requires center79.520..80.130.
- Final center79.700 gives nominal courtyard gaps0.180mm/0.430mm.
- Moving planned AON crossbar to80.25 gives via-to-AON copper gap0.200mm, i.e.0.050mm above the0.150 rule, **not an absolute manufacturing tolerance guarantee**.
- No JP201 courtyard intersection remains. The unchanged IMU GND via intersects U501 courtyard0.0292143mm² but not its actual project body/no-via rectangle. TN0018 stress, soldermask, tenting and assembly checks remain open; do not waive by “0 DRC”.

## Mechanical and safety boundary
J107 final pose is exactly case2 in frozen `../imu_access_corridor_0345`: four nominal CAD contexts, full retained1.8×2.2×2mm per-terminal envelope, zero collisions, minimum non-board0.93mm. No smaller invented heights. Those contexts are not a regenerated current complete assembly; actual wire/fillet, bend/strain relief, tool access, insulation, IMU stress and thermal budgets remain unqualified. Unknown camera remains disconnected, JP301OPEN. IMU I2C/IRQ/prewake firmware and other board unrouted nets are not solved here.

`plan.png` visually inspected: F supply/return, B relocated terminal, In3 restored EXTCLK. Render uses illustrative widths/rectangular pad views; exact geometry checks are in the JSON, not the picture.

## Reproduction / native successor
Run system `/usr/bin/python3 check_model.py` and `-O`; stdout ends in a harmless SWIG removed-track ownership warning, retained in raw logs. Parse the first JSON object (normal/optimized JSON provided). Frozen predecessor scripts are read dependencies, not modified. `check_model.py` removes the old segment only in RAM; it does not add/save native objects, instead forms a finite polygon model. Native implementation must explicitly move J107, remove that exact original segment, add these33 objects, retain all other789−1 existing objects, then refill, run full DRC/ERC/parity, independent component/invariant verification, and preserve geometry/assembly caveats. Expected copper object count before native fill789−1+33=821; no success claim until actual native verification.
