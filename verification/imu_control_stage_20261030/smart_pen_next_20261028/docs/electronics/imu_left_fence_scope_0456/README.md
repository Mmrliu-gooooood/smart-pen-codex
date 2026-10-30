# Left AON fence reconnection + three simultaneous local IMU escapes

**READ-ONLY MODEL — NO NATIVE PCB, NO FAB, NO POWER.** Parent remains `pressure_joint_native_0433`, PCB SHA `69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`, actual native0/113/0. This model opens the second local escape domain; it does **not** finish the three long signal nets or reduce the actual113airwires.

Only **one analytical left-branch placement** was tried. No further full-length route search, new component, footprint move, firmware operation, camera connection or upload occurred. Read this together with immutable prior `imu_control_joint_plan_0444` (two incomplete whole-net models).

## Actual left fence / exact delta

Remove only these three **AON F tracks** from the modeled parent:

| UUID | Original endpoints mm | Reason |
|---|---|---|
| `13079769-348d-5142-9cb4-1d44ec56a7b8` |(2.65,80.25)→(5.72,80.25), .25mm|Use already-screened upper beam replacement, preserve complete supply connection|
| `fb1700a3-5c27-5c36-9d84-b9492b46b711` |(5.72,80.25)→(5.72,80.7), .25mm|Same replacement|
| `64d94581-4427-5e32-b859-8e4da0842006` |(2.65,81.75)→(2.65,79.9), .25mm|This vertical CS/SA0 feed fenced off the SCL left escape; replace with fully connected B return|

Preserve CS/SA0's existing F pair tie x2.65,y81.75..82.25 and both pad links; preserve the other left AON rail x1.8,y80..84.5 and C503 feed. The existing source through-via `(2.65,79.9)` UUID `77f42497-a70c-5858-9af0-104c9889f62b` remains.

New complete supply geometry:

- Upper F .25mm: `(2.65,79.9)→(2.65,79.1)→(5.72,79.1)→(5.72,80.7)`.
- CS/SA0 shared tie: new **.45/.20mm AON via at(2.65,82.0)**, directly touching the retained F tie.
- B .25mm return: `(2.65,82.0)→(2.0,81.35)→(2.0,80.4)→(2.65,79.9)`.

This is real copper back to an existing source via, **not** an imagined plane contact or nonexistent via at(4.35,85.6). `verify.py` proves the CS/SA0→source-via path even when **all planes are excluded**. Removing the new AON via or any one of its three B return segments breaks that plane-excluded path (four negative controls).

C501/C502 retain actual100nF0402 and C503 actual10µF0805. Actual C502.1 AON is `(5.72,82)` and C503.1 AON `(4.35,84.5)`, their opposite pads are GND; neither is crossed/renamed/moved. `actual_scope.json` includes all actual pads and nearby copper. R501/R502 remain10k1%, source/CS/SA0 straps unchanged.

## Three simultaneous F escapes and independent ports

All .15mm F tracks. All new vias .45mm copper/.20mm drill; no long In1/In4 signal traces.

| Signal | Exact F path mm | Through-via port |
|---|---|---|
| SCL, U501.1 |(3.2375,81.25)→(2.95,81.25)→(2.65,80.9)|(2.65,80.9)|
| INT1, U501.12 |(3.75,81.2375)→(3.825,81.075)→(3.825,80.8)→(4.025,80.8)→(4.7,80.125)|(4.7,80.125)|
| SDA, U501.4 |(3.2375,82.75)→(2.975,82.75)→(2.9,82.675)→(2.375,82.675)|(2.375,82.675)|

Minimum center spacing among these three signal ports is **1.796176mm**, exceeding .600mm required by two .45mm copper annuli plus .15mm clearance. Each source pad reaches an explicit B-layer annular probe; deleting its own via disconnects the probe (three negative controls). These are **local end ports**, not a promise that long routes from all MCU/pullup pads fit simultaneously.

## Checks completed / checks still needed

- Exact finite clearance against all old/new copper and actual rule areas: **zero findings for the complete joint model**. New via annuli checked against **all physical pads, all layers, including same-net**; drill spacing and board edge checks included.
- All parent physical pad components remain joined in the model, including pressure/STRAP and all existing DVP/clock connections. Footprints/source and original clock copper remain unchanged.
- Conservative screen subtracts new different-net via .15mm antipad envelopes from normalized existing plane fills. After this screen, AON/GND/SENS core pad counts remain **36/70/12**. All **14 IMU power/ground pads** stay in their existing cores: seven AON (U501.2/.3/.9/.10 + C501–503.1), seven GND (U501.5/.6/.7/.8 + C501–503.2).
- Under that conservative plane screen, additional projection loss on retained old signals, including EXTCLK, is **zero**. This is a geometric screen, not impedance/timing/EMI qualification or a replacement for native freshfill.
- Normal and Python `-O` verification JSON agree. Exact coordinates/removed UUIDs are serialized in `local_plan.json`; verifier reconstructs objects from that JSON, rather than trusting globals from the constructor script.

**Two MEMS F courtyard overlaps are explicit open gates**, not hidden waivers:
- AON via(2.65,82):0.0340552mm² overlap with U501 F courtyard.
- SCL via(2.65,80.9):0.0320048mm² overlap with U501 F courtyard.

Their annuli do not overlap any actual pad or prohibited native MEMS body/central region. Both are outside the x≥3.0 actual body boundary; AON via's copper edge x2.875 leaves.125mm to body. Courtyard overlap is not automatically a pad short, but MEMS solder/stress/process clearance remains unqualified; ST TN0018 outer-fanout and assembly review must still judge it. The SDA escape is tightly constrained by existing AON and GND geometry; no manufacturing margin is inferred merely from model clearance.

Native materialization remains a **separate gate**: first integrate both pullup connections and all three complete MCU-to-IMU signal nets in a jointly clear model. Then run real freshfill/full DRC/ERC/parity, source equality, full-component/core/via/reference checks, normal/-O native cuts and replay. Do not manufacture this local partial plan. Existing parent pressure BOOT/NIB merged-hole, underbody-via, harness/clock, camera, charging, battery and mechanical gates remain. JP301 OPEN, absent firmware provider unchanged, IRQ net spelling still does not configure active-low wake.
