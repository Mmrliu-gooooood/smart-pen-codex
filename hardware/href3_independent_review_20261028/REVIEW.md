# HREF3 independent review — partial PCB, NOFAB

2026-10-28 UTC. Independent read-only review of the BIAS4 → HREF3 transition. No new source, assigned-net, retained-copper, connectivity or native geometry defect was found within this scope. **This is not a manufacture-ready board.**

## Exact reviewed input

- BIAS4 PCB SHA256: `0796d092b4775e314f9b5f43b62b0a7ba153c9b4e8804fb02c6f0ea8cdeae5cc`.
- HREF3 PCB SHA256: `f00d85c7eea8e8abdbf89eb83720fa7aeca564e939f0b6b5f89d548881cb7815`.
- HREF3 frozen manifest SHA256: `a4e798b5c112cec20d4d6376d4f4c79b67db9a8685b9a561bc01eb633648a327`; all 94 listed file hashes match.
- Fresh KiCad netlist/ ERC/DRC outputs and actual exit codes are stored here. Previously existing source files remained unchanged during this review; subsequent additions by the author were separately verified against the final frozen manifest.

## Fresh checks and real defects remaining

Native netlist export exits 0 and all-severity ERC exits 0. DRC includes `--exit-code-violations --all-track-errors --schematic-parity --severity-all` and **exits 5**: 3 unconnected items, 34 dangling vias, 3 dangling tracks, 16 missing-footprint parity issues. All other native geometry categories are zero. A DRC report exists precisely because the board has not passed the release gate.

The missing joins are MCU-to-translator HREF, CAM_PWDN_UART_RX/TRIG-semantic and RF_SIP. The 16 missing footprints remain represented in source, not erased or marked off-board to obtain a cleaner count.

## Independently reproduced source and physical delta

`audit.py` compares independently exported source and the native board objects, and passes in normal and optimized Python. Source retains the same 90 entities and all 374 pin endpoints, component values, footprint identities and properties. All 74 physical footprint references remain. R220 alone moves from F.Cu to B.Cu, retaining its same 100 kΩ / 0603 identity and source path: pad 1 (1.200,45.000) mm, pad 2 (2.850,45.000) mm. All other 73 footprints retain exact pad geometry, layers and nets.

All **3287 BIAS4 track/via items** are retained with identical native geometry, net, widths and drills. There are 41 added items: 36 HREF and 5 GND. Independently summed new HREF length is 3.2220562748 mm and new GND length 2.0331475452 mm. The two new vias are standard 0.6 mm copper / 0.3 mm drill at (1.950,46.525) mm HREF and (1.925,43.350) mm GND. Refilling necessarily changes plane contours; old-track preservation is not a claim that all copper is unchanged.

The physical graph combines native local pad/track/via contacts with separate nodes for each actual filled polygon island. Via contacts use annulus samples, not the drill centre. It does not simply union every item with the same net name. All previously connected multi-pad nets remain connected. The 27 AON, 75 GND and 11 VIO endpoints remain complete. U202.6 and R220.1 share the same HREF component, while U101.23 remains separate. HREF has two components, TRIG two, RF two; there are no other disconnected multi-pad nets in this graph.

## Fail-closed guard review

The actual candidate validator was invoked independently with ten cases: good, wrong literal net, empty mapping, missing UUID and duplicate UUID under normal Python and `-O`. All eight bad cases exited nonzero before the subsequent DRC invocation or marker. Both good cases passed the validator and reached real DRC, which returned **5**, not 0. This proves those guards' behavior, not global optimization-safety of every historical script or a full-board pass.

## Physical and process boundaries

The actual B.Cu rendering was inspected. R220's native B.CrtYd bounds are x=0.520–3.530 mm, y=44.245–45.755 mm; the only other B-side component courtyards belong to R105 and R214, outside this local region. There is no native courtyard overlap, but traces and via features beneath/near R220 require real solder-mask/tenting, body stand-off and assembly review. The image is a top-down board-coordinate projection, **not a mirrored assembly instruction**.

R220 adds a B-side component at y=45 mm. The author's 1.0 mm body + 0.15 mm solder envelope is conditional, not a measured or purchased-part tolerance. Prior enclosure studies cannot automatically certify its clearance. Grid-generated short staircase segments remain and need routing cleanup; no production-layout quality is established by these connectivity checks. Power/return impedance, timing, EMI, thermal, all external ports, RF, exact camera mapping, qualified cells/NTCs, commissioning, assembly yield, accuracy and cost remain open.

## Reproduction dependency

The frozen candidate's `check_delta_graph.py` references sibling `mainboard_resume_20261028/mainboard_revD.kicad_pcb` and its XML, and reproduction scripts reference the original candidate and fine-process contract. Publication must preserve/version these baseline dependencies or document their exact recovery inputs. This directory's audit likewise deliberately references those pinned source artifacts. It is evidence, not a standalone general installation package.

No PCB/source was modified by this review. No purchase, GitHub write, powering, flashing, eFuse, commissioning bridge closure or manufacturing release occurred.
