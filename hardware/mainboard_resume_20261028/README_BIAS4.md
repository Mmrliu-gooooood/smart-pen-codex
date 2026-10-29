# BIAS4: D7 bias branch completed, 0402 placement candidate — NOFAB

This is a successor study to frozen XCLK5, not a manufacturing release. The original XCLK5 directory and its hashes are unchanged. Native ERC is 0; actual DRC remains **4 unconnected items, 34 dangling-via warnings, 2 dangling-track warnings, and 16 missing-footprint parity issues**. Other native geometry checks report 0 in this snapshot. A low unconnected count does not qualify the whole pen.

## Actual change

R217 remains **100 kΩ, 1%, same D7-to-GND net and same source symbol/path**. Its sole schematic property change is the footprint from `Resistor_SMD:R_0603_1608Metric` to `Resistor_SMD:R_0402_1005Metric`. It moves to F.Cu, with pad 1 at (1.10, 21.30) mm and pad 2 at (1.10, 22.32) mm, between the existing R101 and R213 rows. A 0603 body in this corridor caused two courtyard collisions and was rejected. This change adds no new B-side component.

The previously isolated D7 bias stub and its via are removed, with exact UUIDs in the delta report. Every other original track/via is retained with the same geometry, width, layer, drill and net. The new D7 branch is **0.760355 mm F.Cu + 0.075 mm B.Cu**, and one **0.6 mm / 0.3 mm standard through via** at (1.85,21.275) mm. This is not a new fine-via exception. A **1.804264 mm / 0.15 mm F.Cu GND connection** reaches the existing GND via at (0.8,24) mm. There is no new GND via. Two old ground stubs remain as explicit dangling warnings rather than being silently removed.

Actual copper connectivity joins **U101.19, U201.10 and R217.1**. Fresh separate filled-zone checks retain all **27 AON, 75 GND and 11 VIO pad endpoints**. The native source retains all **374 pin endpoints**, 90 schematic entities, 74 PCB footprints and 269 pad shapes. The remaining disconnected signal nets are HREF (two missing joins), TRIG-semantic `CAM_PWDN_UART_RX` (one), and RF_SIP (one). Sixteen omitted board footprints still require proper integration; they have not been marked off-board to improve parity.

## Component and assembly boundary

A real same-value candidate is [YAGEO RC0402FR-07100KL official specification](https://www.yageogroup.com/component-documentation/download/specsheet/RC0402FR-07100KL), checked 2026-10-28. It identifies 100 kΩ ±1%, 0402/1005, 0.063 W at 70°C, body 1.00±0.05 × 0.50±0.05 × 0.35±0.05 mm and ±100 ppm/°C. At the conditional rail upper screen 3.45 V and 99 kΩ, static dissipation is 0.12023 mW, not a concern relative to that nominal rating. This calculation does not qualify ESD, transients, actual environment or the pen as a product.

The installed KiCad nominal 0402 land pattern is used, **not claimed to be an exact vendor-recommended land pattern**. Purchased-part availability, placement/tombstoning/stencil process, clearance tolerances, accepted panel and quote remain open. The candidate MPN is recorded for procurement review; no purchase was made and CNY380 is not established. Existing source labels such as USB4105-GF-A16P belong to the older unresolved whole-mainboard source and are not a new recommendation; the separate USB tail review has the corrected USB4105-GF-A identity.

## Fail-closed checks and failed experiments

The actual new route generator records expected nets from the requested literal net before save, then checks every new UUID after native save/refill/reload. It uses explicit exceptions, not assertion-only rejection. The generator also succeeds under `python -O` for an independent output and its literal contract validates. The guard proof runs good/bad/empty/missing/duplicate contracts in both normal and optimized Python: good cases reach a fresh DRC invocation, all 8 bad cases exit nonzero before the marker or DRC. A good control-flow case is not a zero-DRC claim.

The source/copper delta checker also uses explicit exceptions and passes normal and optimized Python. The inherited separate power/signal connectivity scripts were executed in normal Python; their results are not a claim that every historical checker is optimization-proof. Failed large-footprint, unreachable and collision trials are outside the authoritative frozen whitelist.

Remaining qualifications include physical current and return-path behavior, input AON narrow neck, clock/data timing, analog and EMI, USB/RF, exact camera module mapping, complete battery/NTC safety, commissioning and assembly. All commissioning bridges remain open. No camera/battery was powered, no hardware was flashed, and no Gerbers were released.
