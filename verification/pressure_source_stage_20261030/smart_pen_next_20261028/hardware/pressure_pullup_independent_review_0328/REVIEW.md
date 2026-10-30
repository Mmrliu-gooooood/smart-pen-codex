# Independent source-only R503 correction review

**NOFAB / NOPOWER. Conditional minimum-load correction, not pressure-interface/product qualification.**

Reviewed author197-file manifest `36e709e63bcb4f2ba8dd913a1e93b2e5abcbe6cfa1c3d99f37a22ebee55b29f5`; PCB `6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c`. Parent8fe809 frozen. All197 files and declared432-file parent/3-file audit dependencies verified intact at completion. This review does not claim an initial integrity snapshot; source files remained read-only throughout.

## Exact source and fresh tools

Independent S-expression parser verifies only placed R503 Value100k1%→47k1% and new hidden MPN RC0603FR-0747KL in PCB and pickup schematic. Remove precisely those properties and full parsed trees equal. Other51 native files byte-identical; no copper/pad/position/zone/source net edits and no other100k changed. Embedded generic default symbol unchanged. Reproduced full netlist102 parts/90 nets, exact net-pin-function/libparts and all other component fields; generated BOM only R503 Value/MPN differs. Previous unspecified MPNs stay unspecified.

Fresh bound KiCad9.0.2 full all-track/parity/severity CLI: base/candidate **0 violations /134 unconnected /0 parity**, exit5. ERC **0 errors /1 unchanged VBUS_5V dangling-label warning**. No design completion implied. Full replay returns identical native files; real PCB-only100k versus47k schematic counterfactual yields **0/134/1**, exit5 and R503 parity detection. Normal/-O independent and reproduced verification equal; old/wrong/missing-value/MPN contract negatives reject.

**Fresh raw airwire endpoints differ in4 entries**, not author's original8. Both executions preserve per-net unconnected counts and unchanged physical source copper. Author8-entry evidence remains untouched; review's fresh_raw_airwire_difference.json preserves this run. Initial attempt to reuse author's raw snapshot failed and is retained as REJECTED_reused_raw_representatives.log. Only review copy verify.py was adapted to fresh snapshot, not to suppress counts or geometry. Raw airwire JSON is not stable equality evidence.

## Primary-source and arithmetic checks (2026-10-30)

[YAGEO exact part](https://www.yageogroup.com/component-documentation/download/specsheet/RC0603FR-0747KL):47kΩ±1%,0603,0.1W at70°C,75V maximum continuous,±100ppm/°C; nominal body1.6×.8×.45mm with±.1mm dimensional tolerances. Package classification is not assembly/MPN height qualification.

[ALPS SPVE110100](https://tech.alpsalpine.com/e/products/detail/SPVE110100/):minimum resistive rating50µA/3V; operating life50,000 cycles. This rating is not a consumer pen lifetime guarantee. Contact resistance specification permits1Ω after life. Prior100k+1k nominal at3.3V gives32.6733µA and even3.6V/−1% only36.0036µA, below minimum current. New47k+1k with±1%,contact0–1Ω,rail3.0–3.6V gives61.8799–75.7576µA. Model omits leakage/temp drift/noise/real rail behavior. Supply below3V is not accepted merely because arithmetic current stays above50µA. Calculated sub0.3mW dissipation is not whole-temperature qualification.

## Pin identity and firmware

Actual netlist NIB_CONTACT_N contains U101 physical pad7, pinfunction GPIO2; R503.2,R504.1,C504.1. [Espressif SiP v1.2 table2-1](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf) identifies pad7 as GPIO2/RTC_GPIO2, while GPIO7 is pad12. Firmware must not use package number7 as GPIO index. [Sleep-mode docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/sleep_modes.html) require configured wake sources/power states; pin capability is not implementation. Inspected application worktree board_provider_absent.c returns0, so no pressure acquisition/wake implementation is established. Read-only observed path/hash/source captured in firmware_provider_observation.json; hardware worktree itself does not contain that firmware provider.

## Status / limitations

Accept correction only as active R503 selection erratum accompanying frozen100k descriptions. Do not silently rewrite old evidence or claim pressure routing now exists. Geometry remains unchanged, R503 is still not physically fully connected;134 unconnected items, connectorB52 versus virtualB70.5 mapping, contact actuation/life/debounce/ESD/leakage/RTC firmware remain open. Microsecond RC is not debounce. JP301 remains OPEN; inherited courtyard/short-escape/EP-hole, externalSENS, unknown camera, battery/charging and assembly gates remain. No consumer test, power, procurement, fabrication, upload or manufacturing qualification.

## Reproduction / publication

Only review_manifest allowlist is review delivery. Native/replay/negative duplicated project trees excluded. Reconstruct native/ and materialize.py,run_checks.py,replay_and_negative.py from immutable author at hardware/<review> beside parent. Keep review independent.py and adapted verify.py and fresh raw difference. Run /usr/bin/python3 run_checks.py; independent.py normal/-O (generates fresh raw difference); verify.py normal/-O; replay_and_negative.py. Bind original project/rules/source. Official source links are references, not bundled full copyrighted texts.
