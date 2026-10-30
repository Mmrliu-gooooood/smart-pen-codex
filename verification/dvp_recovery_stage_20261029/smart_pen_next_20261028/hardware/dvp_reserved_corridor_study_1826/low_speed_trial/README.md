# Reserved DVP corridor: two-net low-speed relocation candidate

**NOFAB. This is not a complete DVP bus or an accepted whole-board baseline.**

Starting from frozen `j202_low_speed_reference_candidate` PCB SHA-256 `9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038`, reroute only USB_EN1 and the SENS_TRIG_IN connector tail. Preserve all 102 footprints, schematic/project/rules, other-net tracks/vias, and commissioning OPEN links. No hardware powered, manufactured, purchased or programmed.

Candidate PCB SHA-256: `1d844c44e62e75a01f82e743e87b084707dd50d78afa94c9513aea6b034f5d94`.

## Actual outcome

- Twelve hypothetical straight 0.15 mm tracks, x = 12.6, 12.9, 13.2, 13.5 mm on F.Cu / In3.Cu / B.Cu, from y = 32 to 89 mm, have no finite copper/pad overlap with their 0.15 mm clearance envelopes. The tracks are **not inserted in the PCB** and have no assigned DVP nets. Endpoint exchanges, clock/data fanout, bias stubs, and connector escape remain for the parent study.
- USB_EN1 new path: 21.6487067 mm, two 0.45/0.20 mm through-vias. SENS_TRIG_IN new path: 18.1154329 mm, two such vias. These are added path lengths, not full end-to-end net lengths.
- 19 old low-speed tracks removed; two old USB_EN1 tracks clipped precisely to replacement branch junctions; 120 new tracks plus four vias added. All other tracks/vias unchanged, including all power copper. New vias explicitly tented both sides, not proof of actual fabrication coverage.
- All original finite-copper pad partitions remain identical, including the two rerouted nets. Every serialized AON/GND plane polygon remains electrically joined to its core by the finite-copper graph. This does not establish load, thermal, EMC, or signal-integrity qualification.
- Full native KiCad 9.0.2 DRC, **--all-track-errors --severity-all --schematic-parity**, reports candidate **17 findings / 21 unconnected / 0 parity**. A fresh byte-identical 9a03 baseline has the same 17/21/0 and identical complete finding multiset. The original `pcb_preflight.py` and unchanged `preflight_lock.json` also check same-basename rule/project binding, exclusions, layers and geometry before the native call.
- An initial direct command incorrectly omitted `--all-track-errors` and reported 16 findings on both boards. Those incomplete reports are retained under `rejected_incomplete_drc_mode`; **they are not full DRC results and provide no evidence of version drift or a short repair**. The corrected command restores the historical HREF-to-J103.GND short finding. Earlier wording attributing the discrepancy to unspecified runtime behavior is superseded by this identified argument omission.
- Source/project/rule hashes and raw footprint blocks unchanged. Independent native finite shapes show no new copper intersection with any foreign-net copper.
- Normal and `python -O` verification pass. Four negative tests reject J301 displacement and AON track thinning in both modes. Serialized delta replay followed by fresh fill reproduces the exact candidate PCB hash.

## Reference-plane and mechanical limitations

Fresh plane comparison subtracts actual through-drill bores, not merely anti-pad polygons. In1 and In4 each lose about 1.733976 mm², In2 loses about 5.024189 mm². The only old-track new reference projection loss above the recorded numerical threshold is 3V3_AON, 0.00005037 mm². No old DVP / RF / IRQ / AON I²C projection loss is recorded above that threshold, and no new RF region intrusion is found. This bounded area screen is not PI/EMI or switching-return certification.

The first trial placed a TRIG via at (13.425, 89.825), whose 0.45 mm ring extended 0.05 mm into the nominal connector body. Native DRC did not catch this non-native assembly gate. It was **rejected**, kept under `rejected_ring_overlap`, and not selected. The corrected trial uses TRIG vias at (11.35, 89.125) and (13.425, 89.7). The latter outer ring ends at y89.925, leaving 0.075 mm nominal separation to the coarse y90 body boundary. Exact connector underside, assembly tolerance, mask and solder process remain unqualified. Nominal ring clearance is not a production drawing.

J301 and J103 remain in their actual 9a03 positions. The virtual later J103 position and earlier J301 shifted study are not applied. Pressure frontend, service/ADC functionality, thermal/battery/camera qualification, DVP timing and final enclosure are not completed by this change.

## Reproduction

`replay.py --output <new-directory>` reconstructs from the hash-locked baseline and `serialized_delta.json`; it refuses an existing output directory and requires exact final PCB hash. `verify.py` checks candidate or an explicit test PCB. `negative_tests.py` checks two safety-relevant mutations in normal and optimized execution. Use repository-relative dependencies in `dependencies.json`.

`route.py` is the original bounded search recipe, not the immutable replay method: fresh random track UUIDs mean a new search run must remain a separate candidate. `trim.py` trims old replacement tails and explicitly tents the four new vias. `grid_astar.cpp` is locally compiled source; generated executables and large search array binaries are not release artifacts.

## Toolchain evidence

`toolchain_and_complete_drc_diff.json` records executable `/usr/bin/kicad-cli`, version 9.0.2, binary SHA-256 `d5daf01b170249572de1065faa0870b6006d8463fe4f075c018bf6ba85ca34d8`, all same-basename PCB/project/rules/schematic hashes, full added/removed findings and airwire entries. The initial discrepancy was caused by omission of --all-track-errors; corrected complete-mode reports restore all 17 findings. `baseline_fresh_fill_check.json` proves fresh fill and save of baseline 9a03 reproduce its exact SHA; neither historical source nor frozen files were altered.
