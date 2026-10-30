# Independent IMU/J107/EXTCLK native review

**NOFAB / NOPOWER.120 connections remain. Formal accepted9a03 is unchanged. No consumer, manufacturing, dynamic clock or MEMS qualification.**

Author380-file manifest `ca5ec099df919088b81b3a3d0c2d7f9da981e07728cb4626162355aa5da83ab4`; candidate PCB `d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22`; parent6902c742 pressure47k source. Proposal manifest `53fdac310f1b3ed4b8279e8ba04f402d99f13e60aabcd661fdf24897ba2e18e8`. Source/proposal files and all declared dependencies checked intact at completion; no initial hash snapshot claimed. Frozen source files not edited or uploaded.

## Native result and independent geometry

Fresh KiCad9.0.2 full all-track/severity/schematic-parity: **0/120/0**, exit5; ERC **0 errors/1 inherited VBUS_5V warning**. Independent physical UUID graph with via drill removal and guarded one-shot native zone normalization/all-drill subtraction gives **AON35/39, GND68/102, SENS12/12**. All14 IMU AON/GND pads in correct cores. Independent all-components script preserves every old physical-pad UUID connected component, including separate same-number MCU EP pads. Reproduced19 complete nets and12 DVP chains.

789parent−1old EXTCLK+33new objects=821. All788 retained old copper geometries unchanged. Only J107 B(3.2,84,180°)→(5.2,84,180°); remaining101FP unchanged. Four new vias checked ring and drill against all physical pad layers including same-net: no overlap. Actual relocated J107 versus retained foreign copper and native MEMS rule areas tested by reproduced finite geometry. U501 ground-via courtyard overlap0.0292143mm² remains; no native body/no-via-rule intrusion does not grant TN0018 assembly/stress waiver.

Power0.25mm; AON beam y80.25; AON/GND standard.60/.30vias at(2.65,79.9)/(2.65,83.3). Removed only old EXTCLK UUID2010858e-8edf-52c4-a3a5-f423a79bbfc8. Restored via B/In3/B at x4.25 with upper79.7/lower89.4 and.45/.20signal vias,.15clock tracks. U203.13↔J202.18 connected; R235.1 stays isolated. Projected11.9mm not increased, but electrical via transitions/stubs changed and timing/crosstalk/return-current behavior unqualified. JP201 final nominal courtyard gap.18mm/J107.43mm and clock-via AON copper.20mm are geometry only.

## Source contract / pin functions

Independent parser strips only declared copper/fill, normalizes only declared J107 pose and R503 MPN property ordering, and confirms all other native noncopper source unchanged. Other native files byte-equal; freshly generated netlist components/nets/libparts exact. R503 remains47k1%,RC0603FR-0747KL,original nets/pose; no pressure-fix rollback. JP301 OPEN remains.

Actual embedded U501 source: CS2/SA0_3/VDD9/VDDIO10→AON; NC5/GND6/RES7/GND8→GND. [ST DS11811 Rev9 Table1](https://www.st.com/resource/en/datasheet/lis2dw12.pdf) rechecked: NC5 can connect GND; RES7 must connect GND. This verifies pin contract, not chip startup/I2C/IRQ/prewake function. Mechanical/MEMS soldering guidance and real material/process testing remain open.

## Reference coverage without circular acceptance

Reproduced filled-plane deltas/guarded.25mm erosion: mainIn1GND/In2AON/In4GND loss≈1.532279mm² each, one eroded component each; no added previous-signal reference projection loss. Independent exact_holes.py starts from actual finite new clock projection, subtracts plane, then **only the exact native hole contours**, without first subtracting ideal disks. Every remaining gap is0. Hole extents≈.751×.751mm, each unique around its intended new via; bound.8mm screens merged/nonlocal holes, not an enlarged electrical clearance allowance. Author ideal-circle diagnostic leaves edge slivers; those are not hidden with a relaxed area threshold. Geometry model does not establish impedance/EM/transient qualification.

## Native negatives and honest rollback

Actual isolated delete/refill/fullCLI: AON access via **0/121/0**, all7AON targets offcore; GND via **1/121/0**, all7GND offcore, expected track_dangling; clock In3 segment **2/121/0**, endpoints disconnected, expected2via_dangling. Independent graph separately reproduces causes. Normal/-O native negative results identical.

All33 removed, old segment and J107 pose restored: **0/134/0**. Raw filled rollback is **not** byte-identical to original6902 parent. It equals serialized/refilled parent exactly. Difference is existing R503 MPN field ordering/pretty-print, token content unchanged. Only explicitly restoring original R503 property-block formatting yields original6902 SHA. Separate raw/normalized/format-restored evidence retained and never substituted. Exact forward materialization replay gives candidate d6c913; repeated fill stable.

## Scope and unresolved gates

Four linked nominal CAD contexts use original1.8×2.2×2mm per-terminal J107 budgets; this review checks linkage/hash and same pose, not regenerated entire mechanical assembly. Wiring/solder/tools/strain/stress/actual heights unqualified. MCU8EP via-in-pad/23.8µm edge,short escapes,IMU courtyard,external SENS/back-power,pressure acquisition,unknown camera and battery/charging gates remain. Do not power or fabricate. Actual native plot viewed; no GUI/physical test claim. No remote write, source change or procurement.

## Reproduction / stageability

Only review_manifest allowlist is review delivery. Excluded copied native/replay/negative/normalized project trees are not silently staged. Reconstruct native/,materialization.json,verify.py,physical.py,chains.py,materialize.py,run_checks.py,native_negative.py,rollback_format_audit.py from immutable author; keep exact declared dependency paths and review native_polygon.py (copied guarded helper), independent.py,all_components.py,source_check.py,exact_holes.py. Run run_checks.py; checks normal/-O; native_negative.py normal/-O; rollback_format_audit.py; replay materialize.py with IMU_NATIVE_OUTPUT=<review>/replay/native. Actual native diagrams and authoritative evidence remain in author manifest.
