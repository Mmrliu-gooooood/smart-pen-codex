# Conservative fixed-ground recovery — NOFAB, do not power

This is a limited research successor of `aon_entry_bridge_candidate_2156` (fd989bf8), **not** a complete electrical successor of the accepted 9a03 baseline. The unfinalized 18-branch/110-object study is retained as a rejected comparison. It is not overwritten.

## Result

- Native PCB SHA256: `ead39fa832de2aabff4fbec9ce67d12199094ac9d77e700de54920d8fec86959`.
- Full KiCad 9.0.2 CLI, original project/rules and `--all-track-errors --schematic-parity --severity-all --exit-code-violations`: **0 violations / 203 unconnected / 0 parity; exit 5**.
- Restore **17 whole old GND subgraphs, 96 exact original UUID objects**, with original widths and drills. No partial clipping, new narrow power connection, footprint move or plane-boundary change.
- GND physical pads connected to J106.3 increase **2 → 30 of 102**; 72 remain unconnected. AON remains **1 of 39** (J106.2); 38 remain unconnected.
- The prior 12 DVP chains, full switched-power chain, local GND chain, 19 complete track-only nets and AON entry bridge remain connected. This does not qualify their full electrical/return performance.
- JP301 remains OPEN. No fabrication, upload, purchase, power-up, flashing or device testing performed.

## Why group 37 was not restored

The unfinalized 18-branch study introduced one extra fragment under a 0.25 mm geometric erosion of the AON plane: seven became eight. Its 0.064109831 mm² fragment is bounded by x=0.75..1.123265, y=66.790688..67.040688 mm. It is not a measured current bottleneck or a thermal result.

Eighteen whole-group removal and fresh-fill counterfactuals were run with the same-basename `.kicad_pro` and `.kicad_dru`. **Only removal of group 37** returned the count to seven. Group 37 consists of 14 original objects for `C207.2` and `U204.4`, including GND via `13bf7e2a-de79-4a85-933c-2e382484d6c1` at (3.9,66.6). The entire group was excluded. Its two pads remain unconnected; their later return route needs a separate design.

The seven remaining eroded fragments map one-to-one to the seven baseline fragments. There is no AON pad center within the additional fragment's bounding box. Neither observation proves that the region could not carry load or that every supply path is wide enough: 38 AON pads are still unconnected. Thus the conservative choice does not depend on guessing the load importance of that tiny region.

The current AON fill is **not byte/geometrically identical** to fd989: other restored GND via antipads remove **8.796752166 mm²**. Equal erosion count is not an ampacity/minimum-neck certificate. All four GND filled polygons and every prior SENS track-reference projection are unchanged. Drill projections of all 17 restored vias were checked against SENS track copper (1088 pairs), with no overlap; this is not EMI/field-solver qualification.

`aon_neck_comparison.png` was rendered from native filled polygons and actual vias, and visually inspected. Orange is actual AON copper; blue is the geometric erosion, not a current-density map.

## Verification and reproduction

Run from this directory with system Python capable of importing KiCad 9 `pcbnew`:

1. `materialize.py` restores the selected 96 exact original objects from the frozen 9a03 board into a copy of fd989 and fresh-fills twice. It does not depend on the rejected candidate for this replay. Normal and `-O` outputs are identical and yield the native SHA above.
2. Run the full CLI shown in `check_command.json`. Exit 5 is expected because 203 items remain unconnected, not a success exit.
3. `analyze.py`, `verify.py` and `decision.py`, each normal and `-O`, check real physical-pad finite-copper connectivity, source/footprint invariance, original object geometry, complete-group core paths, 17 independent whole-group deletion negatives, prior chains, plane shapes, reference projections and the explicit conservative decision.
4. `negative.py` removes all 96 added objects from a separate native copy and fresh-fills. It **exactly reproduces fd989**, including the PCB SHA and native **0/231/0, exit 5**. No destructive operation is performed on the frozen source.
5. `compare_removals.py`, `neck.py` and `draw.py` retain the source of the comparative explanation. These additionally require the rejected 2159 study whose hashes are explicitly recorded in `dependencies.json`; that study is not a second accepted design.

Both frozen input manifests were verified: fd989's 80 entries and 9a03's 143 entries. `dependencies.json` records additional precise files used by checks. Missing dependencies must be supplied byte-exactly or the affected check must be reported as not run.

## Rejected execution attempts, not evidence of success

- The first temporary comparison PCB had no matching project/rules. It reported spurious five/six erosion pieces. It is retained with `REJECTED_unbound_project_*` names and excluded from all conclusions. The correct rerun copies the complete native project to a same-basename temporary directory before fill.
- An early reduction replay helper omitted its `__file__` context and stopped before modification. A subsequent CLI therefore examined an unchanged copy of the 18-branch study (0/201/0). `REJECTED_parser_scope.log` and `REJECTED_uncorrected_copy_drc.json` are explicitly non-results. The final materializer replays directly from fd989 plus the original 9a03 objects.

This limited block may be independently reviewed, but the product is **still NOFAB**. Supply/ground completion, functional interfaces, calibrated optics/pressure, full mechanical integration, assembly process, timing, current/thermal performance, battery and total cost remain open.
