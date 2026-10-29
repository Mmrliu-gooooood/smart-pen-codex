# HREF2 power / return delta review against HREF3

2026-10-28 18:56 UTC. **NOFAB. HREF2 is a connectivity research candidate, not a power-integrity improvement or manufacturing selection.** No source board was modified. The reduction to two unconnected items is not sufficient to accept the altered power/return geometry.

## Exact inputs

- HREF3: `hardware/mainboard_href3_candidate/mainboard_revD.kicad_pcb`, SHA256 `f00d85c7eea8e8abdbf89eb83720fa7aeca564e939f0b6b5f89d548881cb7815`.
- HREF2: `hardware/mainboard_href2_candidate/mainboard_revD.kicad_pcb`, SHA256 `228b04b42c45ebb37ca96a27d84a4f7a48f3e2b805c63dff0c2c6a5be2e6fb69`.
- Both hashes remained unchanged after analysis. This scope supplements, not replaces, the separate whole-board native-net/physical-connectivity review.

## C201 supply connection: confirmed worse length, not an automatic failure

C201 value remains **100n X7R**, with the same footprint, pad dimensions, positions and nets: pad1 AON at (1,32.775) mm, pad2 GND at (1,31.225) mm. Native pad adjacency confirms that pad1 enters the recorded first F.Cu segment.

- Old AON feed: one **0.825 mm × 0.15 mm** F.Cu track, terminating at a **0.6/0.3 mm** via at (1,33.6).
- New feed: **0.625 + 0.848528 = 1.473528 mm**, both still **0.15 mm**, terminating at a **0.6/0.3 mm** via at (1.6,34).
- Added length: **0.648528 mm**, approximately **78.6%**. There is no claim that this is a wider or lower-inductance connection.

Using copper rho20=1.724×10⁻⁸ Ωm, alpha=0.00393/K, uniform 85°C and **17 µm effective copper**, the rectangular-conductor screen gives:

| Item | Old | New | Increase |
|---|---:|---:|---:|
| Track resistance | 7.002 mΩ | 12.507 mΩ | 5.505 mΩ |
| Drop if 500 mA were assumed through this track | 3.501 mV | 6.254 mV | 2.752 mV |

**500 mA is a sensitivity assumption, not a measured C201 branch current or approved rail load.** The branch is part of the decoupling connection; capacitor charging/discharging current, local switching loop, effective capacitance, ESR/ESL, via inductance, load-current partition and supply transients remain unquantified. Do not dismiss the added impedance by assuming “only DC capacitor current,” and do not falsely assign the full MCU current to it. These DC numbers cannot prove either safe operation or unsafe operation.

The distance from this AON via to the nearest actual through GND via increases **2.3521 mm → 2.6235 mm** (old nearest (0.9,35.95); new nearest (1.95,36.6)). This nearest-via metric is only a geometric warning, not the loop inductance: actual capacitor ground-pad path, plane current and other conductors must be included in a proper loop assessment.

## Existing AON neck: retained, not solved

Independent 25 µm rasterization of **actual filled In2 AON polygons**, including explicit hole handling, compares the whole-width y=51.7..56.8 mm strip around the prior SCL/SDA restriction. HREF3 and HREF2 have **zero changed pixels** there. This is resolution-limited equality, not a claim of exact manufacturing neck width.

A four-connected erosion screen from the input-via neighborhoods (6.1/6.9,82.4) to the upper bridge neighborhood (9.35,22.95) yields the same useful threshold in both boards:

- Connected at erosion radius 0.100 mm.
- Disconnected at 0.125 mm.

The method uses 0.45 mm endpoint neighborhoods without adding copper. It is a path-width sensitivity screen, not a current solver. It does **not** establish the exact neck as twice the erosion threshold or the maximum safe current. The previously reported approximate **0.2 mm × 5.15 mm** restriction therefore remains a PI qualification item. Its rectangular 17 µm / 85°C / assumed 500 mA screen remains approximately **16.39 mV**, before via, spreading, tolerance, partition and transient effects. No new “fixed power neck” claim is justified.

## New HREF bridge region and ground changes

Across y=37.8..43 mm, including the new In2 signal bridge and changed nearby ground vias:

- In2 AON loses **9,576 pixels = 5.985 mm²**, gains 12 pixels = 0.0075 mm².
- In1 GND loses **1,172 pixels = 0.7325 mm²**, gains 3 pixels = 0.001875 mm².
- In the C201 region x=0..3.5, y=30.5..35.5, both AON and GND cutouts also change.

These are nominal raster copper-area differences, **not** a direct resistance/temperature verdict. The full input-to-upper-bridge erosion threshold is not worsened at this resolution, but that alone does not show that all local branches, current crowding or AC loops are equivalent.

Native polygon `Contains` sampling of new non-ground track centerlines against actual In1 GND finds uncovered samples; new HREF copper has 139/2,010 samples without In1 ground projection (many short segment endpoints repeat). To avoid interpreting that duplicate-heavy count as a coverage percentage, a second independent length-weighted midpoint screen was run on entire nets:

| Net | HREF3 total track length / uncovered In1 projection | HREF2 total track length / uncovered In1 projection |
|---|---|---|
| CAM_D7 | 30.485 / 3.120 mm | 30.961 / 3.120 mm |
| CAM_VSYNC | 62.337 / 6.338 mm | 63.021 / 6.303 mm |
| CAM_HREF | 4.821 / 1.341 mm | 50.493 / 4.071 mm |
| CHIP_EN | 14.672 / 3.143 mm | 13.818 / 0.893 mm |

HREF3's HREF was disconnected, so its short length is **not an equivalent complete-route benchmark**. Some projected gaps arise at antipads, but this review does not waive them or turn a ground projection screen into SI approval. For B.Cu, the adjacent reference is In2 AON rather than In1 GND; coupling and return transfer through actual decoupling/stitching are not solved by looking through that plane. For the new In2 HREF segment, nearby In1 ground projection is useful but still not a proof of loop impedance or reference continuity at layer changes.

## Disposition and required next step

Retain HREF2 as **NOFAB candidate requiring PI/return optimization**, not the preferred finished layout merely because HREF is connected. The unchanged prior bottleneck and longer C201 decoupling feed are explicit open items. Before promoting it:

1. Examine a local C201/feed/via arrangement that restores a short decoupling loop without cutting the AON plane or breaking already-connected nets. Preserve actual measured/source component values; re-run native and island-aware connectivity after changes.
2. Check actual filled AON current corridor and reference transfer around all relocated GND/power vias and In2 HREF transitions. Use a real stackup and load/transient assumptions; document measured/current-budget evidence rather than assigning 500 mA to every branch.
3. Close the already-known AON neck, supply droop/PDN and DVP timing gates separately from DRC and the remaining TRIG/RF connections.

No procurement, energization, flashing, manufacturing export or GitHub write occurred.

Evidence: `power_return_analysis.json`, `copper_delta.json`, `check_power_return.py` and its log, plus HREF3/HREF2 AON raster images. 25 µm raster and 25 µm midpoint sampling are disclosed screening resolutions; neither replaces electromagnetic or thermal validation.
