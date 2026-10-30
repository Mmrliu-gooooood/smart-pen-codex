# Joint pressure / STRAP escape topology — readonly plan 04:29 UTC

**NOT A NATIVE CANDIDATE. NOFAB / NOPOWER.** Supersedes rejected direct-corridor hypotheses in `pressure_route_plan_0425` only as a prospective plan. Neither frozen parent nor source/footprints were modified.

Parent SHA256 d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22. Read `plan_result.json` for every exact proposed object, layer, size and removed/retained STRAP UUID. Full parent has 120 unresolved edges; no reduction is claimed until native refill/full checks.

## Geometry and complete signal endpoint constraints
Normal and `python -O` execute identical runtime guards. All planned objects jointly pass the inherited six-layer finite-copper geometry screen (0.15mm foreign-copper spacing; actual drill spacing; all-layer same-net and foreign-net via-pad intersection rejection). This is not KiCad DRC. In-memory copper graphs verify:
- STRAP_GPIO3: **U101.8 ↔ R103.1**. Source pull resistor and all source pad/net assignments stay unchanged. Four exact local copper objects are replaced; every other object of the full old STRAP graph is retained. Proposed replacement F stub → .45/.20 via (1.65,10.5) → In3 (2.4,9.75) → existing In3 (2.4,9.575). This explicitly reconnects the complete signal graph, not an isolated gap patch.
- NIB_CONTACT_N: **U101.7 ↔ C504.1 ↔ R503.2 ↔ R504.1**, all four pads in one physical component with finite-width copper.
- CONTACT: **J103.1 ↔ R504.2**.

R503 remains actual YAGEO RC0603FR-0747KL 47k ±1%, R504 1k, C504 1n. U101.7 is GPIO2/RTC_GPIO2, not GPIO7. All footprints stay fixed. J103 remains actual B52; R504 remains B54.25. Capacitor is MCU-local; series resistor is NOT MCU-local.

## Signal-layer plan, avoiding reference-plane slots
NIB MCU escape F to .45/.20 via (1.85,9.5). Short B connection to capacitor and R503. Long path is **In3 exclusively**: north/west around existing BOOT via, descend x0.6 to y13.5, then x1.95 from y14.85 to29, shift west to x0.8 by30.15, bypass the known GND vias at (1.525,31.1375) and (1.525,36.8625), return x1.95 at38.65, descend to51.8, west to (1.2,52.55), terminate via (1.2,54.25) and short B stub into R504.1.

**No new In1/In4 track and no long reference-plane slot.** New through vias necessarily create local antipads in GND reference layers where signals/AON differ; their fresh-filled geometry, actual native holes, reference continuity and board-edge ground necks still require explicit native verification. In3 reference must not be presumed perfect from a nominal layer label. The final western x0.6 corridor also needs that check. Do not substitute a long In1/In4 trace.

## Power/return branches — geometry only, not yet plane connectivity proof
- R503.1 B stub to standard .60/.30 AON via (1.3,12.65).
- C504.2 legitimate B GND branch to the **existing** shifted MCU GND via (4.25,10.75); do not resurrect the old colliding via at (4.5,10).
- J103.2 B branch to standard .60/.30 GND via (5.4,55), avoiding upper HREF/VSYNC escape.
The J103 ground via lies under the U203 body, outside all copper pads. This is not an assembly signoff: via tenting/mask, component stand-off, solder migration, board side and manufacturer process require DFM review. It is distinct from the inherited MCU EP via-in-pad gates. If unacceptable, change proposal before materialization, do not silently waive.

An initial integration of the otherwise-clear local AON stub revealed the NIB diagonal crossing its new via; retained `rejected_joint_aon_intersection.log`. The resolved bounded dogleg stays at x0.6 until y13.5. Both normal/optimized final screens are zero-error. All full pressure pads have planned copper, but AON/GND plane joins and baseline AON35/GND68/SENS12 preservation are **not established without fresh native fill**. Do not call all seven gaps electrically closed yet.

## Required next approval and release barriers
Routing owner must accept this exact full joint topology and body-under-via DFM condition before native materialization. A later complete candidate must preserve all old physical pad components, source files, footprints, all other track UUID/geometry including SENS_EXTCLK length, JP301 OPEN, and reference connectivity. Fresh KiCad fill / all-track DRC / ERC / parity, same-net all-layer via-pad audit, all-pad graph, every pressure gap, exact replay/rollback, and native cut negatives (STRAP reconnection, NIB long connection, local GND branch, CONTACT) remain mandatory. No native PCB is emitted here.

No contact life, AON≥3V, debounce/ESD, physical force, firmware wake, optics, thermal, manufacturing or charging qualification claim. Unknown camera and battery hardware must remain unpowered.
