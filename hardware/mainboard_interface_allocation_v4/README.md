# v4 — physical interface source allocation, NOFAB

This is a new native **source-only** candidate. v3 and the routed `016d…` board are untouched. The selected mainboard source is `mainboard_projection/mainboard_revD.kicad_sch`; full core-system source is `system_master/mainboard_revD.kicad_sch`. Always open the top-level root, not the unused captured nested root.

## Actual source change

J103/J104/J105/J202 retain their original references and symbol UUIDs, but move to the explicit `physical_interfaces` hierarchy with the frozen interface library/footprint definitions. J110 is new. This deliberate sheetpath change must be propagated to PCB footprint source paths; do not merely compare reference text. All unrelated component metadata and every unrelated pin/net are preserved. Fixture ownership and all three fixture entities are unchanged; SW101/SW102 occur exactly once outside the mainboard.

**J202 is not pin-compatible with its old 18-position semantic symbol.** `pin_contract.json` contains every old net→new physical contact migration, including seven ground contacts. No numeric-pin continuation is allowed. Its new 24-contact interface is for a new custom flex/carrier only. The unknown 30-pin custom SC035HGS module remains mechanically/electrically isolated; no adapter or power-up approval is implied.

Fresh native XML results:
- core-system master: 94 entities / 392 endpoints, ERC 0;
- selected mainboard: 84 entities / 312 endpoints, ERC exit 5 with only the existing singleton VBUS_5V boundary warning (0 errors);
- external passive fixture: 3 entities / 7 endpoints, ERC 0.

Normal and optimized Python checks pass exact migration, retained source metadata, ownership, and four intentional negatives (numeric 18→24 mapping, raw camera-power substitution, raw-battery ADC connection, lost J202 ground). No PCB DRC/parity/routing result is claimed here. Actual physical placement and combined checks belong to a separately versioned PCB candidate.

## Full-system boundaries are not magically integrated

`system_ownership.json` preserves 96 mainboard/tail/fixture entities (84+9+3), and **separately scopes** original `pickup_contact`, `battery_adc_candidate`, and `camera_power_gate` sources by original path, source hash, namespace/reference, value and footprint. These pre-existing blocks are not copied onto the mainboard or counted as completed layout. This is not a complete purchasable-system BOM.

`cross_board_map.json` validates exact pickup J1 six-pin and safe ADC J2 two-pin mappings. J105 is an unprotected MCU input: never attach raw cell or pack voltage. The ADC block's protected-pack input, AON supply and qualified hardware-PG input remain distinct unresolved integration dependencies; JP1/JP2 remain OPEN.

**Important new verified limit:** the current camera power-gate native source has no physical input connector. J110's 3V3_AON/GND/CAM_PWR_EN nets can be traced precisely to gate U1.1/U1.2/R2.1, with explicitly named local-net aliases, but those component pins are NOT approved harness lands. A real gated-board input landing and physical integration remain necessary. Output JP1 is OPEN; unknown camera and unverified head rail/VIO sequencing remain isolated. No head regulators or VIO supply have been invented.

J104 remains camera-off-only UART service, no external power. J103 remains the exact pickup interface. Shared recovery-fixture cost is separately unquoted, not used to claim the 380 CNY per-pen or 760 CNY two-pen limit is met.

## Reproduce / freeze

`tools/build_v4.py` verifies both frozen parents and refuses overwrite. `tools/verify_v4.py` validates freshly exported XML and actual ERC reports; run normally and with `-O`. `tools/check_system_boundaries.py` checks external source hashes and exact endpoints, likewise normal/`-O`. All safety flags are explicit exceptions, not Python assertions. `source_versions.json` locks native roots, sheets, local libraries and XML; `manifest.json` locks this source package. No source suppression or missing-footprint deletion is used to hide unfinished interfaces.
