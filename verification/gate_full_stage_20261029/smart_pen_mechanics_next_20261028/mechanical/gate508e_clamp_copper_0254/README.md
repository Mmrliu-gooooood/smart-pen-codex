# 508e actual clamp-strip copper recheck — not clamp qualification

Bound source SHA256 `508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35`, `hardware/gate_control_output_candidate/mainboard_revD.kicad_pcb`. Read-only source; fresh fill performed on in-memory loaded board only. No original save or rules change.

The four proposed .25 mm board-edge contact strips are independently rechecked against **new 508e copper**, not inherited from ae805:

| PCB rectangle x/y (mm) | Min filled-zone distance | Track/pad/via bounding-box distance lower bound |
|---|---:|---:|
| x0.. .25, y31..33 | .050 mm | .4115 mm |
| x13.75..14, y31..33 | .050 mm | 2.049999 mm |
| x0.. .25, y81..83 | .050 mm | .8500 mm |
| x13.75..14, y81..83 | .050 mm | 2.4000 mm |

Ten filled polygon outer point lists (net/layer/point-order included) are exactly identical before and after in-memory fresh fill. Distances to all filled outer outlines were calculated as planar FreeCAD faces; hole omission is conservative, and every strip lies outside every outline. Track/pad/via results are conservative bounding-box lower bounds, deliberately NOT asserted to be exact distances to their copper boundaries. No positive-area strip/filled-zone intersection. Per-layer/net distances are in results.json. This is not a substitute for the electrical team's project-context full DRC, signal connectivity or power qualification.

**.05 mm to inner copper is not adequate evidence of safe clamping.** Contact must be insulating, not on components or solder. Mask wear, edge burr/delamination, local strain/warp, clamping pressure, tolerance, material and screw force require actual test; keepers and electrical isolation are NOT approved by this geometric result. Nominal .25 engagement and no new hole do not establish durability. No claim of metal clamp safety or production readiness.

Normal and Python `-O` outputs must agree. Source hash is checked before work and output remains original 508e. Running check.py only writes this study's result JSON; do so in a copy after freezing. Uses pcbnew and FreeCAD; no fetched vendor files, photos, private configuration or physical hardware.
