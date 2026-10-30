# Bounded MCU VDD3P3 joint topology evaluation — BOTH REJECTED

Base PCB `66d5343409eaf0cf58458759f033e9eea74865e1ea85b83ecc0c3068d2032141` has780 copper objects. **READ-ONLY / NOFAB / NOPOWER. No native edits or accepted successor.** Exactly two complete topology hypotheses evaluated, then stopped; no iterative path scan. Failure of these hypotheses is not proof that the board cannot be routed.

## Complete hypotheses, not deleted-control-net tricks

`plan.json` contains every exact object and six original CHIP_EN/BOOT_N segment UUIDs proposed for replacement. Both preserve all old physical pad components in the abstract finite-copper model. EN reconnects U101.4/C101.1/J108.1/R101.1; BOOT reconnects U101.5/J108.2/R102.1. U101.2/.3/C103.1 reach J106.2 through the modeled AON-plane access; C103.2 already reaches J106.3. These per-net checks do **not** excuse inter-net collisions, and neither plan is nativeable.

Two0.25mm escape segments each0.675mm center-to-center (roughly0.35mm beyond left pad edge), then either0.635mm or0.508mm branches. Total new AON trace lengths4.0402/3.9639mm respectively; one0.60/0.30mm AON through via at(.65,8.9)/(.65,8.8). BOOT short layer transfer proposed at(1.95,9)/(1.98,9),0.45/0.20mm hole, onto In2 back to existing(1.26,9.7) access. No ground-layer trace/long slot is proposed, no RF/matching copper or footprints moved.

## Specific blockers

-25mil branch object3 violates U101.4/CHIP_EN pad clearance. Full-width cannot simply be brought to the densely pitched SiP edge.
- Both EN restorations clash with the new AON branch and preserved BOOT via(1.26,9.7), not merely obsolete segments.
- New BOOT through hole clashes with restored EN;20mil case also clashes with actual In3 STRAP_GPIO3 UUID320384e6-70de-4a90-9034-9e5c1855fea9.
- Both new BOOT holes overlap built U101 F.Courtyard (0.05503/0.06831mm²). This body/assembly constraint is reported separately from pad copper; no manufacturing approval is inferred.
- Hole-induced nominal GND plane cuts remove~1.0394mm² per main GND plane.25mil case yields **two** components after guarded one-shot Unfracture+0.25mm erosion, so it is rejected also for reference-plane narrowing.20mil yields one, which does not qualify its rejected routing. `check.json` records nominal exclusion and old signal projection losses; these are not actual freshfill results.

## Why no direct access at y7.8?

`direct_access.json` probes six fixed centers, not an exhaustive search.0.60/0.30mm vias at x1.2/1.4/1.6/1.9,y7.8 intersect **both C103.1 F.Cu and R503.1 B.Cu** actual pads, including same-net pads; x1.9 additionally violates In3 STRAP_GPIO3. At(1.2,7.0), actual C103.2 GND clearance and back-side R503.1 obstruct; at(1.9,7.0), RF_SIP, STRAP_GPIO3 and R503.1 obstruct. Therefore these suggested direct locations cannot be used under the current no-via-in-pad rule. No claim is made that every possible upper or lateral approach is impossible. Filled/capped via-in-pad would be a different manufacturing/footprint decision requiring qualification, not a routing waiver.

## Official guidance and unqualified supply path

[Espressif ESP32-S3 PCB power guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#power-supply), read2026-10-30, distinguishes25mil main feed,20mil pins2/3 and10mil other supplies. It also recommends multiple main-path layer-transition vias, substantial supply drills, decoupling and intact RF ground. It is chip/module guidance, not unconditional SiP approval. Neither0.25mm escape nor single0.30mm supply drill here is asserted to satisfy the complete guidance. The existing source J106.2→AON plane is a distributed finite-copper path, not a uniquely measurable centerline length; its shared loads, necks, upstream feed width and current/thermal/PDN behavior remain unqualified. A successful local branch alone would not close these gates.

All original source/rules/PCB inputs remain unchanged. JP301 OPEN and external SENS isolation unchanged. Normal/-O reports identical. Future work needs a new explicitly bounded topology or qualified placement/manufacturing change; no additional native copper authorized by this rejection report.
