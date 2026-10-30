# Correction v2: guarded one-shot conversion of native fractured fill

**This v2 supersedes the broad conversion advice in v1 (`filled_polygon_erosion_erratum_2321`) also supersedes the raw erosion interpretation in the recent 2150/2156/2159/2305 reports and the 23:15 recovery index. Frozen artifacts remain unchanged.**

## What was wrong

KiCad's saved `GetFilledPolysList()` representation uses fractured polygon outlines: holes are encoded by return cuts in an outline rather than separate hole contours. Directly calling `Deflate(0.25 mm)` on this representation was sensitive to those encoding cuts. The earlier raw counts of AON **7 → 8 → 7** and main GND **11** therefore do **not** establish physical narrow necks or a physical split caused by group 37.

For these fixed native inputs only, calling `Unfracture()` once on a raw fractured copy restores explicit holes. **Unfracture is not idempotent and must never be applied to an already hole-bearing Boolean result or previously converted shape.** `native_polygon.py` rejects explicit-hole inputs and rejects material-area changes above its stated numerical research guard. Caller provenance must still be raw `GetFilledPolysList()` data from the fixed PCB, not an arbitrary polygon. For all four examined native boards (d645, fd989, unfinalized 18-branch comparison, ead39 conservative 17-branch candidate), each of the five individual plane zones has **one** eroded component after normalization. The main GND zones recover 29 holes. AON holes are 16 in fd989, 27 in the 18-branch comparison and 26 in the 17-branch candidate.

This corrects the interpretation, not the original PCB. A single eroded component still does not qualify actual load paths, thermal/current capacity, or return paths. No automatic reinstatement of the excluded C207.2/U204.4 branch is made.

## Evidence and numerical boundaries

- `check.py`: four native inputs, twenty zones, raw versus normalized contours and 0.25 mm erosion, normal/-O identical. It never saves a board. Every source PCB hash remains unchanged.
- Bidirectional Boolean differences between normalized and raw native polygon representations are recorded rather than declared exactly zero. Largest positive-area difference is approximately **1.15e-5 mm²**; reverse differences are approximately **3.74e-6 mm²** or smaller. Native integer polygon approximations and fracture cut endpoints therefore retain their numerical boundary.
- `validate_voids.py`: a synthetic 10×10 mm rectangle with two real holes retains equal area through Fracture/Unfracture. Its direct fractured erosion has a different area; normalized erosion matches the original-hole representation. **835** foreign-via checks confirm that drill voids and an interior 0.149 mm annulus-clearance region remain empty before and after normalization. The 0.149 mm interior test is not a substitute for native 0.150 mm DRC. Same-net drill metal is handled by actual via geometry, not inferred from filled-zone hole lists.
- `normalized_comparison.png` was rendered with explicit hole contours and visually inspected. The red rectangle locates the previous raw-fragment report; it is no longer shown as a physical isolated fragment. Orange is native normalized copper; blue is normalized erosion. This is not a current-density map.

## What remains valid, and what does not

Unaffected by this interpretation correction: native DRC counts, exact PCB hashes, footprint/source invariance, actual finite-copper pad connectivity, exact restored old UUID objects, 12 chains/19 nets, whole-group deletion connectivity negatives, and native remove/refill replay. Their native inputs were not altered. The previous direct raw-plane erosion statistics remain reproducible **only as encoding-sensitive statistics**, not physical neck evidence.

The ead39 candidate still physically restores 17 whole GND groups/96 objects and has 0/203/0, GND 30/102 and AON 1/39 at core. Its omission of group 37 was **over-conservative based on an invalid physical interpretation of raw erosion**, not proof that that branch narrowed an actual supply route. The 18-branch comparison is not automatically accepted: it still lacks its own final reviewed supply/return qualification.

Targeted affected sources and hashes are in `affected_files.json`. This is not an exhaustive audit of every older project script. In particular:

- Recent `analyze.py`/`region.py` outputs in 2150/2156 and their 2159 reviews include raw erosion counts.
- 2159 GND `neck.py` and 2305 `neck.py`, `compare_removals.py`, `decision.json`, README and blue-overlay graphic used those counts to explain group withdrawal.
- `MAINBOARD_RECOVERY_20261029_2315.md` must be read with this correction. Do not reuse its raw-fragment wording as a physical finding.

## Going forward

Use the guarded one-shot conversion only on known raw native fractured polygons before morphology, retain hole/area and actual via-clearance checks, and independently check source-core connectivity and actual load-path clearance. A new AON branch reuse proposal in `aon_branch_reuse_plan_2318` uses normalized polygons for its limited planar cutout estimate. It remains read-only, not a native fresh-fill or electrical sign-off. Never reapply Unfracture after BooleanSubtract: a hole-bearing result must retain its existing holes.

**NOFAB remains in force. Do not power, fabricate or treat any research board as a consumer product.**

## Additional v2 negative test

The synthetic test intentionally calls unguarded Unfracture on a second copy of an already hole-bearing polygon to demonstrate the API hazard: the two holes disappear and the area rises from 93.716972543504 to 100 mm². That result is explicitly rejected and never used. The guard rejects this second call before modifying any geometry. Both normal and -O tests pass; all 835 physical void checks remain empty. This is a correctness precondition, not an engineering tolerance exemption.
