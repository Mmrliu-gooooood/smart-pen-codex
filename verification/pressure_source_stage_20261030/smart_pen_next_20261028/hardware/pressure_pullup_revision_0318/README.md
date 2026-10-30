# R503 conditional minimum-load correction — 2026-10-30 03:18 UTC revision

**Engineering candidate only: NOFAB / NOPOWER. Not a complete pen or qualified pressure interface.**

## Erratum and active source
The prior `mcu_supply_access_candidate_0300` R503 **100k 1%** is insufficient for the ALPS SPVE110100 minimum resistive load of 50 µA at 3 V. It had no specified supplier MPN; none is retrospectively invented. Frozen prior sources and reports remain unchanged. This new candidate supersedes only that R503 selection. This erratum must accompany any old pressure-interface or BOM description; it does not invalidate unrelated source evidence.

Active native files are under `native/`. Base board SHA-256: `8fe809b685633dd86dddc36ec33961d61ef7fad9fca52286bc47bd72a4f614e5`. New board SHA-256: `6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c`.

### Allowed source-delta contract
Only R503's instance Value (`100k 1%` → `47k 1%`) and previously absent hidden MPN field (`RC0603FR-0747KL`) change in:
- `native/mainboard_revD.kicad_pcb`
- `native/schematic/pickup_on_main.kicad_sch`

All other native files, wiring, nets, footprints, positions, pads, tracks, vias, zones and geometry are unchanged. The generic embedded library symbol's default value stays unchanged; the specific placed R503 instance overrides it. `source_delta.json` records old/new instance block hashes. `materialize.py` reproduces the exact approved transformation, and `verify.py` rejects any extra change rather than treating the whole source as byte-identical.

`checks/candidate/bom.csv` is the full KiCad-generated BOM with MPN column; `BOM.csv` is its identical convenience copy. Other previously unspecified MPNs remain blank and are **not** newly qualified. Netlist is `checks/candidate/netlist.xml`.

## Primary-source selection
Selected **YAGEO RC0603FR-0747KL**, 47 kΩ ±1%, 0603/1608, 0.1 W at 70 °C, 75 V maximum continuous working voltage, ±100 ppm/°C, operating −55 to +155 °C. Body 1.6 ±0.1 × 0.8 ±0.1 × 0.45 ±0.1 mm. These nominal package specifications fit the existing 0603 resistor footprint class; actual assembly, land-pattern/process and mechanical checks are still required. No procurement or current-price claim is made. Official exact-part specification (accessed 2026-10-30):
https://www.yageogroup.com/component-documentation/download/specsheet/RC0603FR-0747KL

ALPS official SPVE110100 specification gives minimum resistive rating 50 µA / 3 V and 50,000 operating cycles:
https://tech.alpsalpine.com/e/products/detail/SPVE110100/

The existing pressure audit is `../../docs/electronics/pressure_contract_audit_0312/REPORT.md`; its manifest SHA-256 is `476b28cb3f2beba4b0644d89b34b946607ff69cef3710b2e88e5fcf7059775c2`.

## Calculation, not qualification
Closed contact path: AON → R503 → NIB_CONTACT_N → R504 1k ±1% → CONTACT → switch → GND. R504 and C504 1n C0G stay unchanged.

At AON **3.0–3.6 V**, both resistor tolerances ±1%, contact resistance 0–1 Ω:
- 47k: minimum `3/(47000*1.01+1000*1.01+1)` = **61.8799 µA**; maximum `3.6/(47000*.99+1000*.99)` = **75.7576 µA**.
- 100k negative case: maximum at 3.6 V and both resistors −1% is only **36.0036 µA**, below 50 µA.
- Conservative within-this-model R503 dissipation maximum ≈ **0.267 mW**, well below 0.1 W nominal rating; full-temperature derating is not qualified here.

This is room-temperature tolerance-only resistive screening, excluding leakage and temperature drift. The actual AON rail must remain ≥3 V at the switch rating; sufficient calculated current below 3 V would not satisfy the stated voltage rating. Actual voltage range, GPIO thresholds, contact life, mechanical actuation, bounce/debounce, noise/ESD, leakage and temperature performance still require verification. The microsecond RC is not switch debounce.

Firmware must use **GPIO2 / RTC_GPIO2**, not GPIO7 (the relevant package pad number is 7). Physical connector station B52 versus virtual B70.5 remains unresolved; no routingwholepressure claim is made. Existing firmware board provider is absent, so wake/readout is not demonstrated. ESPressif primary references:
https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf
https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/sleep_modes.html

## Executed checks
KiCad CLI 9.0.2. Full commands and exit statuses are in `cli_results.json`; base and candidate outputs retained.
- Actual all-track DRC with schematic parity: **0 violations / 134 unconnected / 0 parity**, both base and candidate. Exit 5 is expected from unresolved unconnected errors, not success for manufacture.
- Actual ERC: **0 errors / 1 existing warning** (`VBUS_5V` dangling global label), identical both versions.
- Full 102 components, 90 nets, exact net/pin/function mapping and library content; only declared R503 component and BOM value/MPN delta.
- Normal Python and `python -O` verification pass. Negative old-value/wrong-MPN/missing-MPN contracts are rejected; they use runtime checks, not removable assertions.
- Rebuilt native bytes are identical (`replay_and_negative.json`). Native PCB-only 100k counterfactual versus 47k schematic produces actual **0/134/1** DRC, correctly detecting R503 parity mismatch.
- KiCad selected different representative endpoints for **8** airwires despite unchanged raw copper/pads/nets. Full raw differences are retained in `drc_unconnected_raw_difference.json`; per-net unconnected counts are identical. Raw airwire JSON is explicitly **not** claimed identical. Initial overly strict validation failures are retained as `verify_rejected_*` logs.

## Rollback and remaining gates
Rollback means choose the untouched base candidate, not edit frozen files; note that doing so restores the known 100k load defect. `replay/` is reproducibility evidence and `native_negative/` is deliberately invalid evidence, neither is a manufacturing release.

JP301 commissioning links remain **OPEN**. Do not energize unknown camera or battery/charging hardware. All existing unresolved 134 connections, courtyard/short-escape/EP-hole and manufacturing gates remain inherited. No physical test, welding, charging, fabrication, GitHub push or procurement was performed by this revision. Continue source/layout work and independent review before considering fabrication; the complete product remains unfinished.
