# Pressure frontend bounded routing screen — 2026-10-30 04:25 UTC

**REJECTED GEOMETRY / NOFAB / NOPOWER. No native board was created or modified.**

Parent: `hardware/imu_j107_clock_native_0405/native/mainboard_revD.kicad_pcb`, SHA256 `d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22`. Preserve parent 0 DRC / 120 unconnected / 0 parity (inherited result, not rerun here), AON35/GND68/SENS12 core. Parent files were read only.

## Verified physical/source contract
Source audit 0312 and source revision 0318 remain authoritative. R503 is 47k ±1%, YAGEO RC0603FR-0747KL; R504 1k; C504 1n. U101 package pad7 is GPIO2/RTC_GPIO2, not GPIO7. Native pad centers:
- U101.7 F(2.575,9.8), NIB_CONTACT_N.
- C504.1 B(3.475,9.75), NIB_CONTACT_N; C504.2 B(5.025,9.75), GND.
- R503.1 B(1.675,11.5), AON; R503.2 B(3.325,11.5), NIB_CONTACT_N.
- R504.1 B(2.175,54.25), NIB_CONTACT_N; R504.2 B(3.825,54.25), CONTACT.
- J103.1 B(3,52), CONTACT; J103.2 B(5.4,52), GND.
Thus the capacitor is MCU-local, but series R504 is connector-local, not MCU-local. No source/footprint changes are made. Native B52 connector is not the virtual B70.5 station.

## Two evaluated topologies and stop
`strategy1.py` tested left MCU escape at (1.95,9.8) with explicit .45/.20 signal via and In4 x1.95 long trunk. It collided with STRAP_GPIO3 F/In3 copper and drill clearance; the trunk crossed three existing GND vias. AON first via also intersected its own R503 pad; that unsafe same-net case was explicitly rejected.

`plan.py` is the second topology: bent MCU escape to (1.85,9.5), In4 x2.8 trunk, J103 upper-side GND access. It still intersects STRAP_GPIO3 In3 clearance. The new trunk intersects GND, BOOT_N and SENS_D7 copper. The J103 upper-side GND route hits HREF/VSYNC fanout, including drill clearances. Logs retain exact UUIDs; `obstacle_geometry.json` records their native coordinates and relevant complete signal nets.

In strategy2, local AON stub/via (1.3,12.65), C504 GND B branch to **existing** shifted GND via (4.25,10.75), and CONTACT short B connection have zero geometric errors individually. This is NOT a complete pressure circuit or an electrically verified partial board; none was materialized.

The helper screens all six copper layers, 0.15mm foreign-copper clearance, actual via drill-spacing and same-net/all-net via-pad annulus intersections, outline/rule areas. It is a preflight model, not KiCad full DRC, filled-zone connectivity, assembly or EMC approval. No third topology/grid search was attempted. Two rejected straight-corridor hypotheses do not prove that fixed-position routing is impossible.

## Proposed next scope — requires routing-owner decision
First review a **whole STRAP_GPIO3-net reroute proposal** jointly with the NIB MCU escape, retaining its exact source endpoints and physical pad component. The existing route has a large In3 loop; replacing only the local diagonal or silently deleting vias would leave an incomplete review. Exact old copper UUID inventory is included; derive replacement geometry before native mutation. Restrict other old signals to unchanged until a complete proposed route is independently screened. This local reroute alone does not solve the J103 or full longitudinal corridor: use a layer/obstacle topology study for the full NIB path and J103 ground branch, not repeated blind waypoint attempts. If additional old-net reroutes prove necessary, enumerate their entire affected subgraphs before approval.

Any later native candidate must preserve R503 source/MPN, all footprints/source nets, clock geometry/length and old pad components; full fresh fill + ERC/DRC/parity, true all-pad graph, all-layer same-net via checks, exact replay/rollback, meaningful native-cut negatives and independent review are mandatory. No completed-native, reduced-airwire, AON>=3V, contact lifetime, debounce/ESD, firmware wake or physical actuation claim is supported here. JP301 stays OPEN; do not power unknown camera/battery hardware.
