# Gate input supply block — NOFAB, not complete gate circuitry

Successor of frozen `imu_compact_0402_placement` (dd55…), without moving any footprint or changing any component, layer, RF path or MEMS restriction. Board SHA `ae805cea5d51e864588bdf052b64e1bacce118a122b9f98ce21ddaa15345a691`.

## Closed scope and evidence
- U301.1 VIN and C301.1 now join the original 3V3_AON core: **3 components → 1**. U301.2/C301.2 join original ground; whole-board GND **17 → 15 components**, so ground is not entirely complete.
- Fresh full KiCad 9.0.2 DRC with `--all-track-errors --severity-all --schematic-parity --exit-code-violations`: **135 violations / 54 unconnected / parity 0**, exit 5. Baseline 135/58/0. Exact type + item-UUID violation comparison: **zero added, zero removed**. Old 135 violations still prohibit fabrication/power-on.
- Fresh native source: 102 components / 356 pin endpoints. ERC: zero errors, one inherited VBUS_5V singleton-label warning, exit 5.
- All old actual pad-component relationships preserved, using finite polygon copper, via annuli with holes and filled-zone islands over all six layers. AON/ground acceptance sets explicitly include U301 and C301, not only airwire counts. Actual MEMS plane/via intrusion remains zero. JP301 stays source/physical OPEN with distinct separated pad nets.
- **3 old tracks removed and exactly replaced by 17 new tracks + 3 vias**. All surviving old track/via geometry and every footprint/pad geometry/net remain unchanged. The input/IMU and RF copper were not narrowed or moved.
- `audit_gate.py` / `measure_and_bind.py` pass normal and optimized Python with identical results. Seven deliberately corrupted fixtures are rejected in both modes. Fixtures are excluded from manifest.

## Explicit local power geometry
B-side C301 remains (10,64); U301 remains (9.5,67), both 180°. New AON pad escapes are **.50 mm wide** and use **.60/.30 mm** through vias at (11.3,64.8) and (11.3,66.05), connected through actual AON fill. C301 copper escape is .582843 mm; U301 VIN escape .223607 mm. Via centres are 1.25 mm apart. These are not a single direct pin-to-pin top-layer trace.

C301 ground uses .30 mm trace, .807107 mm from the overlapping pad escape to existing core ground via (10,63.4). U301 ground uses .40 mm, .20 mm escape to new .60/.30 via (11.3,67). Ground-via centres are **3.827532 mm** apart; the existing cap ground via is shared with existing circuitry. A planar separation is **not** plane-current path length, total loop length or inductance. Pad current spreading, barrels and plane return are not included in these trace figures. This closes DC connectivity, **not transient/HF/PI qualification**. No arbitrary current rating is inferred from width alone.

## Three bounded low-speed reroutes
|Net|Layer|Removed route length mm|New route length mm|
|---|---|---:|---:|
|CAM_IO_EN|F.Cu|6.700000|7.611270|
|CAM_ISO_OE_N|F.Cu|3.000000|3.041421|
|USB_EN1|B.Cu|36.250000|36.457107|

These are isolation-enable/mode-control nets, **not DVP, XCLK, PCLK or USB data**. Their source pull/default networks and all old connected pad sets remain unchanged; firmware startup and physical switching behavior are still not tested. Exact UUID/net/layer/geometry additions are in `new_routes.json`; `route_input.py` declares the three removals and rebuilds only from dd55. Early rightward U301/C301 movement and colliding trial paths were rejected; the delivered native board has **no placement changes**.

## Native source/BOM and rules
The complete selected schematic tree is copied from `gate_supply_native_mpn_source`, manifest `d9ee61999f3520b4ddd34ccc2bf32919809f872f04905611f2bfae4abba374b8`. Ten exact candidate Manufacturer/MPN/ProcurementStatus native fields are freshly exported and verified. All candidate statuses remain unqualified; C302's inherited 10 V part is NRND and has not silently become a 16 V alternate. See source contract for C303 rating-upgrade boundary. No MPN is invented for wirelands/commissioning copper.

Explicit conditional six-layer .83 mm stack retained; mechanical bound .93 mm. Project/custom rules/netclass hashes unchanged. `pcb_preflight.py` locks same-basename project, custom rules, CLI and full native DRC options. Default material Dk/loss fields remain unqualified, never an impedance guarantee. Manufacturing-mode preflight rejects the unqualified process/quotation/material gates.

## Safety and remaining work
TI TPS22918 Rev C §11.1 requires short/wide supply paths and nearby low-ESR ceramic input bypass; §9.2.2 warns output capacitance/input droop and body-diode reverse current. Existing nominal CIN 10 µF / local COUT 1 µF is not proof of 10:1 against an unknown camera's total bulk and DC-bias values. TPS22918 is **not an overcurrent limiter/protection guarantee**.

**EN, CT, QOD and controlled-output connections are not completed by this block. JP301 stays OPEN.** Unknown camera power/connector/voltage, IO backfeed, startup, capacitor effective values, current/ripple/thermal tests and full-board geometry remain gates. No unknown camera may be energized. No procurement or fabrication release follows from this study.

Official source locally retained at `hardware/power_safety/sources/tps22918.pdf`, originally https://www.ti.com/lit/ds/symlink/tps22918.pdf . Final combined mechanics should bind the actual board hash; since all footprints and dimensions are unchanged, this block adds no new body-height envelope but does not independently certify the whole pen.
