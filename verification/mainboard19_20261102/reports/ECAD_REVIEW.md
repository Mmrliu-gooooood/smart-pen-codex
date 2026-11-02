# R230 / SENS_D6 final candidate — independent ECAD

Candidate f7632bf6296ba212ec59e54edb1dfdb91995f6f4f071a3d9505b6638f3fbf416; accepted parent1639b8db38415f0466c13334add7cd4bfe6708b0caa232e8b1e79a7044fdf8e7. Conditional static review only, design acceptance required. NOFAB/NO POWER; no SI/PDN/boot or complete assembly qualification.

## Explicit final DRC gate
Independent CLI runs the complete candidate_native/mainboard_revD.kicad_pcb with --schematic-parity and no severity filter. drc_gate.py explicitly requires JSON violations TOTAL=0 (including every warning), unconnected_items=19 and schematic_parity=0. Final result is0 errors,0 warnings,19 unconnected,0 parity.

The original4ab628 actual DRC JSON with0errors BUT2warnings is retained as warning_fixture_4ab628.json. Both normal/-O gates explicitly reject it on DRC_ALL_SEVERITIES_ZERO while preserving19opens/0parity. Thus warning-bearing output cannot pass an error-only or log-tail-based check. Earlier candidates remain unaccepted; only the final native hash is reviewed here.

## Strict object changes
Only approved1.1mm old GND leaf037571e0 removed;8 Btracks added (.15 D6,.30 GND), no new or removed vias. All3185 retained copper objects exact. Only R230 physical footprint is rigidly flipped F→B0° and moved to(4.25,36.2). Its ENTIRE serialized footprint equals independent native rigid replay,100k1%, padUUIDs/nets/full shapes/masks/identity preserved; R224 untouched.

Additionally only J107 usertext UUID7bdd4403-e4fa-4ba6-b02d-6a4a325e4f85 '1 EN1' moves globally(5.22,35.71)→(7.6,35.71), local(-1.18,4.05)→(1.2,4.05). Exact raw comparison allows only that position token; content/font/size/stroke/layer/mirroring/angle and every other J107 attribute/pad/pose unchanged. Other101 footprint blocks exact. All53 nonboard dependencies, zone/rule definitions and pin mapping unchanged.

Raw footprint parsing uses balanced top-level native_blocks.blocks plus startswith('(footprint'), not a newline-sensitive empty matcher. Both parent and candidate require exactly103 nonempty footprints before pcbnew loading and again after Reference mapping. Empty-input, missingFP and unauthorizedFP mutations explicitly reject.

## Actual complete source and finite topology
Independent XML export uses candidate_native/mainboard_revD.kicad_sch (not nested legacy):103 components,10 sheets. All91 named electrical network logical terminal sets match PCB; finite group92 is the empty net for2 J202 mechanical pads. U101.57 is the sole repeated logical terminal with9 physical pad copies, explicitly checked.

Only SENS_D6 merges [{J202.11,U201.15},{R230.1}] to {J202.11,R230.1,U201.15}. GND103/AON41/VIO12 unchanged. Every new track reaches an actual pad component. Signal reuses existing D6 via(3.725,39.3), no new hole.

Independent finite copper graph explicitly binds R230.2, oldGNDvia74ea5a95 at(11.1,32.325), and new-feed existingGNDvia ba18b306 at(1.5,33.725) to the SAME physical103-pad GND component. This is not a same-net-name inference. Retained vias/stitching remain byte-exact.

## Nominal clearance / inverse
All8 additions AND both moved R230 pads screened against foreign copper on applicable layers. Native25nm outward polygons/1nm brackets; actual mixed/default requirement.15mm (bothFineSignal127.127). Minimum .162581–.162582mm: newtrack edd29acc versus B CAM_HREF track5b48baa4. No new drills, hence no new-drill minimum is claimed (JSON null). Nominal geometry does not qualify manufacturing tolerance.

Inverse removes8 additions, restores1 oldleaf plus original R230 and original J107 rawblock, refills matching project: exact parent1639 PCB AND entire project bytes restored.

## Regressions and replay
Normal/-O core,clearance,finitefunctional,top-source comparisons. Twelve structural mutations in both modes (24 cases): missingD6,missingGND,wrongD6width,wrongGNDwidth,wrongnet,removedoldGNDvia,wrongR230value,wrongpose,emptyinput,missingR224,unauthorizedR224change,unauthorizedJ107labelcontent. Four DRC gate cases include actual warning fixture rejection. Copied complete-project replay reruns core, actual top export and full CLI/gate; evidence reports counts rather than log suffixes.

    /usr/bin/python3 review.py
    /usr/bin/python3 clearance.py
    /usr/bin/python3 functional.py
    /usr/bin/python3 footprint.py
    /usr/bin/python3 inverse.py
    /usr/bin/python3 negative.py
    /usr/bin/python3 drc_gate.py
    /usr/bin/python3 drc_regression.py
    kicad-cli sch export netlist --format kicadxml -o top_netlist.xml candidate_native/mainboard_revD.kicad_sch
    /usr/bin/python3 top_source.py

Use writable XDG directories for CLI, KiCad9 pcbnew/kicad-cli. Parsed JSON comparison ignores only source absolute path after export; dictionary ordering may differ on directory copy. Generated inverse/negative project copies omitted and reproducible. Independent final plane/MCAD manifests are separately bound; they do not authorize fabrication/power.

## Final companion bindings
Planes `independent_r230_final_planes_20261102_1154/manifest.json`, SHA94b99c38b8fcd7d1aaa41536b609c5eccd9f1211cd562bfa835f6ce0f6905ef7,294payload. Actual3 planes exactly equal1639;3962retained projections/36caps/12ports unchanged. Both old/new feed vias contact same actualIn1/In4 GND polygons (.12742847897mm² annular intersections each), and same R230/U101.57 finite core. A keep-net-name/remove-copper-geometry negative breaks connectivity. D6 actual uniongap.10908327511mm² is local oldsignalvia effect; newGND fully referenced. NoSI/PDN claim.

MCAD `independent_r230_final_mechanics_20261102_1156/manifest.json`, SHA68275a66c9a5e0c7571916cce2941d8a64bb8a638d4cdd6729bc7688126e3a70,23payload. Full104 actualflip,1524body/copper tests,8native keepouts, own-pad-only allowances, unknown-operation proxies and exact3D scene intersections pass. Only R230 budget moves;213 other shapes fixed and reopened/readback. Nearest positivegap J107.1=.515mm; historical assembly unknowns/camera absence retained. No complete-pen fit or supplier-height qualification.

Historical mechanical raw-scanner supplemental manifest `mechanical_raw_scanner_erratum_20261102_1154/manifest.json`, SHAe757b8dbdd45dffa40afaf932054aefeac2a14951fb3f39fe3a2fbd8f782f3c8,6payload, bound without rewriting older manifests. Current independent ECAD parser and finalMCAD both require nonempty103 blocks and reject empty/missing/unauthorized modifications.

Companion manifests are bound copies; their complete payloads remain separate. Design acceptance and publication are separate from this review; this review made no native edits.
