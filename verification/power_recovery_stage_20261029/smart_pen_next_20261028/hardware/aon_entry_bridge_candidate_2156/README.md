# Single AON entry repair — research only, NOFAB / DO NOT POWER

Base: `power_zone_freshfill_candidate_2150`, d64594c0ddfcddc7b8c3a40043fe56e144f25d4c59d2fa33e30a9595054c3de5.
Candidate: **fd989bf844a8bc224f315dd3d2559d7a55ae1ba8f9384b0c06b6e301b6668454**.

## Bounded change

Exactly one new **0.50 mm wide, 0.90 mm long In2.Cu 3V3_AON segment**, (11.9,83.9)→(11.0,83.9), UUID `4011118b-7e7a-587d-9f01-ce37302f8576`. This gives the fixed entry via a full-width connection into the existing plane ending at x=11.5. No thin bridge, via relocation, plane enlargement, DVP rerouting, footprint movement or rule relaxation. The original via remains 0.60 mm diameter /0.30 mm hole and the F.Cu feed remains 0.50 mm.

All 533 previous copper objects are exact and one is added (534 total). All 102 FP /366 physical pads, source files and every non-fill board character except that segment remain exact. All five **filled polygon geometries are also exactly unchanged**, not just area: reference/antipad/neck geometry cannot have degraded from this added same-net segment outside/touching the old AON outline. Existing GND reference holes are retained and not ignored.

## Native and independent checks

KiCad 9.0.2 full `--all-track-errors --schematic-parity --severity-all --exit-code-violations`:
**0 violations /231 unconnected /0 parity**, exit **5** (NOT a board pass; unconnected items remain).

Previous AON via_dangling and isolated_copper warnings both disappear without suppression. Fresh fill, save/reload and refill are byte-identical. Finite copper graph uses actual pad IsOnLayer, actual filled shapes and via holes subtracted; J106.2 now reaches the AON plane and the two previously floating middle-bridge segments. The 12 DVP chains, complete SW chain, local GND chain and 19 prior whole nets remain connected. Native full DRC checks all real layers/holes, clearance, keepouts and edges; no new violations.

**Causal negative**: remove this one segment in a separate /tmp native project, fresh fill, then full CLI. It recreates the *exact frozen d64594c0 PCB bytes* and **2/232/0** (exit5). Finite-copper removal also disconnects the AON zone from J106.2. Main candidate hash unchanged after negative. Existing single-GND-via removal negative still works.

All pad-core memberships are unchanged: **1/39 AON and2/102 GND physical pads**. The repair connects the source to a plane, not any omitted load fanout. **38 AON and100 GND physical pads remain disconnected**; U101.57 repeated physical pads are separately UUID-labelled. All 200 foreign-via/zone-layer checks and64 reference-projection results equal the base. `analysis.json` normal/-O identical. `verification.json` contains exact comparisons and actual CLI negative.

## Limits / scope stop

The one entry defect is closed. No attempt to restore remaining load or ground fanouts. Existing 0.25 mm erosion fragmentation and incomplete signal-reference coverage from base persist, so no full-width backbone/ampacity/SI/at-least-old-return claim. JP301 stays OPEN; unknown camera and charge commissioning remain prohibited. This is not the formal accepted board and does not replace 9a03 or frozen d64594c0.

Scripts: `materialize.py`, `analyze.py`, `region.py`, `verify_and_negative.py`, `draw.py`; `fresh_planes.png` and `entry_zoom.png` derive from actual native shapes (track widths drawn as copper polygons). The only candidate tried was this full-width short In2 connection; moving the through via would unnecessarily change all-layer antipads.
