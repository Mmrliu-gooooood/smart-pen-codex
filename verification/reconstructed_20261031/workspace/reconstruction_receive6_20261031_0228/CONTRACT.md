> Original six-link planning contract. The selected frozen scope is PCLK+HREF four closures, with all new VSYNC stubs removed; README.md and final reports govern the selected result.

# NEW receive-six reconstruction — research only

Parent: exact c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855, independently accepted static 0/49/0 and privately roundtrip-backed-up. This is not recovery of lost historical receive copper. No frozen baseline changes.

## Intended six closures
| Net | MCU input | Enabled U202 A-port output | B.Cu-mounted 100k output bias |
|---|---|---|---|
| CAM_PCLK | U101.21 / GPIO15 | U202.4 / 1A1 | R218.1 |
| CAM_VSYNC | U101.22 / GPIO16 | U202.5 / 1A2 | R219.1 |
| CAM_HREF | U101.23 / GPIO17 | U202.6 / 2A1 | R220.1 |

U202 is SN74AXC4T245 PW16, with DIR low: enabled signal direction is sensor-domain B to AON-domain A. This is independent of the physical B.Cu resistor mounting side. OE, sensor identity, actual power sequencing, loads and receiver configuration remain unresolved. The 100k resistors add output load/stubs; they are not evidence of an otherwise floating input. AXC4 has typical 71k internal pulldowns, not the AXC8 figure.

Authoritative references: https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf (SCES877B, April 2024); https://documentation.espressif.com/esp32-s3_technical_reference_manual_en.pdf (LCD_CAM through GPIO matrix); https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html ; PICO SiP pin mapping must be checked against the source native/netlist, not bare-chip package numbering. GPIO15/16 also have RTC/32k crystal functions: input ownership and firmware must explicitly exclude incompatible use. GPIO17 input ownership also must be configured. No GPIO reassignment.

## Bounded alterations
R230 moves F to (11.1,34.25),90deg; R219 moves B to (6.2,39.5),0deg. R230.1 SENS_D6 remains an isolated bias leaf, as in the actual baseline. No extra sensor closure. R231 stays fixed. Exact full104 bodies/heights and actual pad/net contracts retained. Two-pose independent mechanics package 0236 applies, not lost historical poses.

C104 direct 2.55mm/.254 F supply connection and existing AON stitch (5.4,14.75) retained. Its GND stitch moves to (7.85,15.2), .6/.3, with .15 F terminal lead. Lead 1.231107225mm; nearest selected straight GND-anchor span 3.716517187mm. Sum increases .568922738mm versus original. This is a geometric trade, NOT proven PDN equivalence or improvement. Final filled-plane corridors/cores must be rechecked. USB, CHIP_EN, BOOT and all eight data paths retain logical connectivity; no convenience USB move.

## Search and verification policy
Signal width .15, through-vias .45/.2 initially; native rules and stackup unchanged. Full maximum-body/installation envelopes, foreign pads/copper and explicit native keepouts are hard exclusions. Ordinary courtyard-only overlap is disclosed as a process gate, not automatically a body collision or fabrication approval. Extra .1mm trace/body and .2mm via/body goals are exploratory, not manufacturer/user requirements.

Initial no-path results included a Python wrapper bug: native PCB_VIA objects returned from connectivity can be PCB_TRACK wrappers. Anchors now use GetClass and actual available layers, with regression fixture. This is an algorithm correction, not invalidation of already reviewed native boards. Six trunk orders and two bias-first orders are bounded diagnostics, not mathematical impossibility proofs.

An explicit crossover trial permits In2 only inside x4..8.5,y13.5..19mm. In2 is AON mixed plane, NOT GND. No unconditional use or acceptance: require actual current AON filled island/thermal/feed continuity, GND returns, retained-reference differences and all-native finite checks. Partial paths/stubs are diagnostic only; no adoption until coherent group validation.

Final gates: native refill/reload, DRC/parity, all old physical partitions and GND94/AON41/VIO12, exact declared delta, source pin/domain checks, new-path lengths/layer transitions/bias stubs, retained and new references, explicit C104 return trade, normal/-O checks and negative cuts/replay, full finite mechanics/keepouts, independent joint review and private checkpoint. PCLK-data translator skew, edge-dependent coupling, loaded VOH, actual setup/hold/polarity/clock rate and sensor timing remain unqualified. NOFAB, NO POWER, provider NULL, JP201/202/301 OPEN; actual99.8mm/fullRF retained.
