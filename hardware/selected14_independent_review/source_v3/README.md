# Option B selected — v3 system/source allocation and passive fixture candidate

**Decision:** prototype recovery uses the existing mainboard J108 EN/BOOT/GND service points plus an external passive recovery fixture, replacing the two proposed internal buttons. This new version does not modify v2 or the earlier concept freeze. It changes source ownership, not PCB geometry/copper. Selection is not assembly or safety qualification.

## Stable source switch point

Open only the top-level `mainboard_revD.kicad_sch` in the selected folder (nested source-library/archive files are not alternate top-level projects):

|Source|Entities / endpoints|Top-level schematic SHA256|
|---|---:|---|
|`system_master/`|93 /383|`1f744f9490a27f5da831fb1936ebeb8cf0d84dc675fad8c475144963dad5dae5`|
|`mainboard_projection/`|83 /303|`c2687211f6085fb0a4ca409a26983ed62a124c91ae4243455eccdd9a72bf6854`|
|`fixture_projection/`|3 /7|`848aa5b0da7a69d56f48cef667227946e8b9d0e0d0bcdf490537f8297dd7aa31`|

`source_versions.json` locks all native source files. The system retains every original380 endpoint/net identity; the only new endpoints are JF1.1 CHIP_EN, JF1.2 BOOT_N, JF1.3 GND. SW101/SW102 preserve original reference, value, symbol UUID and pin identities, but their instances now truly reside on the `recovery_fixture` sheet. Original MCU switch-connected stubs are removed explicitly. This is recorded in `design_change.json`, not an on-board flag change used to hide missing parts.

The mainboard keeps actual J108 and J109, AE101.2 NC and C106/C107 native0402+DNP. All other retained source value/footprint/library/sheet/UUID/properties remain unchanged. The fixture projection contains SW101 RESET, SW102 BOOT and the JF1 mating interface, all as real source components with presently unselected physical parts/footprints.

## Actual per-board status, not mathematical parity clearance

Fresh native ERC: system master0; fixture0; main projection exits5 with only the pre-existing singleton VBUS_5V boundary warning, zero errors. Normal and optimized identity/ownership checks pass, rejecting duplicated switch ownership, hidden sensor handoff, missing switch and added active driver.

Expected unplaced mainboard functions now comprise **J103/J104/J105/J202** only. This must be verified by pairing the selected projection with the actual routed PCB and running full native DRC/parity; this source task does not run or claim that PCB result. The complete system still contains the externally allocated fixture and tail components. Moving switches does not make an unfinished fixture physical hardware.

- J103 retains pickup/contact6-net interface:3V3_AON/GND/AON_I2C_SCL/AON_I2C_SDA/PICKUP_INT_N/NIB_CONTACT_N.
- J104 retains camera-off-only UART sharing CAM_RESET_UART_TX/CAM_PWDN_UART_RX/GND; no concurrent sensor drive.
- J105 retains BATTERY_ADC/GND with ADC input safety requirements.
- J202 remains `SENSOR_1V8_SEMANTIC_NOT_FPC`: required physical sensor handoff unresolved, not an approved18-pin connector or permission to eliminate those connections.

## Ownership and cost

`system_ownership.json` has95 uniquely owned entities:83 mainboard,9 selected tailRevB,3 shared fixture. SW101 and SW102 each appear **once**, exclusively fixture-owned. The two internal semantic connector entities are not physical BOM parts. Tail components use the previously checked selected RevB source rather than duplicate old generic master parts.

Fixture procurement lines are SW101, SW102 and JF1; switch/probe MPNs, footprints, jig, wire, enclosure/strain relief and ESD protection remain unqualified and are not bought. A **single shared fixture cost is separately unquoted**, not counted once per pen and not used to claim either pen fits380RMB or the two-pen760RMB ceiling. Its mechanical/assembly/test cost must be budgeted explicitly before procurement. DNP and source BOM-exclusion flags are preserved.

## Passive fixture implementation contract

`fixture_handoff_contract.json` fixes J108↔JF1 by both source version and signal identity:
- pin1 CHIP_EN: SW101 can only short it toGND;
- pin2 BOOT_N: SW102 can only short it toGND;
- pin3 GND: first-make/last-break reference, currently a requirement—not a proven mechanical feature.

No external supply, push-pull driver, charger CE permission or camera signal is added. Reference pad coordinates in the contract are from the captured prelayout board and are **not** a final mechanical mating drawing. Any pad move, width/layout change affecting fixture access or face/orientation change requires a new geometry contract. Equal pin numbers do not establish a physically safe mating orientation.

Before any power: verify versions, source-to-contact continuity, switch-open state, alignment and absence of shorts in a qualified ESD-controlled setup. Connect ground before signals, disconnect it last. If this order cannot be mechanically guaranteed, do not hot-mate; connect unpowered and validate the complete setup first. The fixture itself supplies no power; only the separately qualified pen power path may be used. Keep unknown camera disconnected and all charging commissioning bridges open.

For download-boot validation, GPIO0/BOOT must be low at reset release and GPIO46 must satisfy its low boot condition; EN/CHIP_PU low resets the MCU. The source preserves R10510k pulldown on U101.52/GPIO46, but reset/strap levels and timing require physical measurement. After strap sampling, release BOOT; for normal boot reset with BOOT released. USB recovery depends on actual tail/J109 data and ground continuity; UART recovery requires camera-off isolation. No flashing, erase, eFuse change, charging or physical hardware operation has been performed here.

Espressif's source basis: [boot-mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html), [schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html). Fixture ESD, contact resistance/bounce, clamp/keying, timing, reset efficacy and recovery across bad firmware remain verification gates.

## Rebuild boundary

`tools/build_v3.py` verifies the frozen v2 input manifest and refuses to overwrite an existing v3. It creates native system/main/fixture sources only; no PCB or copper is written. `tools/verify_v3.py` checks the captured exported native maps and exact allocation. Fresh native exports/ERC are recorded per folder. A later source change requires a new version and the same checks. Final routed-board and fixture hardware checks remain independent; these source results are not manufacturing release files.
