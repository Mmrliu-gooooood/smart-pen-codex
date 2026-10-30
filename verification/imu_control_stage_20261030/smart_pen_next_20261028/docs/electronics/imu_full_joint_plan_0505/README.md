# Complete IMU seven-gap connectivity model — original grid variant

**READ ONLY / NO NATIVE / NO FAB / NO POWER.** Actual parent remains `pressure_joint_native_0433`, SHA `69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`, native0/113/0. All seven requested gaps are connected in this **model**, but106remaining is only a model prediction, not a measured new DRC result.

The previously verified `imu_left_fence_scope_0456` local topology is preserved: its three independent MEMS ports, full AON upper/left return, no footprint/source/clock change. Additional MCU escapes are reserved simultaneously before any long route:
- GPIO1/U101.6 to IRQ via(3.275,8.9).
- GPIO5/U101.10 to SCL via(3.925,12.475).
- GPIO6/U101.11 to SDA via(2.575,13.1). SDA uses y12.94 below U101.14; this is a narrow actual gap, not generous DFM margin.

Both actual10k pullup supplies are included: R501.1 to new AON .60/.30 via(.875,86.5); R502.1 via F to actual C503.1(4.35,84.5), **not a nonexistent via at85.6**. Two pullup signal branches are reserved first. One full-length strategy then routes SCL preferentially onIn3, SDA onB, IRQ onF, retaining all earlier branches as hard obstacles. There was no second full-length strategy. All tracks respect the existing actual source geometry; no long In1/In4 signal use, no sacrificed return/clock and no moved footprint.

## Complete checks

`strategy1.json` serializes474new objects and exactly3removed old AON F objects. `verify.py` reconstructs this serialization independently, checking all-pad/all-layer clearance, every old pad component, core connectivity, all IMU14 power/ground, and complete physical pad graphs:
- SCL = R501.2 + U101.10 + U501.1.
- SDA = R502.2 + U101.11 + U501.4.
- IRQ = U101.6 + U501.12.

Conservative new-via antipad subtraction from normalized parent fills retains all old components; AON core grows36→38, GND70→70, SENS12→12. Every whole long-route/local-source/pullup branch removal produces the expected physical disconnection. CS/SA0 B feed retains its four direct-metal negative controls without relying on plane copper. Old-signal projected reference losses under this screen are zero, including EXTCLK. **This is not native freshfill or timing/EMI proof.** Normal/-O verification and metric JSON agree. Actual `.dru` allows .127onlyfor bothFineSignal127; this model screens all new clearance at.15and signal widths.15, conservatively not exploiting that exception. All minimum vias .45/.20 are the existing allowed study rule, not new manufacturing qualification.

## Why this is not an elegant final layout

| Net | New copper length | Segments | Vias | Segments <.1mm |
|---|---:|---:|---:|---:|
| SCL |81.476399mm|184|4|167|
| SDA |84.507706mm|199|3|168|
| IRQ |78.568291mm|69|4|31|

Total366signal segments are shorter than.1mm. Strict collinear compaction has already been applied; there are no remaining adjacent same-direction collinear pairs. Remaining grid micro-turns cannot honestly be deleted as “collinear cleanup.” This variant is retained as reproducible connectivity evidence and baseline for a separately authorized exact-visibility simplification, **not called elegant/production-ready**.

`layers.svg`/`layers.png` show F/In3/B, gray retained source and colored new geometry. Planes are intentionally omitted for legibility. Coordinates and exact widths, not pixels in that image, govern checks.

## Open DFM/physical gates

All new via annuli avoid all real pad copper, including same-net. Courtyard intersections are separately recorded in `verification.json`, including the two inherited U501 gates, MCU underbody/courtyard, back C504, R501, J301, JP201 and back J105. A courtyard pass is not solder mask/tenting/stress/process approval; these intersections cannot be hidden by a zero electrical-clearance count. No manufacturing or assembly release is authorized.

100kHz/10k is only the future controlled I²C test starting point; total bus capacitance, edge/timing, IRQ polarity/latching and actual sleep/wake provider remain unqualified. IRQ's `_N` spelling is not configuration; actual provider remains absent. Preserve all pressure merged BOOT/NIB-hole, camera module, charging, cell, harness, mechanical and other parent risk gates. JP301 OPEN; unknown camera unpowered.

Search binaries and large transient `.bin` arrays are not allowlisted; source `grid_astar.cpp` is included. No frozen parent was edited. Native materialization, full ERC/DRC/parity, native reference/fill checks, cut/replay and physical tests remain distinct next gates.
