# Ground recovery cut-negative protocol

Only reads positive `native/`; each test copies the full source/project/libraries into `native_negative/<target_pad>/`, removes exactly the target's new segment/via UUIDs from materialization.mapping, freshly fills zones, saves and reloads the actual PCB. No positive PCB/source edits. NOFAB/NOPOWER.

Expected lost-pad sets are declared before execution in `negative_ground_declaration.json`, against selected20_final.json hash:
- R224.2 cut: R224.2 + R228.2.
- R226.2 cut: R226.2 + R206.2.
- J104.3 cut: J104.3 + R223.2.
- R220.2 cut: R220.2 + R225.2 (updated final local topology: R225 dogleg uses R220 branch rather than its own via).
- All other 16 groups: only their own target pad.

Actual lost/gained core-GND sets must match exactly, not merely contain an intended target. All non-GND finite physical component graphs must equal positive graphs. Explicit checks also cover NIB_CONTACT_N, STRAP_GPIO3, AON I2C SCL/SDA, pickup interrupt and U203.13→J202.18 clock connectivity.

Real KiCad DRC uses `--all-track-errors --schematic-parity --severity-all --exit-code-violations`. Expected unconnected count derives from actual GND component-count increase over positive76unconnected, rather than assuming every lost pad is a separate island. Only cut-induced track_dangling/via_dangling violations are permitted; complete descriptions remain in each result. Parity must remain0. Physical lost-set checks prevent extra legitimate-looking connectivity changes from being ignored.

Run normal and `-O` versions separately after parent announces native_ready. Outputs must match exactly; all child stderr and DRC reports/logs retained. `negative_ground.py --declare` creates declaration only and does not load/write a PCB. Do not treat this protocol alone as a test result; terminal execution evidence is `negative_ground.json`, `negative_ground_optimized.json` and their comparison report.

## Executed result, 2026-10-30 08:29 UTC

Both real20-case runs passed and JSON outputs are byte-identical (SHA256 `b068e10238f371f36f0ab9c4be6b0003ebf2dda401e0e432db465b4e6e2b360a`). The terminal comparison script also passes normally and under `-O`.

-16 single-pad cuts: DRC0 /77unconnected /0parity; core90.
- R224.2 cut: R224.2 and R228.2 leave core together but remain one floating connected island; DRC0/77/0; core89. Not incorrectly counted as two new missing edges.
- J104.3 cut: losesJ104.3/R223.2; R223 branch terminal is left dangling. DRC1/78/0; core89.
- R220.2 cut: losesR220.2/R225.2; R225 dogleg terminal is left dangling. DRC1/78/0; core89.
- R226.2 cut: losesR226.2/R206.2; R206 branch terminal is left dangling. DRC1/78/0; core89.

The three warnings are not merely accepted by generic violation type: `negative_ground_compare.py` checks their exact UUIDs against the predicted partner terminal coordinates in materialization.mapping. Any other dangling item or warning fails the terminal check. All non-GND component graphs match the positive board; explicit pressure/strap/IMU/I2C/clock checks pass in every run.

Positive PCB remained `abd8a388a606582e80ebe5f59da7579f7020cd44be6af494e032b8f69fde8ca0`. Each negative PCB is intentionally disconnected and **must never be sent for fabrication**. This is connectivity-verification evidence, not power, thermal, timing, assembly or product validation.
