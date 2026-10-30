# 99.8mm tail/fanout candidate — LIMITED STATIC EVIDENCE, NOT ACCEPTED REPLACEMENT

**NO FAB / NO POWER. JP201/JP202/JP301 OPEN; provider NULL.** Actual FPC/connector installation and signal-reference classification remain review gates.

Parent: independently accepted R218 PCB `ff70d9171b364e2d89ce13d109f22a2362afe76c340d384e194fb541bed6af8a`.
Candidate: `a14b30138f9f74ddbfb28bd20872160a1e83b96c1ed4da91d2805589050f97f4`.

## Actual nominal length correction
J202 moves rigidly(7,90.5)→(7,88.8)mm, same180° B; no other footprint/pad/value/net edits. Three tail Edge.Cuts endpoints95→93.3; RF end−6.5 and complete RF area retained. Extracted bounds x0..14,y−6.5..93.3 give14×99.8mm, replacing101.5mm nominal length. The0.2mm headroom does NOT qualify fabricated tolerance or finished-board≤100mm.

Original placement-only99.8 board had17/79/0. Repaired candidate actual full/all-track/all-severity/schematic-parity DRC **0/75/0**, same missing count as accepted R218. ERC0errors/1 inherited dangling-global-label warning. All-net finite physical pad partitions are EXACTLY equal to accepted R218: GND92/103, AON41/41,SENS12/12, all previous signal/head clock paths and R218 preserved. Six J202 grounds remain intentionally unresolved, not silently joined. No source/rules/stack edits.

## Exact routing delta
33 old copper objects changed,9 B.Cu segments added, zero objects removed; total1240 copper objects. Seven EXISTING vias moved, not seven newly introduced vias:
- D0(13.1,87.6), D1(12.9,86.9), D2(12.7,86.2), D3(12.1,85.5), all0.45mm/0.2mm drill.
- EXTCLK(4.25,88.175),0.45/0.2mm.
- GND(1.25,87.9), VIO(3.5,89.7), retained0.6/0.3mm.
D0–D3 side escape avoids J106 ground solder pad rather than blindly shifting fanout through it. D7 local bend repaired. Remaining terminal stubs and power/ground/clock tail connections shortened. No new long reference-plane signal route; existing clock/VIO In3 termini shortened. Full before/after geometry is `selected_final.json`.

`raw_delta.json` confirms every unrelated old copper/footprint/outline raw block byte-identical. J202 raw block differs only rigid placement; three outline blocks differ only95→93.3. All54 native files except PCB byte-identical to accepted parent.

## Reference evidence — NOT zero loss / NOT SI signoff
At the retained1e−8mm² reporting threshold, every unchanged signal projection is preserved EXCEPT one explicitly retained CAM_3V3_SW/In1 sliver: **2.3103e−8mm²**, triangle vertices(6.651115,88.019799),(6.750677,88.046477),(6.651117,88.019800)mm. This has sub-grid altitude and is consistent with clipping quantization, but that classification awaits independent review. Threshold was not widened and the value is not called zero.

Separately, full per-net UNION comparison (avoiding bend/endcap double counting) shows changed-route uncovered reference increases:
- D2/In1 +0.0198654439mm²
- D1/In1 +0.0194009185845mm²
- D0/In1 +0.0029348785705mm²
- EXTCLK/In2 and In4 +0.000595034125mm² each
These are NOT merged into the tiny unchanged-track residual. `verify.json` reports absolute before/after union areas, every changed segment's absolute coverage and all inherited uncovered segments. Via self-antipad versus additional missing-return attribution is pending independent classification; no blanket no-increase waiver, no fabricated SI approval. Clock timing/skew/return/EMI remains open. An attempted offset-clock refinement worsened AON reference coverage and was rejected locally, not applied to this candidate.

## Physical and assembly gates
All changed copper passes actual finite foreign-copper/outline/rule/drill checks. Every moved via checked against ALL pads on ALL layers, including same-net pads: no overlap. This is nominal CAD only.
Native J202 B.Courtyard DOES exist: moved GND/VIO/clock vias intersect it; exact areas in `physical.json`. Courtyard is not an accepted installation/process contract. Clock via nominal copper gap to its own J202.18 pad is0.05mm, not mask/tenting/manufacturing approval. Full retained13.9×5.5×2.22mm operating/body envelope and J106/J107 wire budgets require independent mechanical check. No implicit via fill/plug/tent, protrusion-free solder, FPC bend freedom or body clearance assumptions. VIO via maintains its original connector-relative position; ground/clock upstream relations changed. RF exclusions and body envelopes were not shrunk.

## Reproducible positive / negative / rollback evidence
Materialization consumes hash-pinned parent and explicit model, deterministic new UUIDs, fresh native fill/reload and stable second normalized refill. Actual independent reconstruction and inverse unified diff match all54 native files; rollback actual DRC0/75/0. Normal/-O reports match.
Eight real native terminal cuts: J202.2/.3/.5/.6/.12/.18/.23/.24. Each refilled/reloaded board loses EXACTLY that physical pad from its parent net component; all other net partitions exact. Actual76 missing/0parity every cut. Seven yield one precisely predicted upstream dangling track/via UUID; ground24 yields0violations. These are broken test specimens, not fabrication boards. Expected upstream dangling item is computed from actual endpoint topology, no blanket warning waiver.

Reproduce in isolated copy with `/usr/bin/python3` pcbnew9.0.2 and kicad-cli: materialize.py,run_checks.py,verify.py,physical.py,negative.py,replay_rollback.py,raw_delta.py,render.py. `TAIL_NATIVE_OUTPUT` redirects reconstruction. Run verifiers normal and `-O`. negative.py writes its own JSON because pcbnew SWIG teardown warnings otherwise contaminate stdout; warnings retained in logs, not hidden.

`manifest.json` is an explicit evidence allowlist. Exploratory attempts, placement-only/rejected intermediate boards, alternate models, negative native specimens and logs of rejected trials are excluded from upload payload. Local diagnostics include initial insufficient pad-layer research inherited from prior task, local tail geometry trials, UUID setter/read-only property correction and deterministic save-order normalization; no rejected trial is promoted into validated source. One early CLI used only XDG_CONFIG_HOME and attempted unwritable default cache/data locations; subsequent checks explicitly used writable/tmp config/cache/data, no retry of denied directories.

Independent electrical/reference and exact mechanical review remain required before adopting even this bounded static candidate. DynamicOE/loadedVOH/actual supply sequencing, unknown camera/FPC, firmware behavior, battery/charging, thermal/DFM, manufacturing and bench authorization remain unresolved.
