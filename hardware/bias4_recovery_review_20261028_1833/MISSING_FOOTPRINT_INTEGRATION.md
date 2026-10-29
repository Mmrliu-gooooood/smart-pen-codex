# BIAS4: classify the 16 missing footprints before physical integration

2026-10-28 18:38 UTC. Read-only source classification, **NOFAB**. These are still 16 real schematic-parity findings; nothing was marked off-board, excluded, DNP, or deleted to suppress them. “Semantic” below describes design intent, not a native exemption or a completed physical port.

## Evidence keys

All paths relative to `smart_pen_next_20261028` unless explicitly stated.

- **N**: fresh native export `hardware/bias4_recovery_review_20261028_1833/fresh.xml`, exact pin/net and source sheet metadata; same source as BIAS4 `hardware/mainboard_resume_20261028/mainboard_revD.kicad_sch`.
- **U**: `hardware/usb_main_integration/README.md`, `contract.json`, `endpoints.csv` and `hardware/usb_tail_revB/usb_tail_revA.xml`.
- **I**: `docs/verification/MAINBOARD_REVD_SCHEMATIC_REVIEW_20261028.md`, especially different J102/J201 order and semantic camera-port restrictions.
- **P**: `../smart_pen_rebuild_20261028/hardware/pickup_contact/README.md` and native pickup source. Separate 12×20 mm test board, not proof of whole-pen packaging.
- **A**: `hardware/battery_adc_candidate/README.md`; conditional isolated ADC schematic, no finished PCB or qualified PG.
- **C-old**: `hardware/power_core_layout_candidate/README.md` and native XML: four-pin J5 includes CE permission.
- **C-new**: `hardware/power_integrated_layout_14x45/power_integrated_study.xml`, native J5 `MCU USB MODE / NO CE PORT`, three physical wire lands; latest integrated candidate.

## Classification by exact ref

| Ref | Source sheet | Native intent / actual state | Classification and required next action | Evidence / certainty |
|---|---|---|---|---|
| AE101 | `/mcu_core/` | `ANTENNA_TBD_NO_FOOTPRINT`; pin1 RF_ANT, pin2 GND; empty footprint | Genuine RF realization missing. Choose actual antenna architecture and land/keepout compatible with enclosure, battery and hand; then implement matching/return geometry and physical RF tests. A connector/port symbol is not an antenna design. | N; explicit TBD. Architecture not yet established. |
| L101 | `/mcu_core/` | `RF_MATCH_TBD`; pin1 RF_SIP, pin2 RF_ANT; empty footprint | Genuine matching-network placeholder. Select topology and footprint in conjunction with antenna and stackup; component value cannot be justified from ERC. Preserve C106/C107 DNP tuning intent and qualify RF network rather than blindly shorting RF_SIP. | N; explicit TBD, value/part unresolved. |
| SW101 | `/mcu_core/` | RESET; CHIP_EN to GND; empty footprint | Real service-operation element not realized. Decide accessible switch versus documented test-pad/pogo reset facility, implement physical access and resistor/reset timing, revise source honestly if topology changes. | N; service requirement represented, physical choice unknown. |
| SW102 | `/mcu_core/` | BOOT; BOOT_N to GND; empty footprint | Real recovery/programming-operation element not realized. Choose switch or factory pogo access and test boot/recovery; cannot remove only to reduce parity count. | N; physical choice unknown. |
| J101 | `/usb_entry/` | Older `USB4105-GF-A16P` USB-C symbol; absent mainboard | Separate-board owner identified: choose **one** USB tail candidate and keep one connector in system BOM. Tail B native candidate is `USB4105-GF-A-120`, not the old pseudo-MPN. Replace mainboard USB-front-end ownership with explicit tail hierarchy/interface; qualify tail B heel-trim assembly. | N, U; ownership explicit, final assembly not approved. |
| U102 | `/usb_entry/` | TPD4E05U06DQAR, old generic USON footprint; absent mainboard | Separate USB tail owner. Keep one ESD device, reconcile tail official-derived DQA footprint and optional external copper routing across internally NC pins; source not just five ref deletions. | N, U; candidate ownership established. |
| D101 | `/usb_entry/` | TPD1E10B06DYAR VBUS-to-GND TVS, old generic SOD523 footprint | Separate USB tail owner. Keep one TVS with qualified DYA geometry and local surge return; TVS is not sustained-overvoltage cutoff or fuse. | N, U; candidate ownership established. |
| R110 | `/usb_entry/` | USB_CC1 to GND, 5.1k 1% | Separate USB tail owner. Keep one independent CC1 Rd on tail, no duplicate mainboard loading. Final whole-system pin/net/BOM reconciliation needed. | N, U; explicit. |
| R111 | `/usb_entry/` | USB_CC2 to GND, 5.1k 1% | Separate USB tail owner. Keep one independent CC2 Rd on tail, do not short CC1/CC2 or infer 1.5/3A permission. | N, U; explicit. |
| J102 | `/usb_entry/` | `LOGICAL_CAMERA_ONLY_NOT_FPC`, 20 host-side signal/control pins; no supply/GND | Internal cross-source semantic boundary, not a second actual camera connector. After deciding single-board integration, replace redundant port representation with honest hierarchical connectivity; keep CAM_PWR_EN and ILLUM_STROBE destinations, which are not in J201. No 1:1 cable may be inferred. | N, I; semantic intent explicit, exact final hierarchy not yet implemented. |
| J201 | `/safe_bias_interfaces/` | `HOST_3V3_SEMANTIC`, 20 pins including 3V3_AON and GND; different ordering to J102 | Internal host/translator boundary in the already combined PCB. Same action as J102: reconcile actual ownership and source interfaces rather than placing a redundant connector simply to satisfy parity. If intentionally split again, define actual connector/pin map instead. | N, I; semantic intent explicit. |
| J202 | `/safe_bias_interfaces/` | `SENSOR_1V8_SEMANTIC_NOT_FPC`, 18 sensor-side pins including VIO/GND | Genuine camera-side physical interface still missing. Define connector/lands and verified as-built camera mapping, DVP bit mapping, voltage/clock/reset/trigger semantics and supply source. This is **not** the custom 30-pin order and not permission to directly energize it. | N, I; actual module interface qualification unresolved. |
| J103 | `/usb_entry/` | `PICKUP_INTERNAL`, 6 pins AON/GND/I2C/interrupt/contact | Real pickup/contact interconnect if keeping separate board; native order matches existing pickup J1. Alternatively integrate actual LIS2DW12/contact circuitry into mainboard source and copper. Need physical pads/connector, MEMS placement/strain, harness, sole I2C pull-ups, contact minimum-load qualification. | N, P; endpoint order established, mechanical/mainboard integration unresolved. |
| J104 | `/usb_entry/` | `UART_TEST_CAMERA_OFF_ONLY`, CAM_RESET_UART_TX, CAM_PWDN_UART_RX, GND | Factory/service test interface, not a required external user connector. Implement test pads/pogo or qualified connector and explicit camera-isolated test mode. Reused control GPIOs must not be driven by UART and camera simultaneously. | N; interface condition explicit, test access not realized. |
| J105 | `/usb_entry/` | `ADC_SAFE_EXTERNAL_ONLY`, BATTERY_ADC/GND | Conditional ADC interface. GPIO4/U101.9 exists, but required safe front-end/PG is still a schematic-only candidate with two OPEN bridges. Implement and qualify front-end plus physical connection, or explicitly defer monitoring in a new source revision. Never attach raw battery to this port. | N, A; ADC functionality not yet qualified or physically integrated. |
| J107 | `/usb_entry/` | `CHARGER_MODE`, pin1 USB_EN1, pin2 USB_EN2, pin3 GND | Real power-board control interface requiring physical mainboard lands/connector and harness. **Latest integrated 14×45 J5 matches logical order 1/2/3**, but routing, assembly and default-state/brownout verification remain. Do not reuse older four-pin J5 wiring blindly. | N, C-new; logical matching verified, physical host port absent. |

## Version-sensitive integration traps

1. **J107 ↔ power J5:** latest integrated 14×45 native J5 has 1=USB_EN1, 2=USB_EN2, 3=GND and explicitly **NO CE PORT**. Older standalone power-core J5 instead has 1=USB_EN1, 2=USB_EN2, 3=CE_PERMISSION_EXTERNAL, 4=GND. With that older board, mainboard J107.3 must map to old J5.4, never old J5.3. This report does not reintroduce an external CE port to the new integrated board.
2. **J102 ↔ J201:** they share many net names but not pin sequence or full membership. J102 has CAM_PWR_EN/ILLUM_STROBE; J201 instead includes AON/GND. Do not build a pin-for-pin 20-way cable.
3. **USB front end:** five tail-owned components must not appear twice in final purchase/assembly BOM. R112/R113 stay mainboard-side and tail DP/DM reach their **pre-series-resistor** pins. Existing resistor pads are not automatically approved solder-wire ports; add actual mainboard DP/DM/return interface.
4. **Camera semantics:** J202 is 18 logical sensor-domain pins, not the 30-pin custom factory FPC. Neither netlist union nor successful DRC resolves its physical voltage/mapping uncertainty.

## Prioritization

- Treat the 16 findings as **4 real unresolved service/RF components + 5 explicitly tail-owned components needing source ownership reconciliation + 7 semantic/physical-interface decisions**. This count is classification, not permission to waive any of them.
- First produce one system ownership/connector contract and actual primary-board USB/pickup/power/camera endpoints. Fixing only the last four routed joins would still leave unusable physical interfaces.
- RF and physical camera qualification remain major blockers. ADC may remain explicitly deferred and open, but cannot be reported as working monitoring. RESET/BOOT must retain a tested recovery route even if not user buttons.
- Then regenerate native netlist/ERC/multi-board pin contracts, BOM and PCB parity and review actual assembly fit. No source or parity settings changed in this review.
