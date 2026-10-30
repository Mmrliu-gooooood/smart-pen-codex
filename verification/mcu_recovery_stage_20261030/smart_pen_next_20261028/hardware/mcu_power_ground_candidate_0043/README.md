# Rejected first MCU supply / EP-ground restoration — NOFAB

This is preserved negative evidence, not the recommended research successor. It restored eight old AON groups (41 objects), widened the ten RTC/CPU-IO/VDDA local tracks to0.254mm, and restored nine old0.60/0.30mm EP ground vias on the unchanged U101 pad matrix. Native fullDRC0/180/0 does **not** make it acceptable.

The old EP via at(4.5,10) physically overlaps the back-side C504.2 solder pad: disk-overlap0.081736964mm² and drill-overlap0.012487330mm². Both are GND, so ordinary native electrical DRC does not flag the manufacturing conflict. The extra C504.2 core connection (GND40/102 instead of expected39) was traced to this via, not inferred as a beneficial fill result. Native source/geometry and initial finite-copper results are retained; the successor's `clearance.py` independently rejects this version.

See `mcu_power_ground_clearance_0109` for the limited XY-clearance successor. It still has181 unconnected items and open EP-via manufacturing qualification. Neither board is allowed to be fabricated or powered from this evidence.

The initial FPID Python pointer-representation check, multi-load API failure, and incomplete/contaminated exploratory negative outputs are excluded from claimed passes. Explicit REJECTED logs are retained. `materialize.py` reproduces this rejected geometry only; the successor's exact native reversal test reconstructs it as a negative case.
