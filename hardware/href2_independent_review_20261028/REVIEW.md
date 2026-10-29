# HREF2 independent review — partial mainboard, NOFAB

2026-10-28 UTC. This is a fresh review of HREF2, **not an inherited HREF3 approval**. It independently confirms the HREF main connection and the explicit layout delta within the scope below. The board is not ready for fabrication or an integrated pen.

## Inputs and native results

- HREF3 PCB SHA256: `f00d85c7eea8e8abdbf89eb83720fa7aeca564e939f0b6b5f89d548881cb7815`.
- HREF2 PCB SHA256: `228b04b42c45ebb37ca96a27d84a4f7a48f3e2b805c63dff0c2c6a5be2e6fb69`.
- Fresh KiCad netlist export exits 0. All-severity ERC with `--exit-code-violations` exits 0.
- Fresh DRC includes `--exit-code-violations --all-track-errors --schematic-parity --severity-all` and **exits 5**: **2 unconnected items, 33 dangling vias, 3 dangling tracks and 16 missing-footprint parity issues**. All other native geometry categories are zero. It is incorrect to call the whole DRC passed.
- Remaining disconnected electrical nets are CAM_PWDN_UART_RX (TRIG-semantic) and RF_SIP. HREF is now physically complete among all three present pad endpoints, including the bias resistor.

## Independently checked source and geometry provenance

Fresh XML semantics match HREF3: all 90 entities, 374 pin endpoints, values, footprint identities and source properties are unchanged. All 74 physical footprints retain exact pad geometry, net assignment, attributes and source paths. R220 remains in the previously reviewed B-side location; this successor introduces no further component placement change.

The new board **does not preserve all old copper**. Against HREF3, 3247 track/via objects are retained identically, 81 removed and 199 added; no surviving UUID changes its geometry. Removed counts by net: GND 31, CHIP_EN 4, CAM_VSYNC 23, CAM_D7 21, 3V3_AON 2. Added counts: GND 27, CHIP_EN 2, CAM_VSYNC 13, CAM_D7 9, 3V3_AON 3, CAM_HREF 145. These are object counts, not component counts or total net lengths.

The independent audit reconstructs the exact permitted geometry multiset from:
1. HREF3 geometry;
2. the SHA-locked XCLK5 → `href_left_source` research delta described in `transplant_contract.json`;
3. removal of exactly the five identified HREF3 R220-ground objects;
4. the two subsequent literal UUID/net route contracts for HREF completion and new R220 ground.

The resulting multiset exactly equals the final native PCB. This checks actual class/net/layer/endpoints/width/drill tuples, not just the author's success log or reused net names. No undeclared extra copper deletion/change is present. The independent `audit.py` passes in both normal and optimized Python using explicit exceptions.

## Actual electrical connectivity

The independent graph combines native local pad/track/via contact with separate nodes for each actual filled polygon island. Via contact uses annulus samples rather than assuming a drill centre is copper. Same-net disconnected islands are not automatically joined. Every previously connected multi-pad net remains connected. All 27 AON, 75 GND and 11 VIO pad endpoints remain connected. HREF has one component; only TRIG and RF retain two each.

This graph establishes connectivity, not impedance, current capacity or transient stability. The relocated AON feed is visibly different: its prior 0.825 mm / 0.15 mm F.Cu segment and via at (1.0,33.6) mm are replaced by two 0.15 mm segments totalling 1.473528 mm and via at (1.6,34.0) mm. That explicit change and the GND rerouting require their own power/return review; neither the HREF3 result nor preserved endpoint count certifies power integrity. Detailed changed-net segment geometry is in `return_screen.json` for cross-review.

## In2 HREF and return-path boundary

The actual In2 HREF segment totals **5.472792 mm**. A geometric screen samples the centreline and ±150 µm transverse offsets at ≤25 µm intervals against actual filled In1 GND polygons, with repeated segment endpoints counted. Of 224 samples, 40 centre samples lack projected GND and 70 have at least one of the three offsets outside GND.

**All 40 centre misses lie within 0.450694 mm of one of HREF's endpoint vias.** Inspection of the rendered actual polygons confirms these are chiefly the signal vias' own antipads, not evidence that the middle span crosses a long split plane. Side-offset samples also approach adjacent SENS_D0/D4 antipad boundaries. These counts are geometric diagnostics, not a failure rate or quantitative return-current simulation.

The two new HREF transition vias at (1.3,37.85) and (2.2,42.95) mm are respectively about **1.409 mm and 1.531 mm** from the nearest GND via. Their real transition inductance/return path, stackup, edge rate and waveform margin have not been qualified. The 5.47 mm internal route is not by itself a 24/36/72 MHz timing or SI approval. `In2_HREF_vs_In1_GND.png` is a top-down layer projection for inspection, not assembly artwork.

## Fail-closed guards

The actual current validator from the routing provenance was independently called with good, wrong-net, empty-map, missing-UUID and duplicate-UUID contracts in both normal and `-O` modes. All eight bad cases return nonzero before the subsequent DRC/marker. Both good cases reach a real DRC, which exits 5 as expected for the unfinished board. This independently confirms those guards, not all historical script behavior or overall manufacturability.

## Remaining gates and reproducibility

Open gates include the 16 footprint/physical-port integrations, RF and TRIG, routing cleanup of fine staircase segments and dangling remnants, current/return behavior, timing/EMI, exact camera mapping, approved cell/NTC/charging qualification, real parts and assembly process, full enclosure clearance, handwriting accuracy, endurance and cost. Existing B-side R220 mask/tenting/body-clearance concerns remain unchanged. No power, camera or battery connection is authorized by this report.

Reproduction depends on pinned HREF3, XCLK5 and `href_left_source` PCB artifacts plus the explicit transplant/removal/route contracts. Publication must retain those versions or record their recoverable source hashes. The full moving experiment directory should not be represented as a finished release. No source/PCB was modified by this review and no GitHub write, purchase, powering, flashing, eFuse change or manufacturing release occurred.

## Final freeze verification

The finalized candidate manifest SHA256 `021ea579e06a9c78930b7b16bd5ca4ace1d638a268670fd10fc0028c7a0c1ea4` contains 102 files. Every listed file matched its SHA256, including the unchanged reviewed PCB. The final README explicitly describes the power-route degradation, unchanged old narrow neck and endpoint-antipad interpretation; it does not claim a final preferred or manufacturing-qualified board. This is a content/hash closure, not a replacement for the separate quantitative power review.
