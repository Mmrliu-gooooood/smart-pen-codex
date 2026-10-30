# 508e actual-native joint mechanical delta screen — NOFAB

## Authority and scope
Actual native `hardware/gate_control_output_candidate/mainboard_revD.kicad_pcb`, SHA256 `508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35`. Compared by pcbnew to ae805: 102 footprint identities, positions, angles, sides and pad net/shape/size geometry extracted; exactly R301, R302, C302, TP301 changed. This is a new study; frozen RevC and RevD inputs remain untouched. The native board is not modified or refilled here. Electrical audit belongs to the electrical reviewer; old ae805 copper/edge-grip conclusions are NOT inherited to 508e.

B datum Y=2.264793176328504, board maximum thickness .93; X=PCB x−7, Z=127−PCB y. Actual native movements and pin/net mappings are in results.json. R301/R302 exact YAGEO RC0603FR-07100KL/RC0603FR-071KL retain max body 1.7×.9×.55 plus .15 installed height; C302 unchanged TDK C1608X7R1A105K080AC retains 1.75×.95×.95 plus .15. No height reductions. New boxes conservatively union actual pad XY bounds with body max and extrude full installed height (not a claim that bare pads have full component height). This makes R envelopes 2.6 mm wide and C302 2.1 mm wide, stricter than body-only previews.

## Results
- Four changed shapes against all other RevC and RevD shapes: zero positive-volume collisions.
- All RevD fixture parts against complete updated context: zero positive-volume collisions.
- Actual updated entire mainboard assembly lowered from +Y at offsets 10, 5, 2, 1, .5, .1, 0 mm, keepers/screws/hardstops/side shims removed: zero collisions with cassette and remaining fixture. These are sampled positions, NOT continuous swept-path or real assembly proof.
- Both new FreeCAD copies saved and reopened with all shapes valid. Normal and `python -O` numerical results equal, except nondeterministic CAD serialization hashes; final CAD hashes in manifest are authoritative. No claim of new STEP or printed object.
- Unchanged RevC cassette motion, ±.2 separately cut harness poses and RevD fork assembly remain prior evidence, not newly exercised here. Changed items are far from the Z75–79.2 short CONTACT harness; actual nominal whole-context test includes it.

## TP301 correction and tool gate
Actual pad is **1×1 mm rectangle** (`PAD_SHAPE_RECT=1`), not the circle mistakenly described in the unfrozen earlier preview. Final pen center is (−2.675, 2.2647931763, 52.5). Copper thickness is inside substrate. The historical .15 mm external TP budget is retained conservatively, not a physical added part.

Illustrative lateral access from (−15,−1,52.5), Ø2 mm shaft and last 5 mm taper ending Ø.5 mm at pad center intersects the board by **0.1091394693 mm³**: flat finite tip cannot be treated as a zero-radius point. A taper to an ideal mathematical point has zero observed intersections. This is a useful opening-direction comparison only; no real probe geometry, contact force or heat limits have been selected. TP301 access therefore remains **UNQUALIFIED**. Moving the actual endpoint to a correct finite-tip tangent contact requires the real probe specification. Do not claim physical access from the ideal point.

## Boundaries
External 38-part common bench is not a 19 mm finished pen shell. Short-wire endpoints must remain independently fixed; solder joints cannot locate either body. Board-edge clamp pressure/warp, insulating material, spring/hysteresis/50k switch-life, 47k load condition, soldering, strain relief, fatigue, real tool access and two-unit cost remain gates. 5 µm and .01 mm are self-selected metrology targets, not required purchased instrument specifications or allowable strain; see frozen metrology erratum. No approved final diameter, battery/lens mount or production release.

## Reproduction
Run `/usr/bin/python3 screen.py` and `-O` in a **copy** of this study (it saves new CAD/results). Requires pcbnew, FreeCAD/Part, exact source PCB and ae805, RevC `contact_oblique_harness.FCStd`, RevD `common_datum_bench.FCStd` at recorded project paths. These input CADs already contain the prior exact contexts. No dynamic source scripts/proxies are invoked by this screen. Root's four-main-part shell experiment is separate and not represented by these copies.
