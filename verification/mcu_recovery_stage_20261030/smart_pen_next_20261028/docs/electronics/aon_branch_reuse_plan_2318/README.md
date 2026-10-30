# Read-only AON whole-branch reuse plan — NOFAB

No native board was created or changed. This plan is bound to conservative GND research board **ead39fa832de2aabff4fbec9ce67d12199094ac9d77e700de54920d8fec86959**: 630 copper objects,102 footprints,366 physical pads; native0/203/0; AON1/39 and GND30/102 pads presently reach their J106 source cores.

## Bounded proposal

The original9a03 AON net contains188 copper objects in22 complete track/pad subgraphs, excluding zones. Every object was rechecked against the actual current copper, actual pad layers/positions, drill clearance and unchanged-source endpoint identity. The stale2005 conflict table was not used.

Eight whole groups / **41 original objects** pass the limited screen and reach the present AON source in a finite-copper **hypothetical** model. Group IDs are0,2,5,6,8,10,15,19. Exact UUIDs, widths, drills, layer sets and coordinates are in `evaluation.json`; a compact summary is `proposed_groups.csv`.

- C104.1 ↔ U101.20
- R240.2 ↔ R241.2
- C105.1 ↔ U101.46
- U101.55 ↔ U101.56
- C102.1 ↔ R102.2
- R101.2
- R103.2
- C207.1

The model adds13 source-connected pad terminals, yielding a **hypothetical14/39 AON** total. This is not a native DRC result or a prediction of functional power-up. Eight whole-group deletion counterfactuals each disconnect their own terminals.

The other14 old subgraphs remain rejected, including changed U201/U202/U203 AON-side pins and C201/C203/C205 decoupling. These must be jointly rerouted for the current component placements, not copied to obsolete coordinates. Original main-feed and U301/U204 branches that conflict with the current layout are not included. Net3V3_AON and external-head SENS_VIO remain distinct; no source mapping, voltage-domain change or GPIO assignment was made.

## Geometry and return bounds

All proposed objects were screened against actual current pad/copper geometry and through-hole drills, including same-net via-in-pad exclusion. The complete proposed groups also pass actual Edge.Cuts0.25mm and native rule-area checks. Their10 original through-vias retain0.60/0.30mm dimensions; the45 new-via-pair drill comparisons have minimum nominal drill gap1.880166mm. No footprint or source branch is trimmed or narrowed.

The limited planar estimate subtracts proposed AON via antipads from copies of the current GND zones. Each main GND layer loses approximately **6.358612791mm²** of modeled copper. With the one-shot normalized representation described below, each zone's0.25mm eroded component count stays1. Existing SENS track-reference projected additional loss is0 in this model. Current30 core-connected physical GND pads remain connected in the cutout finite-copper model.

These are **pre-fill estimates only**. Native fresh fill can remove islands or produce geometry differing from a simple Boolean cutout. No full-load current path, minimum useful width, thermal behavior or RF/EMI return qualification follows from the component count or projection result.

## Original width is not power qualification

Some original branches are only **0.15mm** wide. This plan preserves those widths exactly rather than silently narrowing anything, but does **not** certify them as adequate supply conductors. Frozen source pin names identify U101.20 asVDD3P3_RTC, U101.46 asVDD3P3_CPU and U101.55/56 asVDDA. These are real supply/analog pins, not merely logic pull-ups; current, voltage-drop, transient and decoupling-route requirements remain to be checked.

The broader0.5mm conductors in the C102/R102 group retain their original width. They do not turn every0.15mm fanout into a0.5mm qualified main path.

`role_and_return_limits.json` reads the exact frozen source symbol and current physical-pad core status. All nine U101 ground physical pads are still disconnected from the source core. C207.2 is also still disconnected because its prior GND group was not restored. Therefore attaching the listed supply branches would not qualify U101 or C207 as operationally powered/decoupled. C104/C105/C102 ground terminals presently reach core, but device-level power integrity remains open.

## Mandatory polygon interpretation correction

Use `filled_polygon_erosion_erratum_v2_2327` (manifest9def5b5758a1383e0276a3cb7256d4c23c3bf931791946ba8ae50e4681d087d1). Raw saved native fill is fractured-hole encoding. The old7/8/7 AON and11 GND erosion counts were encoding-sensitive, not physical-neck proof.

This plan uses a byte-identical `native_polygon.py` guard only once on known raw native `GetFilledPolysList()` input; explicit-hole inputs are rejected. **Unfracture is not idempotent: never call it again on an already hole-bearing Boolean result.** Subsequent cutout operations retain their hole contours. Numerical conversion and actual via-void boundaries are covered by the separate v2 correction, not waived here.

## Reproduction and stop condition

- `plan.py` / `-O`: reconstruct all22 whole original AON subgraphs and fresh current conflicts.
- `evaluate.py` / `-O`: actual board/rule checks, hypothetical core graph,8 causal deletion negatives,10-via45-pair drill checks, normalized reference-plane cutout estimate and current GND core retention.
- `export.py`: exact source pin roles, present device return state and CSV.
- Native inputs remain byte-identical; dependent source files and correction hashes are listed explicitly.

Next authorized design step, if chosen, is a **new** bounded native candidate restoring only these41 original objects, then full same-project DRC/parity, actual fresh fill, all prior chain/pad invariants, source/ground-core checks and normalized reference/return analysis. If a group fails those checks, reject or separately redesign it; do not silently lower rules or extend this plan to the other14 groups.

The present read-only task stops here. **No copper was added, no plane was cut on the native board, no manufacturing or power-up is permitted.**
