# 18 / 18.5 / 19 mm conditional tolerance comparison — NOFAB

Separate supplement to `flex_power_revD_study`; frozen CAD/input files are unchanged. Reproduce: `/usr/bin/python3 sweep.py`.

## Explicit assumptions, not supplier tolerances

- OD is treated as exact because no outer-diameter tolerance has been specified.
- Nominal wall1.2 mm, diagnostic tolerance±0.1: use worst1.3.
- Allow0.2 mm outward radial assembly displacement/board bow. This is a conservative radial bound, not a measured bow distribution.
- Separately allow0.2 mm loss of relative inter-board spacing. Common barrel displacement and differential board placement are different effects; both must be checked.
- Unknown passives:1.3 mm body plus0.15 mm assumed solder. Known package heights unchanged.
- Power assembly total thickness4.15 mm remains conditional; batteryØ12.2 and USB5 mm budgets remain conditional. Their actual tolerances are not supplied.
- Actual sampled HREF3 board has R105/R214/R220 on B side;16 schematic parts still absent. Source SHA256 in JSON.

A screen with zero remaining clearance only means mathematical non-penetration. An additional **0.10 mm residual clearance** is reported as an explicit engineering comparison, not a product standard or complete tolerance allowance.

## Compact result

All values below are worst remaining radial clearance / worst inter-board clearance in mm.

| Arrangement | 18 OD | 18.5 OD | 19 OD |
|---|---:|---:|---:|
| Existing213, passives1.0 | -0.0032 /0.10 |0.2468 /0.10 |0.4968 /0.10 |
| Existing213 unchanged, passives1.3 | -0.2005 /-0.20 |0.0495 /-0.20 |0.2995 /-0.20 |
| Repositioned213, passives1.3, nominal gap0.20 | -0.1228 /0 |0.1272 /0 |0.3772 /0 |
| Repositioned213, passives1.3, nominal gap0.30 | -0.1476 /0.10 |0.1024 /0.10 |0.3524 /0.10 |
| Axially separated260, passives1.3 |0.1989 /not stacked |0.4489 /not stacked |0.6989 /not stacked |

**Simply increasing barrel diameter does not fix the existing stack:** with1.3 mm passives its nominal inter-board gap is zero, and the differential-placement allowance makes it -0.20 mm at all three diameters.

Repositioning both boards restores a0.30 nominal inter-board gap:
- Main PCB underside Y=2.820 mm.
- Power envelope Y=-3.080..1.070 mm, still Z82..127.
- Back-passive lower face Y1.370; nominal gap0.300.
- Minimum modeled radius7.647640 mm. Add wall1.3 + radial allowance0.2 + residual0.1, giving a **radial-only mathematical OD threshold about18.4953 mm**.

Thus18.5 passes this particular0.10 screen by only **0.00236 mm radial surplus**. It must not be called a robust production size: the numerical grid is0.001 mm, and real OD tolerance, unqualified power thickness, support structure, missing parts and connectors swamp that surplus. Among the requested discrete diameters, **19 mm offers0.3524 mm radial remainder** under these assumptions, while the inter-board remainder is still only0.10. This is a candidate for further engineering, not an authorization to select19 mm or change the user's18 mm target.

For a mathematical zero-clearance-only screen, moving to mainY2.783 / powerY-3.017 restores0.20 nominal inter-board gap and gives radial OD threshold18.2456. The resulting worst inter-board clearance is exactly zero: not an assembly recommendation.

## Keep18 by removing the stack

The existing axial260 comparison places the mainboard Y1.0, power centered Y±2.075 in a separate axial segment, and avoids mainboard/power overlap. With1.3 passive height and the stated radial allowances, the limiting power rectangle leaves **0.19893 mm** at18 OD. It clears the explicit0.10 residual screen; length increases **47 mm from213 to260**.

This is an honest geometric fallback, not a recommendation for a long consumer pen. There may be shorter solutions through qualified low-profile components, relocating specific passives, a redesigned power board or a different complete battery arrangement. No component dimensions are reduced silently to obtain a pass.

The 213 and260 lengths still omit finalized front/tail closure tolerances, connector wiring, assembly supports and a qualified antenna system. The calculation is not a physical assembly or thermal/charging qualification.

## Existing purchased camera remains separate

The earlier necessary bound **OD≥24.22 mm** applies only to the nominal21.82 ear span retained in a transverse-board/parallel-optical-axis arrangement with1.2 walls, zero clearance, and unknown ear tolerance. It is not a universal prohibition on tilted layouts and not a complete oversized-head drawing. This supplement does not convert the purchased13 mm camera into an8 mm future camera.
