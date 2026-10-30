# CAM_ON-only maintenance: independent review — NOFAB

**Decision: suitable as the next J107/J103 routing baseline.** This is approval of a constrained maintenance delta, not whole-board clearance, manufacturing or dynamic gate safety.

Input PCB **1c4907d04a2bf2dea3a53f89266bc49c0cb96a0683b4898b58cd36b6525ec16d**, source manifest **691382b1d07926ef4430f8aaa98f64f5cf04006f5bd2dd0726adeb657c548de1** (103 entries). Baseline 508e / manifest **70f161b643809f8c930c2b32bf82725be6ba742d52635171442646c5bfd6cf52**. Both complete input manifests independently checked. Source unchanged; review operates only on its isolated native copy and excluded corrupt fixtures.

## Fresh result and physical scope
Same-basename project/custom rules, explicit layer stack and source retained. Fresh command:
```
kicad-cli pcb drc --format json --exit-code-violations --all-track-errors --schematic-parity --severity-all -o drc.json native/mainboard_revD.kicad_pcb
```
Result **28 violations / 41 unconnected / parity 0**, exit **5**. Full finding multiset (description, item UUID/coordinates, ignoring item order only) exactly matches 508e; not merely equal counts. Fresh XML retains 102 entities / 356 endpoints and all ten native Manufacturer/MPN/ProcurementStatus fields. All source/project/library files byte-match 508e. Routing preflight passes configuration binding; manufacturing remains unapproved.

- Only CAM_ON tracks change: **41 removed / 6 added; 44→9 total**, .15 mm width. Measured length **11.995332→11.542938 mm**.
- All three original CAM_ON vias and every surviving conductor geometry remain unchanged; all 102 footprint/pad/source identities unchanged.
- Actual F.Cu T junction `(8.4,67.95)` remains copper-connected; independently measured physical incident branch degree **3→3**. Old horizontal copper passes through the T point internally (one explicit endpoint); new copper splits there (three explicit endpoints). A preliminary endpoint-only counter was corrected to include segment-interior junctions; this was a checker issue, not a broken branch. U301 stub and retained anchor branches preserved.
- Full finite pad/track polygons, annular vias minus holes, actual filled islands: **all 90 net pad partitions identical**. All six AON plane islands still physically connect to core.
- No new changed-copper overlap with any foreign net. JP301/MEMS and gate-source connectivity also checked by the full underlying audit.

## Real route change, fill and adjacent reference
This **changes finite copper geometry**, not an equivalent collinear merge. Copper union removed/added areas (mm²): F **.419335/.377332**; B **.212122/.193535**. Exact delta coordinates/UUIDs are in the copied `maintenance_delta.json`.

All five zone-layer filled-polygon serializations match 508e and a fresh refill of the isolated candidate; no new plane split or neck geometry introduced. Existing plane/neck qualification is **not** inferred from unchanged geometry.

Finite CAM_ON pad/track/via copper lacking adjacent ground projection (mm²):
- F→In1 **.803601→.795228**.
- B→In4 **.815287→.815167**.

Both decrease; script explicitly rejects worsening. This metric includes via antipads/pad projections and is not electromagnetic return length, impedance or noise qualification. No body placement or edge clamp strip was changed.

Native integer-nanometre length thresholds reproduce CAM_ON sub-.1 mm segments **28→0**; whole routing batch short segments **669→641**. Other nets' routing complexity remains, not silently cleaned in this block.

## Reproduction and limits
Normal and optimized checks: `verify_maintenance.py`, `audit_gate.py`, `independent_checks.py`, `track_statistics.py`. `verify_source_refill.py` verifies source/MPNs and fresh fill. `maintenance_negatives.py` rejects changed added width, moved retained via, moved TP301 and changed fill in both modes: **8 expected rejections**. Reports retained; malformed fixtures excluded from manifest. Verified sibling dependency manifests must accompany local reproduction.

**Do not** claim 28 existing violations / 41 unconnected items fixed, or inherit whole-pen manufacturing approval. Prior CT return, startup/noise, QOD pulse, IO/body-diode backfeed, unknown camera load, mechanics/assembly, cost and safety gates remain. No source edits, external write, procurement or device action. The next routing stage must use this exact candidate and recheck its own collateral delta.
