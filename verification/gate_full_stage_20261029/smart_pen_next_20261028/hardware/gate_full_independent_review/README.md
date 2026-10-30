# Independent complete gate static-copper block review — NOFAB

**Accept the declared static source/copper connectivity delta, not a completed safe gate or pen.** Significant routing complexity and PI/dynamic gates remain. No author source edited, no external write/procurement/manufacturing.

Input PCB **508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35**, author manifest **70f161b643809f8c930c2b32bf82725be6ba742d52635171442646c5bfd6cf52** (100 files). Baseline ae805 and d9ee native-MPN source are hash-bound dependencies in `source_rules.json`; previous evidence is not needlessly copied. Native source/project/libraries necessary for fresh checks are isolated here.

## Fresh native, refill and reconstruction
Commands, using KiCad 9.0.2 and real same-basename project/rules:
```
kicad-cli pcb drc --format json --exit-code-violations --all-track-errors --schematic-parity --severity-all -o drc.json native_snapshot/mainboard_revD.kicad_pcb
kicad-cli sch export netlist --format kicadxml -o fresh.xml native_snapshot/mainboard_revD.kicad_sch
kicad-cli sch erc --format json --exit-code-violations --severity-all -o erc.json native_snapshot/mainboard_revD.kicad_sch
```
- Fresh full DRC **28 violations / 41 unconnected / parity 0**, exit **5**. Baseline 135/54/0. Multiset comparison resolves 109 findings and adds **two dangling-track warnings only**, CAM_SDA / CAM_ISO_OE_N UUIDs recorded. Remaining counts: **9 shorts, 9 mask bridges, 4 hole-clearance, 1 clearance, 5 dangling**. These are real open gates, not waived findings.
- ERC retains one VBUS boundary warning, no errors. Fresh XML: **102 entities / 356 endpoints / 90 nets**. Exact values/footprints/symbol paths/pad nets and ten native Manufacturer/MPN/ProcurementStatus fields verified.
- Independently fresh-filled board: all five zone-layer polygon serializations unchanged; saved refill hash equals input hash. Actual connectivity audit ran on this newly filled/read-back board, not stale zone metadata.
- Rebuilt from immutable ae805 plus exact delta, supplying matching project/custom-rule files to the reconstruction basename. Raw serialized hash differs (`ffea01ad…1379`), but independent explicit track/pad geometry and actual connectivity audit passed; hash difference is not used as evidence of equivalence.

## Full finite-copper and isolation proof
All six-layer actual pad/track polygons, annular vias minus drill holes and each real filled-zone island are joined only by positive-area copper intersection. Existing pad subsets never split. Required power pads stay in core. **AON 1 component; GND 15→12** (not all ground complete). Six gate nets CAM_PWR_EN / CAM_ON / CAM_CT / CAM_QOD / CAM_3V3_PRELINK / CAM_3V3_SW each have one real pad component.

Additional independent check intersected every conductor of those six critical nets with **all other nets** over six layers: **no cross-net copper overlap**. Pre/post JP301 islands also separately checked; full native DRC reports no output-net short/clearance/mask finding. JP301 remains source OPEN/DNP with physical separation. This rules out direct copper bypass, not semiconductor body-diode, leakage or externally attached paths. No unknown camera connection authorized.

MEMS actual plane/via intersections zero; six-layer rule preserved. RF actual radiator finite-copper restriction rechecked including its declared terminal exception, no intrusion. Exact native component delta is only B-side R301/R302/TP301/C302 positions; no component/MPN substitutions.

## Large delta quality: not just lower DRC counts
**229 removed / one explicitly trimmed old VIO track / 1005 added conductors**, surviving old geometry unchanged. Added population is **973 tracks + 32 vias**, not 1005 independent electrical links. **669 tracks are shorter than .10 mm**, minimum .025 mm. This is a highly subdivided grid route and a maintainability/cleanup concern; not evidence by itself of an open/short or automatically excessive electrical length. Cleaning or merging must be a separate successor with full connectivity/DRC replay, never casual deletion of dangling-labelled conductors.

AON In2 fill changed **2→6 islands**, area **741.638→712.671 mm²**. Four ground zone-layers each remain one island, areas modestly reduced. Independently tagging islands as graph nodes proves **all six AON islands and all four ground islands connect physically to original core**; no floating plane island was found. Nevertheless plane area/island count cannot qualify neck ampacity or HF return distribution. Routing over/around plane boundaries and shared impedance remain PI/EMI work, not hidden by the global net graph.

All new PRELINK/SW output tracks are **.50 mm**; no .15 signal spur is used as a declared output main conductor. .50 mm width does not imply guaranteed load-current/thermal performance. Detailed per-net lengths, layers, widths, short-segment counts, plane areas and islands are retained in `geometry_risk.json` / `plane_contacts.json`.

## Main supply and U204 branch independence
The dedicated new main bridge is **.50 mm B.Cu, 9.816295 mm trace-only** with .60/.30 mm vias. Remove **53 new thin-branch conductors**, fresh-fill under matching basename project/rules, and test read-back finite copper: only deliberately isolated R203.2 leaves core; all old AON pad requirements remain, including **U204 pin 8**. U204 pin 3 is SENS_SDA, not its supply.

U204 pin 8 has a separate **.30 mm In3 bridge, approximately 4.2302 mm**, no new via. The removed .15 mm path is thus not the camera main-feed dependency. Removing the .50 main bridge *and* that thin branch is rejected by actual core-load topology in normal and optimized modes. These are DC topology counterfactuals, not load/temperature/PI tests.

## Default control, CT, QOD and path limitations
Fresh source and actual pad components confirm:
- U101.47 CAM_PWR_EN → R302 1 kΩ → CAM_ON/U301.3; R106 100 kΩ and R301 100 kΩ provide separate source-declared pulldowns to real core GND.
- U301.4 CT ↔ C303.1, C303.2 GND. U301.5 QOD ↔ R303 100 Ω ↔ PRELINK. U301.6 output reaches C302 and JP301.1; JP301.2 is a separate switched connector net.
- Physical QOD output-side branch proven by finite copper; whole-segment conservative sum **4.331371 mm**. The centreline-only metric failed to resolve that side contact and correctly reports no length, rather than inventing one.

Replayed path metrics allow finite pad-width contact and omit pad spreading/barrel/plane impedance: C303→CT about **2.716 mm**; C303 GND→first via **5.275 mm** (about 5.52 including pad-centre segment). This remains a long timing-cap return, not a compact low-noise loop. CT same-layer SCL edge spacing around .45 mm is not a crosstalk guarantee. JP301.2→J301 explicit copper path about **21.629 mm**; external harness/load absent. Chip/default pull connectivity establishes neither MCU ROM state, leakage margin, noise immunity nor safe sequencing.

[TI TPS22918 Rev C](https://www.ti.com/lit/ds/symlink/tps22918.pdf) describes reverse body-diode risk and input/output capacitance considerations. Unknown total CL and biased effective capacitance prevent claiming a validated CIN:CL ratio. TPS22918 is **not an overcurrent limiter or overcharge-protection device**. R303/QOD must be checked against actual CL, voltage, internal discharge resistance and pulse energy; continuous external drive is not a single-capacitor discharge. Dynamic startup, inrush, off-domain IO backfeed, discharge pulse heating and unknown camera load remain unqualified.

## Rules, tests and release boundary
Project **2927268f…5b08e**, custom rules **5f62979b…9b7**, canonical netclass **e4f5dac0…5a53** match ae805; full hashes recorded. Explicit six-layer conditional .83 mm stack/.93 mechanical bound retained; default Dk/loss unqualified. Manufacturing preflight rejects missing process/material/quote approval. Native MPN fields retain conditional procurement status, including inherited C302 NRND restriction.

Normal/-O source/copper/isolation/main-feed results retained. Seven corrupted native cases rejected by expected error class, plus two missing-main-bridge topology rejections. Config-aware fresh-refill fixtures are isolated; delivery manifest excludes them. `audit.py`, `source_rules.py`, `geometry_risk.py`, `plane_contacts.py`, `main_feed.py`, `output_isolation.py`, `negative_tests.py`, `negative_main_bridge.py`, `refill.py`, `rebuild.py`, `measure.py` and `qod_branch.py` reproduce checks locally with verified dependency folders.

**Remaining release blockers:** all 28 native findings and 41 unconnected items; mechanical recheck for four moved entities; CT/PI/return geometry optimization or justification; gate/IO dynamics, QOD pulse and real camera load; exact component/process/assembly qualification; RF/USB/thermal/battery safety and budget. DRC reduction is progress, not product completion.
