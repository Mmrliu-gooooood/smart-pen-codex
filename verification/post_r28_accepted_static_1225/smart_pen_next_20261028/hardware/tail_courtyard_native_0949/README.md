# Ground / VIO / EXTCLK whole-tail escape — pending independent review

**NO FAB / NO POWER; JP201/JP202/JP301 OPEN; provider NULL.** This is a bounded local successor, not manufacturing or dynamic/SI approval.

Parent0927 PCB: `a14b30138f9f74ddbfb28bd20872160a1e83b96c1ed4da91d2805589050f97f4`.
Candidate PCB: `8684d20fa449402ab1309b9af17d1cb64e0e6c4935532a36febaf362b0060f09`.

## Closed nominal routing obstacles
The three GND/VIO/clock vias formerly intersecting native J202 courtyard are moved upstream and their complete affected paths rebuilt. No footprints, pads, nets, source, rules, layer stack or outline changed. Actual14×99.8mm remains, full RF area retained. All three moved copper discs now clear ALL native F/B courtyards and all physical pads, including same-net pads; they also clear the full retained J202 open-envelope projection x.05..13.95,y87.8..93.3:

| Via | Position mm | Diameter/drill mm, unchanged | Gap to full J202 projection |
|---|---|---|---|
| GND | .8,87.4 | .6/.3 | .1mm |
| SENS_VIO_1V8 | .8,85.6 | .6/.3 | 1.9mm |
| SENS_EXTCLK | 2.5,87.525 | .45/.2 | .05mm |

Power vias were NOT shrunk to force clearance.9 existing copper objects modified,4 tracks added, zero removed;1244 total objects. New tracks are two In3 local termini (VIO/clock) and two B clock escape segments, original widths retained: GND.3,VIO.25,clock.15mm. Existing VIO In3 trunk shortened and fanned left; no plane-layer signal route added. Whole paths are in `selected_final.json` and F/In3/B render.

## Actual electrical evidence
Full all-track/all-severity/schematic-parity DRC **0/75/0**. ERC0errors/1 inherited dangling-global-label warning. Every physical pad component on EVERY net EXACTLY equals0927, including GND92/103,AON41/41,SENS12/12 and acceptedR218. Six J202 grounds and other inherited omissions remain. Finite copper/drill/outline/rule tests pass for every changed/new item. Every unrelated copper/footprint/outline raw block is byte-identical; PCB is the sole changed file in54-native-file tree.

Three real terminal negative cuts J202.18/.23/.24 each lose EXACTLY that named pad, preserving all others. Clock and VIO cuts yield1/76/0 with the precise topology-predicted upstream track_dangling UUID; ground cut0/76/0. Full native refill/reload and actual CLI used. Broken specimens excluded from release. Actual reconstruction and inverse unified patch restore all54 native files byte-for-byte; rollback real0/75/0. All verification/physical/reference/negative/raw/replay reports match normal and`-O`.

## Clock reference gap: route avoided, not filled or hidden
Independent0927 review localized the extra adjacent-AON-SDA clearance interaction to a0.000595034125mm² polygon. `reference_closure.py` tests that exact polygon: former In3 clock projection overlap0.000595034125, new overlap **0**. Adjacent AON_SDA via is unchanged. We rerouted the clock away; we did NOT delete the unrelated via, mask its clearance or claim the gap became filled.

Native normalized plane checks find **zero additional unchanged-signal projection loss versus0927**, retaining the1e−8mm² reporting threshold. Full per-net UNION uncovered reference changes:
- EXTCLK/In2 .1322377828255→.131597673675mm² (−.0006401091505).
- EXTCLK/In4 .291886615333→.2902158608205mm² (−.0016707545125).
- No other union change above1e−8mm².

Absolute nonzero coverage is still reported, not called zero or SI approval. Inherited D0/D1/D2 own-via-antipad coverage changes from0927 and older CAM reference history remain; this work does not reverse or qualify them. New clock routing avoids the specific reviewed adjacent gap, but all full-clock return/timing/EMI and actual load gates remain.

Total planar net lengths change: GND126.935798676→127.506342793mm; VIO101.566230802→101.568082019mm; EXTCLK44.5625→47.941958606mm (**+3.379458606mm**). Via counts unchanged. These are extracted lengths, not latency/skew or loaded-edge qualification. Whole affected path, not just via point, is checked for connectivity, copper and reference effects.

## Mechanical scope and residual process gates
Exact8684 mechanical screen is frozen separately at `assembly_tail_courtyard_review_20261030_1000`, manifest `179e798ecc2080e30cceaf0593ca2b183aec7e2e62225905d94cb1df93328352`; independent review remains separate. Native/full-budget screen finds VIO left-edge gap.5mm copper/.65mm drill; new VIO/GND nearest R501 retained installation projection≈.415017mm; clock.05mm to full J202 operating projection. New/changed outer tracks intersect only their intended J202 target/open budget, no unrelated modeled installation/wire budgets.

Native-courtyard clearance is NOT fabrication/process approval. The.05mm nominal clock-to-broad-envelope margin remains tolerance-sensitive. Unknown real FPC bend/insertion/tool/actuator travel, tenting/mask/plugs, connector seating, finished outline tolerance, fixture/probe access, wire strain relief and installation procedures remain gates. The **unchanged D0 via still overlaps the broad J202 open-envelope projection by.025mm**, though not the native courtyard/body; no claim every board via clears every operating budget. Old J104 probe-via process gate remains. Full body/operation budgets and RF exclusions were not shrunk.

## Reproduction / scope
Use isolated copy, `/usr/bin/python3` pcbnew9.0.2,kicad-cli,diff/patch: materialize.py,run_checks.py,verify.py,physical.py,reference_closure.py,negative.py,raw_delta.py,replay_rollback.py,render.py. `COURT_NATIVE_OUTPUT` redirects deterministic reconstruction; final model and parent SHA pinned. No correctness relies on assertions. negative.py writes JSON directly to avoid pcbnew SWIG teardown warning pollution; logs retain those warnings.

`manifest.json` explicitly allowlists final source/evidence only. Local exploration/alternate models/intermediate boards and negative native specimens are NOT release payload. No external upload, purchasing, fabrication, bridging or power actions. Parent frozen directories untouched. Camera/FPC identity, dynamic five-OE edges/load, loadedGPIO VOH, actual supply sequence/brownout, firmware provider, battery/charging, cost, thermal and manufacturing authorization remain unresolved.
