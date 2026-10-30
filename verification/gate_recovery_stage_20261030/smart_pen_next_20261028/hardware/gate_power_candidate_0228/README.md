# Gate supply and paired returns — research candidate only

**NOFAB / NOPOWER. Not a finished pen and not a replacement for the accepted manufacturing baseline.**

Parent: ca66f962b84eb96367d52a6b6fc400617c9706bfe666cf964638956cd57f4c5a.
Candidate: 66d5343409eaf0cf58458759f033e9eea74865e1ea85b83ecc0c3068d2032141.
Exact seven-object gate3 plan from `docs/electronics/remaining_power_return_plan_0208/gate3.json`; no MCU RF attempt, no unrelated nets, no original copper or footprint movement/removal.

## Actual verification

- Fresh native fill twice is byte-idempotent. Independent materialization replay is byte-identical.
- Native all-track DRC, all severities, schematic parity: **0 violations /137 unconnected /0 parity**, exit 5 because unfinished connections remain. Previous143→137.
- Retains773 original copper objects; adds six tracks plus one through via, total780.
- Finite physical copper including actual pads and filled planes: AON core25/39, GND61/102, external SENS12/12. All prior pad components and eight local gate/cap/return pairs preserved.
- All non-copper text and zone definitions exactly preserved; source/project/rule files unchanged. Normal and Python `-O` verification results identical.
- New copper full-layer clearance/hole/board-edge/rule checks pass. New via has no pad overlap on **any** physical layer including same-net; built courtyard caches report no nominal overlap.
- Native deletion/refill negatives: AON two-track removal →139 unconnected; each of four GND return removals →138. Removing U301 ground via also intentionally leaves one track_dangling warning. All five disconnect the intended physical pads from the core.
- Five actual filled planes retain one component after guarded single Unfracture and0.25mm erosion; no new old-signal reference projection loss. This is a geometry diagnostic, **not IPC/current qualification**.

## Near-plane margin, honestly bounded

New GND via(12,67), diameter0.60/drill0.30mm: nominal clearance antipad radius0.45mm. Actual AON plane minimum center distance0.500mm, remaining nominal margin0.050mm; exclusion intersection0. No new long slot is introduced. Freshfill AON subtraction is **not exactly zero**:1.8674e-08mm² at bbox[8.5495,67.151613,0.012235,0.045660]mm, remote from the new via. Other plane deltas zero. Small polygon/fill numerical delta is preserved in evidence, not rounded away; finite core and eroded topology remain. No fabrication tolerance qualification is inferred from0.05mm.

## Still blocked

JP301 remains physically **OPEN** between PRELINK and SW; no commissioning bridge. SENS remains externally sourced/isolated, not a local1.8V supply. Camera pinout, external supply/backpower, gate enable path, all137 remaining airwires, global feed widths, MCU via-in-pad/EP clearances, peak loads, temperature, cell safety, assembly and measured optics remain unqualified.0.5mm VIN branch and0.3mm returns are nominal selected geometry, not rated-load or thermal proof. No charging, fabrication, energization or hardware qualification authorized by this package.

See materialization.json, verification.json, physical.json, plane_detail.json, negative.json and manifest.json. Only manifest allowlist is stageable; caches and duplicate replay/negative source copies are excluded.
