# Independent full review — control/service7522

**ACCEPT scoped static research: exactly four control/service physical joins.** This is not a validated sensor PWDN implementation, operating UART/camera-control result, SI/PDN, power, process or fabrication approval. NOFAB / NO POWER / provider NULL / JP201, JP202, JP301 OPEN.

PCB `7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1`; author manifest `bec167d27945b9d4af03171fd7f0c457315ffc82333d178ececc6063f2f86614`, all192files verified before isolated allowlist copy and again at close. Source remained untouched.

## Independently reproduced

- Fresh actual KiCad9 all-track/schematic-parity DRC **0/37/0**, from688 baseline0/41/0. Exactly two3→1 partitions, four joins, merging MCU49/J104.1 with existing U203.5/R222 and MCU50/J104.2 with U203.6/R223. All other pad partitions retained; GND94/AON41/SENS_VIO12.
-311 native/physical/source contracts normal/-O; full finite candidate screen, native contract, source roles, raw contract,9 wrapped-via fixtures, boundary/window regressions;42 aggregate gates normal/-O. Eight model families equal normal/-O, including exact allowlist-only6902 junction reconstruction.
- Fresh schematic XML pin/net/function map equal author source; actual U101.49 GPIO43_U0TXD, .50 GPIO44_U0RXD; CPU supply U101.46=AON. Actual U203SN74AXC4T245PWR and R222/R223100k1% values verified. No generic-module pin substitution.
- Own raw parser verifies UUID uniqueness,483new objects=476tracks+7vias, zero old removals, only retained filled-zone blocks change. All52 non-PCB project/source files byte-identical. Author raw contract additionally confirms all2,872 old non-zone top-level blocks exact, including non-UUID fields. No pose, value, old power/USB or rule change; fill changes are real.
- Four independently recreated saved/refilled/reloaded terminal cuts **in both Python modes**, preserving all unrelated partitions. MCU49, MCU50 and J104.1 each yield1 track_dangling/38 unconnected/0 parity; J104.2 yields **0 violations/38 unconnected/0 parity**. That last cut must not be called an electrical pass merely because it has no dangling warning. Own specimen hashes and results match across modes. Author saved-cut pipeline also reproduced all8 results.
- Own bidirectional raw replay checks **53 native files**, forward exact7522 with actual0/37/0; inverse exact688 with actual0/41/0. `.kicad_prl` excluded, not assumed54files. Matched project refill/reload normal/-O byte-exact selected7522.
- Own selected matched-refill counterfactuals NONE/edge-via/IO_EN-source/In2-track removal equal frozen advisory results. Current power cores, actual-via corridors, U202→U203 constructive feed corridors and actual plane-island memberships equal advisory. Independent all12terminal path/private-arm articulation results equal advisory.

## Explicit remaining engineering gates

Actual DIRhigh/OElow routes U203.5→.12 SENS_XSHUTDN_N and .6→.11 **SENS_TRIG_IN**, not validated power-down. Existing B.Cu-mounted100k parts pull down A-input nets; their placement side is not the translator B port. Provider polarity, voltage and reset/trigger timing remain unknown.

GPIO43/44 UART0 defaults, reset weak pullups and ROM/bootloader activity are relevant before application control mux.100k does not prove safe startup-low. Service camera-off label does not enforce isolation; external adapter TX can contend with camera-mode GPIO44 output. No5V/RS232, live service or hot-plug approval. Espressif499Ω TX recommendation is absent and unresolved for UART/EMI claims; no silent component/eFuse change. TI AXC4 input edges≤10ns/V, loaded thresholds, power/OE sequencing, actual firmware/cable/probe loads and sensor pulse requirements remain unqualified. Primary sources and precise scope are linked in frozen advisory0521.

3,363 retained projections have no measured loss, but AON main island area drops1.886450566711mm² and each ground layer loses3.0987258113445mm². One current main AON island/same20via memberships and examined feed paths remain; this is not unchanged impedance/current capacity. Old C104/power tracks exact does not prove unchanged PDN.

Shared-source holes have foreign IO_EN influence: remove-only IO_ENsourcevia counterfactual recovers RESET B .0014289556225mm². PWDN edge-connected own-antipad at13.35,37.025 explains .0672331491835B/.0649894137275In3 outside-enclosed-hole areas. This distinguishes causes, not harmlessness. Other tiny foreign grazes, secondary AON absence, raw polygon numerical floors and nonadditive shared-hole effects remain explicit, without arbitrary zero-projection manufacturer criteria.

MCU→U203 nominal planar lengths66.925530/74.345167mm,3/5 actual layer transitions. True service private arms2.345722/2.024846mm; true bias arms6.264474/8.848699mm. All were junction-removal tested against the other three terminals. Shared U203→bias paths21.157251/15.878596mm are not pure stubs. Vertical barrel delay, external cable and loaded edge/coupling are not included; no timing acceptance.

## Separately bound independent geometry

Mechanical0524 manifest `767f9b90fac6214d1dc45ed15f817281f616d27770f4468c8e42025ee05ceb58`, all28files verified; exact author192/7522 binding. Full body/Fab/native keepout screens and actual J104 terminal scopes accepted separately, not reclassified as electrical evidence. Four narrow terminal escapes, ordinary court projections and nominal .15mm C202 via/body gap remain explicit; no uniform.2mm rule, supplier tolerance, via-underbody/tenting or probe/tool access waiver. Saved CAD applicability is separate from a newly saved7522 assembly claim.

Frozen advisory0521 manifest `ac111af161fa07cd7665c71f2321206209f869f5530afeff69005942ba6e871c`, all60files verified. Both closures are dependencies, not claims of powered functional validation. Private checkpoint/adoption awaits parent joint decision.
