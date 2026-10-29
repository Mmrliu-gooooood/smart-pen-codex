# HREF2: complete HREF continuity research — NOFAB, PI optimization still required

2026-10-28 UTC. This successor completes U101.23 ↔ U202.6 ↔ R220.1 continuity, but is **not preferred for manufacture merely because two connections remain**. Frozen HREF3 and BIAS4 are unchanged.

## Native result

Fresh ERC 0. Full native DRC with all severities, all track errors, schematic parity and `--exit-code-violations` returns **5**: **2 unconnected items, 33 dangling-via warnings, 3 dangling-track warnings and 16 missing-footprint parity issues**. Other native geometry checks report zero. All 90 schematic entities / 374 pin endpoints and all 74 footprint pad geometries remain unchanged from HREF3. No component was hidden to improve counts.

The remaining MCU control path is **U101.50 GPIO44/U0RXD → U203.6 (2A1) → U203.11 (2B1) → SENS_TRIG_IN**, with R223 bias. The historical CAM_PWDN_UART_RX name does not mean the pin is proven to be the custom camera's PWDN. The current design requires this connection; unverified camera use does not authorize deleting it. UART test use remains camera-off-only. The other unresolved RF_SIP connection needs an actual RF matching/antenna/controlled-geometry design, not a random signal trace.

## Changed topology, not all-old-copper preservation

The exact geometry multiset retains 3247 HREF3 copper items, removes/replaces 81 and adds 199. The explicit delta includes local CAM_D7, CAM_VSYNC, CHIP_EN, GND and 3V3_AON changes derived from the older frontier research, plus new HREF routing and a relocated R220 ground connection. See the transplantation and new-net contracts in `reproduction`. It is incorrect to reuse HREF3's statement that every old copper item is retained.

All 27 AON, 75 GND and 11 VIO endpoints remain connected, as do the other previously connected multi-pad nets. Connectivity does not qualify current capacity, decoupling, EMI or waveform timing.

## Power and return qualifications remain open

C201 is still 100 nF X7R at its original pad location. Its 0.15 mm feed changes from 0.825 mm to 0.625 + 0.848528 = 1.473528 mm; the 0.6/0.3 mm AON via moves from (1,33.6) to (1.6,34) mm. Under a conditional 17 µm copper / 85°C calculation, resistance changes about 7.002→12.507 mΩ; a purely assumed 500 mA would add about 2.752 mV. This is not measured branch current, a decoupling-loop model or PI approval. The nearest GND via distance also increases from about 2.352 to 2.623 mm. Further local shortening and return optimization must be considered before selection.

The old roughly 0.2 mm / 5.15 mm SCL/SDA AON neck remains: the y51.7–56.8 mm sampled fill is unchanged, and the input-to-upper-bridge raster path still survives 0.1 mm erosion but not 0.125 mm. This research does not solve that bottleneck. Plane fill changes elsewhere, including near the new In2 HREF segment.

In2 HREF routing totals about 5.472792 mm. Independent ≤25 µm sampling found 40 of 224 centre points outside actual In1 GND, all within 0.450694 mm of the endpoint HREF vias: this is principally the vias' own antipad clearance, **not evidence of a long mid-route ground split**. The ±150 µm corridor has additional nearby signal-hole boundaries. The endpoint vias are about 1.409/1.531 mm from the nearest GND vias. Actual transition return impedance and waveforms remain unqualified; sample ratios are not failure probabilities.

## Evidence and reproducibility

The independent review is at `hardware/href2_independent_review_20261028/REVIEW.md`; the separate power study is at `hardware/power_href2_review/REVIEW.md`. The candidate's `guard_proof` tests good/wrong-net/empty/missing/duplicate contracts in normal and optimized Python. Bad cases must stop before DRC; good cases reach the actual expected incomplete-board DRC exit 5. Optimized generator output is compared by full copper geometry multiset, not UUID equality.

Reproduction depends on the explicitly identified XCLK5, HREF3 and earlier frontier research board hashes, as well as the existing fine-process contract. This directory is not a standalone manufacturing package. Failed shorting/clearance experiments in the sibling trial directory are not this result and must not be merged silently.

R220 remains the HREF3 B-side 0603 placement, so its back-side body, mask/stencil/nearby via and enclosure gates persist. Grid-derived staircase fragments still need deliberate cleanup after connectivity settles. USB/RF, physical interface ownership, battery/NTC/charging, camera levels/timing/optics, whole housing fit, cost and actual writing remain open. No charging bridge was closed, no physical test or purchase occurred, and no Gerbers were released.
