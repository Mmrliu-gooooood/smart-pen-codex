# Authoritative recovery addendum — 2026-10-29 23:27 UTC

The mandatory correction is now `filled_polygon_erosion_erratum_v2_2327`, manifest SHA **9def5b5758a1383e0276a3cb7256d4c23c3bf931791946ba8ae50e4681d087d1**. V2 supersedes broad conversion advice in v1 and raw erosion interpretation in the 23:15/23:21 indexes.

Raw native filled polygons use fractured hole encoding. The recent raw AON7→8→7 and mainGND11 erosion piece counts are encoding-sensitive, not proof of physical neck splitting. On the fixed native inputs, guarded one-shot Unfracture yields explicit holes; each plane remains one component under0.25mm erosion. Numerical set differences and835physical foreign-via void checks are retained, not ignored.

IMPORTANT: Unfracture is NOT idempotent. Applying it to an already hole-bearing Boolean result can remove holes and falsely add copper. Only use it once on known raw native fractured fill; reject explicit-hole inputs, check material area and void preservation. Never call it again after BooleanSubtract. V2 includes a deliberate rejected repeat-call example and normal/-O guards.

Native board hashes/DRC/core connectivity and exact replay are unchanged. Research ead39 remains0/203/0, GND30/102,AON1/39,NOFAB. The earlier omission of group37 was over-conservative on the raw-erosion premise; no branch is automatically reinstated.

`aon_branch_reuse_plan_2318` is a separate read-only proposal against actual630objects/366pads: eight complete old groups,41objects, hypothetical14/39AONpads at core. It is not native materialization, fullDRC or actual fresh-fill validation. Legacy0.15mm MCU rail fanouts must not be mistaken for0.5mm qualified main supply paths.
