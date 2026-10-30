# IMU local supply/return — rejected bounded route plan, 2026-10-30

**NOFAB / NOPOWER. This directory has NO new native PCB and is NOT a completed candidate.**

## Immutable active source
`../pressure_pullup_revision_0318/native/mainboard_revD.kicad_pcb`, SHA-256
`6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c`.
R503 remains **47k 1%**, not superseded by the older 100k source. No source, schematic, footprint, pad, copper, zone or commissioning link was edited. Source has 789 tracks/vias. JP301 remains OPEN. Source validation reported 0 DRC / 134 unconnected / 0 parity, and ERC 0 errors / 1 existing warning; these are **inherited source results**, not a fresh completed-route validation.

## Actual pin/capacitor contract
Read from current native source and checked against ST LIS2DW12 DS11811 Rev9:
- U501.9 VDD, U501.10 VDDIO, U501.2 CS and U501.3 SA0 belong to 3V3_AON. CS high selects I2C; SA0 high is retained, not silently changed.
- U501.5 NC is allowed to tie to ground; U501.6/8 ground and U501.7 RES ground are retained.
- U501.11 INT2 stays intentionally unconnected. INT1, I2C and firmware wake/readout are outside scope.
- C501/C502 are 100nF 16V X7R 0402; C503 is **10uF 10V X7R 0805**, not 1uF. All cap pad1=AON/pad2=GND. No capacitor moves or value changes.
- 7 AON and 7 GND related pads were isolated in source finite-copper analysis. Connecting all fourteen would require proving source-core membership, not merely touching a nearby island. No core-count improvement is claimed here.

## Coherent intended local topology and bounded trial
Use outward F.Cu 0.25mm pin fanouts, VDDIO→C501, VDD→C502, a west CS/SA0 common branch, south NC/GND/RES branches, and an east cap-side ground return. Standard 0.60/0.30mm through vias must access existing AON/GND cores outside the MEMS body. C503 remains at its original location as the local bulk capacitor. No thin new main feed, split ground, cap movement or disturbance of DVP/USB routing is authorized by this trial.

The initial and one corrected local trial are preserved (`plan_initial.py.txt`, `plan_initial.json`, `plan.py`, `plan_route.json`). Successful F fanouts are hypothetical objects only; rejected groups are not inserted. **A partially accepted objects list is NOT a complete routing plan.** C501/C502/C503 plane access was not completed after the return-via blockers were established.

Exact source obstructions (mm):
- Actual B-side J107.1 USB_EN1 pad occupies x1.25–2.75, y80.5–82.5. Initial west AON via(2.2,82) and corrected(2.2,80.4) collide. An additional bounded source-only probe at(2.65,79.9) clears the modeled copper/pads but is not a completed core connection or body-clearance approval.
- In3 SENS_VIO_1V8 trace runs x3.5, y77–91.4, width0.25. It blocks the south return via(3.4,83.4).
- B SENS_HREF runs x5.25, y79.1–90.5; B SENS_VSYNC runs x5.75, y79.75–90.5, both width0.15. They block corrected right return via(5.55,83.3).
- Additional finite alternative probes at(4.45,83.4), (7.3,81.3), (5.72,79.7), (4.35,85.8), (7.2,84.5) are rejected by actual all-layer copper/pad geometry. Exact net/UUID reasons are in `source_and_probes.json`; include EXTCLK, D7/D6, CAM_3V3_SW and C503.1 conflicts. No grid/A* search was run.

## MEMS mechanical constraint retained
Current project interpretation uses F central keepout x3.425–4.575/y81.4125–82.5875 plus body x3–5/y81–83 no-via/no-pour constraints; only required outward pad fanout is considered. Existing back/inner planes remain unchanged. These rectangles are project screens, not purported exact ST package dimensions. ST TN0018 Rev8 guidance and `../../docs/electronics/mems_layered_rule_erratum/README.md` must accompany any resumed redesign. Package stress, solder process and sensor noise/temperature qualification remain open. Unknown component-body collisions are not cleared by copper-only checks.

## Executed verification / limits
`geometry.py` performs finite native shape intersection at .15mm foreign-copper clearance, all-layer via-vs-pad overlap including same-net, .25mm via drill separation, .25mm board-edge clearance and native rule-area exclusion. `inspect_source.py` checks immutable source SHA and reads actual source positions; normal and optimized Python output are byte-identical. Current plan replay is byte-identical. Failed trials are deliberately retained.

**No new native save/fill, full DRC/ERC/parity, finite-core, plane-reference or Unfracture-v2 replay is claimed**, because no complete collision-free native candidate exists. No manufactured or energized assembly, pickup qualification, firmware provider or upload is implied.

## Next decision
Do not continue blind local via searching. A separately scoped coherent placement/routing study must expose actual all-layer DVP/USB/EXTCLK obstacles and component body envelopes, then choose either a verified access corridor or explicitly proposed cap/connector/route rearrangement. Any changed placement must be independently reviewed before materializing a new source. Existing source stays frozen; this blocked plan does not replace it.

Primary sources consulted:
- https://www.st.com/resource/en/datasheet/lis2dw12.pdf (DS11811 Rev9)
- https://www.st.com/resource/en/technical_note/tn0018-surface-mounting-guidelines-for-mems-sensors-in-an-lga-package-stmicroelectronics.pdf (TN0018 Rev8)

Reproduce read-only evidence from this directory:
```
/usr/bin/python3 inspect_source.py
/usr/bin/python3 -O inspect_source.py
/usr/bin/python3 plan.py
```
