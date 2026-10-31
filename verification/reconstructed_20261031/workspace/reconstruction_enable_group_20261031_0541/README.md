# FROZEN-INCOMPLETE enable research checkpoint — NOT a replacement baseline

Selected native: `final_partial_candidate/mainboard_revD.kicad_pcb`
SHA256: `56e01aa105cc12dc7eb53cfb892ffddea806462878e7b8602cb1823f7d32b980`
Accepted design baseline remains **7522**, native0/37. This separate diagnostic is **0 violations /34 unconnected /0 parity**, only three local merges, NOT the proposed five-merge enable completion. NOFAB / NO POWER / providerNULL / JP201,JP202,JP301 OPEN.

## Actual connectivity, not count-based functional claims
- CAM_PWR_EN: U101.47(GPIO41)↔R106.1(100k) is joined; R302.1(1k)↔TP301.1 is separately joined. These two components remain DISCONNECTED.
- CAM_BUS_EN: U101.37(GPIO47)↔R108.1(100k) is joined; JP202.1 remains DISCONNECTED.
- No downstream open commissioning/power bridge is closed. No load-switch ON, SCCB EN, camera startup or safe-off functionality is established.
- All other old finite physical pad partitions unchanged; GND94/AON41/VIO12 cores preserved. Values/netlist/pinmap, all103 footprints/pads,104 installation budgets, exact99.8mm outline, native keepouts, stackup/rules/USB/pre-existing power tracks preserved.

## Exact source replacement / changes
28 parent tracks and2 parent vias replaced by207 tracks and9 vias. All added traces .15mm, vias .45/.20mm. Parent source changes are restricted to CAM_IO_EN, CAM_RESET_UART_TX and XCLK source-In3 approach; all other non-zone raw blocks exact. Parent footprints/pads and settings are raw-exact, not merely same reference count.
The RESET source now uses4.006636mm newIn2 crossing. It is not “unchanged PDN” just because power tracks are untouched. Unused proposed GPIO41 via, unused JP202 lead and four unused terminal-tail portions were removed before selection. No long enable-trunk trial copper is included.

Planar centerline paths (vertical via delay excluded):
- MCU47→R106:25.829826mm, F/B/F; R302→TP301:5.535660mm, B/In3/B.
- MCU37→R108:22.074057mm, F/B/F. These local bias connections are not complete operating-net trunks or qualified RC loads.
- Changed XCLK MCU43→U203.4:64.529953mm vs63.887797 parent (+.642156), same existing functional partition. No clock/timing equivalence claim.
- Changed IO_EN MCU48→JP201.1:80.755588mm vs80.009477 (+.746111).
- Changed RESET MCU49→U203.5:68.561116mm vs66.925530 (+1.635586), with source layer-transition change. Other source/control gates remain.

## Return / plane evidence and limits
3,888 retained conductor/reference projections have zero measured loss. This does NOT establish new-path SI/PDN acceptance: all13 new net/layer/reference unions and nonzero missing-reference areas are disclosed in `reference_checkpoint.json`; own-antipad versus shared/foreign causes have not been independently localized for this incomplete checkpoint.
Ground-plane material: each In1/In4 loses3.518245787237mm² and gains.5139632594465mm². AON In2 loses3.7750235199795mm² and gains.513963250488mm². AON remains one mainland with the same20 current AON-via memberships; the pre-existing(11.9,83.9) exception is unchanged. Actual current spreading/impedance and dynamic margins remain unqualified; island membership is not a current-density proof.

## Mechanical/process conditions — do not report blanket Fab/process pass
No new nonterminal full-installation-envelope area overlap was found in the mechanical diagnostic; all vias clear full bodies. But R302's new continuing route is nominally TANGENT to its retained full envelope (zero tolerance margin). TP301 is a measurement land with a native unfilled1×1mm Fab rectangle/.05stroke: two non-pad-ended continuations overlap its actual Fab stroke by .013335366357 and .0019380465195mm²; a third conservative Fab-bbox hit has actualstroke0. These are explicit unresolved land/process continuations, NOT blanket target waivers or proved solid collisions. Tool/probe/contact qualification remains open. GPIO47 continuation nominal full-U101 margin .060mm, ordinary courtyard passages and other small nominal margins are not fabrication approval. See separate exact mechanical package; no author claim overrides it.

## Why construction stopped
Initial ordinary F/In3/B joint search failed. Its automatic component diagnostics flagged artificial search boundaries; expansion y2.8..80.5→.5..89 still left source and lower components separated. This is finite .025mm-grid/mask evidence, NOT global impossibility. Read-only all-In2 via-site analysis found nearest relevant source/sink sites near y35.275/y45.85: ≥10.575mm vertical span in that model, not a short local crossover. The initial y36..43 window had no eligible transition sites. An already-running wider trial constructed one PWR trunk and failed BUS before the stop instruction arrived; that trial is explicitly rejected/not adopted and excluded from this manifest. No further routing after the parent's architectural stop.
Storage architecture may reassign these controls. Therefore retain accepted7522, preserve this limited diagnostic privately as research, and review storage feasibility before investing in additional enable routing/plane disruption. No schematic/pin/firmware changes adopted.

## Tests / reproducibility
Native fresh matched-project DRC0/34/0; finite all-pad/core checks; raw exact allowed-source replacement; unchanged outline/zone definitions/rules;33 native role/value/LayerSet assertions; normal/-O equality; fresh refill byte identity; reversible native replay both directions; three independent terminal-cut negatives in both modes. `regressions.json` contains12 aggregate gates. These are static model tests only. Construction trials are not deterministic-UUID replay authorities: the supplied raw reversible delta and selected native are authoritative.
Primary source applicability and open GPIO47 domain, GPIO41JTAG/default, TCA9517 loaded EN, Schmitt IO-enable, TPS22918 ON-before-VIN/CT/QOD and open-bridge constraints are in `source_roles.md`. The original sensor-role/power/service/clock/storage gates remain.
