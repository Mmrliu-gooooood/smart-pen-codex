# IMU power/return + J107 access + EXTCLK native candidate

**NO FAB / NO POWER — incomplete board, not product release.** No remote push or physical action performed by this subtask.

## Verified stage result
- Parent source `6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c`, pressure R50347k1% retained.
- Candidate `native/mainboard_revD.kicad_pcb`: SHA256 `d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22`.
- Real KiCad9.0.2 full `--all-track-errors --schematic-parity --severity-all`: **0 violations / 120 unconnected / 0 parity**, versus parent0/134/0. ERC0errors/1 inherited VBUS_5V global-label warning. CLI exit5 is expected from unfinished connectivity/warning; not a clean release.
- Native finite copper cores: **AON35/39, GND68/102, SENS12/12**. All14 IMU AON/GND pads now join their designated existing rail cores. Every old connected pad-component set is preserved; nineteen previously complete nets and twelve translator→J202 DVP chains remain complete. EXTCLK U203.13↔J202.18 restored; R235.1 remains isolated as in source.
-821 native tracks/vias =789parent−1old EXTCLK+33proposal objects.102 footprints retained; only J107 pose changed. No other footprint, pad net, schematic, BOM value, source, rule or stackup change (KiCad R503 MPN serialization normalization below).

## Exact selected changes
Approved plan `../../docs/electronics/imu_j107_clock_joint_0357/manifest.json`, hash `53fdac310f1b3ed4b8279e8ba04f402d99f13e60aabcd661fdf24897ba2e18e8`.

J107 backside origin(3.2,84)→(5.2,84),180°. IMU/U501/C501–503 unchanged. New power traces0.25mm, AON via(2.65,79.9) and GND via(2.65,83.3),0.60/0.30mm. AON crossbar y80.25 is FINAL; do not use rejected y79.9 variant with clock upper via79.2.

Remove only old EXTCLK B segment UUID `2010858e-8edf-52c4-a3a5-f423a79bbfc8`. Restore original(4.25,78.6)→(4.25,90.5) endpoints with B stubs and In3 middle via(4.25,79.7)/(4.25,89.4), standard0.45/0.20mm signal vias,0.15mm clock trace. Projected11.9mm unchanged; two transitions, electrical via length/stubs added. No HREF/VSYNC rework. Clock, strobe and firmware timing are NOT certified by connectivity.

## Independent checks and reproducibility
`verification.json`/optimized: exact object delta, unchanged old objects,102FP/pad identities and pose, all previous components, actual cores, all-layer physical via-to-pad overlap including same-net=0. Native finite drill/copper/edge/rule checks=`physical.json`; no added copper conflict. Same script normal and `-O` outputs identical. Independent materialization replay produces byte-identical native files; repeated freshfill byte-stable.

Native negative tests reload, refill and CLI-check separate per-case processes, not stale cached connectivity:
|Cut|DRC violations / unconnected / parity|Measured consequence|
|---|---|---|
|AON access via|0/121/0|All7 IMU AON target pads offcore|
|GND access via|1/121/0|All7 IMU GND target pads offcore; expected1track_dangling|
|EXTCLK middle In3 segment|2/121/0|U203.13↔J202.18 disconnected; expected2via_dangling|
|All33 additions, restore pose+old segment|0/134/0|Parent connectivity/copper restored|

Normal/optimized negative JSON identical. Initial negative checker expected only track_dangling and was corrected to assert the exact observed per-case dangling types; it did not change the PCB to suppress a genuine violation. Earlier exact `JP301=OPEN` assertion was corrected to the actual full source value `OPEN / DO NOT BRIDGE`. Frozen source never changed.

## Honest rollback serialization boundary
`rollback_format_audit.json` distinguishes:
1. Raw freshfilled rollback **does not** byte-match parent because KiCad moved/prettified only the pre-existing R503 MPN property. Token contents unchanged.
2. Freshfilled/serialized parent **does** exactly byte-match raw rollback.
3. Only after an explicit restoration of the original R503 property-block formatting does the inverse board byte-match original parent SHA6902c742. Separate `rollback_format_restored/` artifact, not silently substituted for raw rollback.

Independent R503 checks confirm47k1%,MPN RC0603FR-0747KL,pose(2.5,11.5),pads3V3_AON/NIB_CONTACT_N identical in source/native/raw rollback. No reverting the pressure fix.

## Real filled-plane/return evidence
Guarded one-shot hole normalization precedes area/erosion checks. Actual main In1GND/In2AON/In4GND lose about1.532279mm² each; other small GND regions unchanged. Each remains1component after0.25mm erosion. No old signal loses additional reference-plane projection.

New EXTCLK projection lacks copper only at its own actual native antipad holes. Ideal-radius modeled masks leave up to0.000549411mm² edge slivers due to native filler polygon shape. `physical.py` instead extracts exactly the one normalized native hole containing each new clock via on each relevant plane, verifies local bounded0.751×0.751mm extent (<0.8mm bound, not a widened clearance allowance), and subtracts that exact contour. Residual outside actual own holes=0. No relaxed numerical threshold to invent a pass. This is geometric coverage, not EM/impedance/crosstalk validation; B and In3 both have In4GND nominal reference.

## Assembly/MEMS/mechanical gates still open
- JP201 top-via courtyard intrusion resolved: final center79.7. Nominal full-ring gaps to JP201/J107 courtyards0.18/0.43mm; via→AON copper0.20mm,0.05 above0.15 rule. These are nominal geometry, not tolerance/capability guarantees.
- GND via15 overlaps U501 F courtyard0.0292143mm², but no project-body/no-via rectangle or native MEMS keepout intrusion. Keep TN0018 stress, stencil/mask/tenting, actual package/assembly process qualification OPEN; no “0 DRC” waiver.
- Same J107 case2 in frozen `../../docs/electronics/imu_access_corridor_0345/mechanical_screen.json`: four nominal CAD contexts, complete1.8×2.2×2mm per-terminal envelopes, zero collisions, minimum non-board0.93mm. This is a linked nominal clearance result, not regenerated current whole assembly or actual solder/wire/tool/strain/thermal validation. Unknown actual heights are not treated as zero.
- Existing MCU exposed-pad DFM and power widths/thermal gates stay open. IMU I2C/IRQ/prewake firmware still needs completion. Remaining120 airwires are NOT dismissed. Unknown camera must remain disconnected; JP301OPEN; no battery/charger commissioning.
- `native_view.png` rendered from actual candidate and visually inspected. Plot strokes/pad boxes illustrative; native geometry and JSON authoritative.
