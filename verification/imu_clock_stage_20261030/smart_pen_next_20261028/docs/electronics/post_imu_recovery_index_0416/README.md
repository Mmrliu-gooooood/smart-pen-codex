# d6c913 native recovery index — READ ONLY / NO FAB / NO POWER

**Actual current state: 0 DRC violations / 120 unconnected / 0 schematic parity.** This inventory does not instruct commissioning or bridge any intentionally OPEN interface. No copper or frozen files changed.

## Source and identity

- PCB `hardware/imu_j107_clock_native_0405/native/mainboard_revD.kicad_pcb`, SHA `d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22`; native manifest `ca5ec099df919088b81b3a3d0c2d7f9da981e07728cb4626162355aa5da83ab4`.
- Physical components are calculated from actual native finite copper including filled planes, real pad layers and via drills. Raw DRC airwire endpoints are mapped by object UUID, not description-only or nearest pad.
- `embedded_audit.json` directly parses every retained schematic lib_symbols definition and instance; matches 364 electrical physical pads to pin number/function/type and source sheet/lib/UUID. Unnumbered mechanical pads are explicitly excluded from electrical-symbol expectations. The schematic tilde `~` means intentionally unnamed pin and exports as an absent netlist pinfunction; it is not inferred as a functional GPIO. PCB GetPinFunction was not used.
- J107 remains B origin `(5.2,84),180°`; USB_EN1 pad `(4,81.5)`, USB_EN2 `(4,83.9)`, GND `(4,86.3)` — all three still isolated. Moving port did NOT complete charger mode control.
- EXTCLK keeps U203.13↔J202.18; old B segment x4.25,y78.6..90.5 replaced with B stubs + In3 y79.7..89.4, two0.45/0.20 vias. R235.1 bias attachment is still unconnected, so `SENS_EXTCLK:1` does not mean that restored main chain broke.
- R503 retained47k1%,MPN RC0603FR-0747KL,origin `(2.5,11.5)`, pad1=AON,pad2=NIB_CONTACT_N; source value/MPN/pose/nets independently verified in native predecessor rollback audit.

## All 120 airwires by net

|Net|DRC missing links|Physical pad components|Source sheet categories|
|---|---:|---:|---|
|3V3_AON|4|5|/camera_gate_on_main/, /controls_sccb/, /dvp_translation/, /mcu_core/, /pickup_on_main/, /safe_bias_interfaces/, /usb_entry/|
|AON_I2C_SCL|2|3|/mcu_core/, /pickup_on_main/|
|AON_I2C_SDA|2|3|/mcu_core/, /pickup_on_main/|
|BATTERY_ADC|1|2|/mcu_core/, /physical_interfaces/|
|CAM_BUS_EN|2|3|/controls_sccb/, /mcu_core/|
|CAM_D0|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_D1|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_D2|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_D3|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_D4|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_D5|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_D6|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_D7|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_HREF|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_IO_EN|2|3|/controls_sccb/, /mcu_core/|
|CAM_ISO_OE_N|6|7|/controls_sccb/, /dvp_translation/|
|CAM_PCLK|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_PWDN_UART_RX|3|4|/controls_sccb/, /mcu_core/, /physical_interfaces/, /safe_bias_interfaces/|
|CAM_PWR_EN|3|4|/camera_gate_on_main/, /mcu_core/|
|CAM_RESET_UART_TX|3|4|/controls_sccb/, /mcu_core/, /physical_interfaces/, /safe_bias_interfaces/|
|CAM_SCL|2|3|/controls_sccb/, /mcu_core/, /safe_bias_interfaces/|
|CAM_SDA|2|3|/controls_sccb/, /mcu_core/, /safe_bias_interfaces/|
|CAM_VSYNC|2|3|/dvp_translation/, /mcu_core/, /safe_bias_interfaces/|
|CAM_XCLK|2|3|/controls_sccb/, /mcu_core/, /safe_bias_interfaces/|
|CONTACT|1|2|/pickup_on_main/|
|GND|34|35|/camera_gate_on_main/, /controls_sccb/, /dvp_translation/, /mcu_core/, /physical_interfaces/, /pickup_on_main/, /safe_bias_interfaces/, /usb_entry/, /usb_main_port/|
|IO_ENABLE_LINK|1|2|/controls_sccb/|
|NIB_CONTACT_N|3|4|/mcu_core/, /pickup_on_main/|
|PICKUP_INT_N|1|2|/mcu_core/, /pickup_on_main/|
|SENS_D0|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_D1|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_D2|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_D3|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_D4|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_D5|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_D6|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_D7|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_EXTCLK|1|2|/controls_sccb/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_HREF|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_PCLK|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_SCL|2|3|/controls_sccb/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_SDA|2|3|/controls_sccb/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_TRIG_IN|2|3|/controls_sccb/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_VSYNC|1|2|/dvp_translation/, /physical_interfaces/, /safe_bias_interfaces/|
|SENS_XSHUTDN_N|2|3|/controls_sccb/, /physical_interfaces/, /safe_bias_interfaces/|
|UNUSED_A_INPUT|1|2|/controls_sccb/, /dvp_translation/|
|UNUSED_B_INPUT|1|2|/dvp_translation/|
|USB_EN1|1|2|/mcu_core/, /usb_entry/|
|USB_EN2|1|2|/mcu_core/, /usb_entry/|

Counts are DRC missing connections, NOT number of missing pins or missing whole functional subsystems. `index.json` contains every physical pad component with ref/value, exact pad position/layers, source function/type/sheet and all120raw endpoint mappings.

## 3V3_AON: 35/39 core pads; 4 outside

|Physical pad|Value|Other net(s) on component|Source sheet / definition locator|Pad xy mm|
|---|---|---|---|---|
|R203.2|10k 1%|CAM_ISO_OE_N|schematic/controls_sccb.kicad_sch / ISO:R|[10.325, 72.0]|
|R501.1|10k 1%|AON_I2C_SCL|schematic/pickup_on_main.kicad_sch / Pen:S_R1|[1.775, 86.5]|
|R502.1|10k 1%|AON_I2C_SDA|schematic/pickup_on_main.kicad_sch / Pen:S_R2|[4.825, 86.65]|
|R503.1|47k 1%|NIB_CONTACT_N|schematic/pickup_on_main.kicad_sch / Pen:S_R3|[1.675, 11.5]|

Every outside-core pad listed here is a singleton physical component in this native board; no hidden already-connected subgroup is counted as separate routing work.
## GND: 68/102 core pads; 34 outside

|Physical pad|Value|Other net(s) on component|Source sheet / definition locator|Pad xy mm|
|---|---|---|---|---|
|C504.2|1n C0G|NIB_CONTACT_N|schematic/pickup_on_main.kicad_sch / Pen:S_C4|[5.025, 9.75]|
|J103.2|DRY CONTACT PADS|CONTACT|schematic/pickup_on_main.kicad_sch / Pen:S_J2|[5.4, 52.0]|
|J104.3|UART_SERVICE_CAMERA_OFF_ONLY|CAM_PWDN_UART_RX, CAM_RESET_UART_TX|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT3|[10.0, 56.6]|
|J105.2|ADC_SAFE_FRONTEND_LINK_NOT_RAW_BATTERY|BATTERY_ADC|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT2|[4.4, 77.5]|
|J107.3|CHARGER_MODE|USB_EN1, USB_EN2|schematic/usb_entry.kicad_sch / MCU:PORT3|[4.0, 86.3]|
|J202.1|5034802400_NEW_24PIN_SENSOR_HANDOFF|, SENS_D0, SENS_D1, SENS_D2, SENS_D3, SENS_D4, SENS_D5, SENS_D6, SENS_D7, SENS_EXTCLK, SENS_HREF, SENS_PCLK, SENS_SCL, SENS_SDA, SENS_TRIG_IN, SENS_VIO_1V8, SENS_VSYNC, SENS_XSHUTDN_N|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT24|[12.75, 90.5]|
|J202.10|5034802400_NEW_24PIN_SENSOR_HANDOFF|, SENS_D0, SENS_D1, SENS_D2, SENS_D3, SENS_D4, SENS_D5, SENS_D6, SENS_D7, SENS_EXTCLK, SENS_HREF, SENS_PCLK, SENS_SCL, SENS_SDA, SENS_TRIG_IN, SENS_VIO_1V8, SENS_VSYNC, SENS_XSHUTDN_N|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT24|[8.25, 90.5]|
|J202.13|5034802400_NEW_24PIN_SENSOR_HANDOFF|, SENS_D0, SENS_D1, SENS_D2, SENS_D3, SENS_D4, SENS_D5, SENS_D6, SENS_D7, SENS_EXTCLK, SENS_HREF, SENS_PCLK, SENS_SCL, SENS_SDA, SENS_TRIG_IN, SENS_VIO_1V8, SENS_VSYNC, SENS_XSHUTDN_N|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT24|[6.75, 90.5]|
|J202.17|5034802400_NEW_24PIN_SENSOR_HANDOFF|, SENS_D0, SENS_D1, SENS_D2, SENS_D3, SENS_D4, SENS_D5, SENS_D6, SENS_D7, SENS_EXTCLK, SENS_HREF, SENS_PCLK, SENS_SCL, SENS_SDA, SENS_TRIG_IN, SENS_VIO_1V8, SENS_VSYNC, SENS_XSHUTDN_N|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT24|[4.75, 90.5]|
|J202.4|5034802400_NEW_24PIN_SENSOR_HANDOFF|, SENS_D0, SENS_D1, SENS_D2, SENS_D3, SENS_D4, SENS_D5, SENS_D6, SENS_D7, SENS_EXTCLK, SENS_HREF, SENS_PCLK, SENS_SCL, SENS_SDA, SENS_TRIG_IN, SENS_VIO_1V8, SENS_VSYNC, SENS_XSHUTDN_N|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT24|[11.25, 90.5]|
|J202.7|5034802400_NEW_24PIN_SENSOR_HANDOFF|, SENS_D0, SENS_D1, SENS_D2, SENS_D3, SENS_D4, SENS_D5, SENS_D6, SENS_D7, SENS_EXTCLK, SENS_HREF, SENS_PCLK, SENS_SCL, SENS_SDA, SENS_TRIG_IN, SENS_VIO_1V8, SENS_VSYNC, SENS_XSHUTDN_N|schematic/physical_interfaces.kicad_sch / SmartPenInterfaces:PORT24|[9.75, 90.5]|
|R104.2|10k 1%|STRAP_GPIO45|schematic/mcu_core.kicad_sch / MCU:R|[4.325, 1.7]|
|R206.2|10k 1%|UNUSED_B_INPUT|schematic/dvp_translation.kicad_sch / ISO:R|[9.825, 46.0]|
|R214.2|100k 1%|CAM_D4|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[2.9, 33.725]|
|R216.2|100k 1%|CAM_D6|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[8.325, 28.0]|
|R218.2|100k 1%|CAM_PCLK|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[5.325, 41.5]|
|R219.2|100k 1%|CAM_VSYNC|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[8.325, 41.5]|
|R220.2|100k 1%|CAM_HREF|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[2.85, 45.0]|
|R221.2|100k 1%|CAM_XCLK|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[3.825, 56.0]|
|R222.2|100k 1%|CAM_RESET_UART_TX|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[6.825, 56.0]|
|R223.2|100k 1%|CAM_PWDN_UART_RX|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[6.825, 58.6]|
|R224.2|100k 1%|SENS_D0|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[2.325, 39.1]|
|R225.2|100k 1%|SENS_D1|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[5.325, 43.3]|
|R226.2|100k 1%|SENS_D2|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[8.325, 44.0]|
|R227.2|100k 1%|SENS_D3|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[11.325, 44.0]|
|R228.2|100k 1%|SENS_D4|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[2.325, 40.9]|
|R229.2|100k 1%|SENS_D5|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[5.325, 40.9]|
|R230.2|100k 1%|SENS_D6|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[8.325, 40.9]|
|R231.2|100k 1%|SENS_D7|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[11.325, 40.9]|
|R232.2|100k 1%|SENS_PCLK|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[11.425, 50.9]|
|R233.2|100k 1%|SENS_VSYNC|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[2.325, 50.9]|
|R234.2|100k 1%|SENS_HREF|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[8.325, 50.9]|
|R235.2|100k 1%|SENS_EXTCLK|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[11.425, 60.6]|
|R237.2|100k 1%|SENS_TRIG_IN|schematic/safe_bias_interfaces.kicad_sch / ISO:R|[5.325, 62.0]|

Every outside-core pad listed here is a singleton physical component in this native board; no hidden already-connected subgroup is counted as separate routing work.

## Next bounded subsystem proposals — topology only, no route feasibility claim

|Priority/scope|Exact missing connections|Boundary / reason|
|---|---|---|
|1. Dry-contact pressure input|7: R503.1→AON(1),C504.2/J103.2→GND(2),CONTACT(1),NIB_CONTACT_N(3)|Source GPIO2=U101.7. Finish whole switch/filter/pullup chain instead of just47k supply. J103→R504 remains physically long; geometry/EMI/debounce/test still required. No structural move approved here.|
|2. IMU control and wake|7: R501.1/R502.1→AON(2),AON_I2C_SCL(2),AON_I2C_SDA(2),PICKUP_INT_N(1)|U101.10 GPIO5↔U501.1 SCL; U101.11 GPIO6↔U501.4 SDA; U501.12 INT1↔U101.6 GPIO1. Power-complete is NOT prewake-functional; firmware/sleep mode checks remain.|
|3. Translator OE control|7: R203.2→AON(1),CAM_ISO_OE_N(6)|Join Q201.3,R203.1,U201.22,U202.14/.15,U203.14/.15; preserve voltage/power-sequence safety. Other enable controls are separate work, so do not claim full camera safety complete.|
|Small isolated option: charger-mode external port|3:USB_EN1(1),USB_EN2(1),J107.3GND(1)|U101.24 GPIO18/U101.27 GPIO21 to moved port. PCB-only closure does not qualify external charger behavior, harness or battery charging.|
|Subsequent MCU↔translator DVP|24:CAM_D0..D7,HREF,PCLK,VSYNC,XCLK each2|Existing translator↔J202 twelve chains remain; separate MCU-side connections and100k bias branches are not done. Preserve all prior branches, safe-bias returns and signal references; timing not certified.|

Full camera sensor-side bias/ground closure must include the remaining21safe-bias GND resistor endpoints and corresponding individual signal attachments, six additional J202 ground pins, control links and external rail/sequence constraints. An independently completed signal chain does not mean these bias/return paths are complete.

**Do not short JP301:** `OPEN / DO NOT BRIDGE` is retained. Its two pads belong to distinct commissioning nets; “zero airwires” cannot justify bridging it. JP201/JP202 and other commissioning links require their own source/safety decision; planned same-net wiring to a pad is not permission to close the link. Unknown camera remains disconnected.

## Scope / reproducibility

`build.py` and normal/optimized JSON agree. `embedded_audit.py` directly audits source functions. All categories retain their source sheet instead of classifying from an empty footprint function field. The JSON is the complete staging index; this README is the priority view. These are proposed work packages, not manufacturability approval, route trial or new upload.
