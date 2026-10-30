# Fresh plane fill only — NOFAB / DO NOT POWER

Base: frozen `head_power_joint_native_candidate_2141`, PCB `7e639fa62f08ba04dd5507f383e38ce1134877c5108e2527b855eb9b00b39115`.
New PCB: `d64594c0ddfcddc7b8c3a40043fe56e144f25d4c59d2fa33e30a9595054c3de5`.

## What changed and what did not

The five original plane definitions already existed empty in the base. All nine board zones (five copper, four rule areas) were compared with the 9a03 source, ignoring only old filled polygons and `fill yes` state. Definitions are exact; no need to duplicate or transplant zones. Fresh KiCad 9.0.2 ZONE_FILLER generated current polygons, then save/reload/refill produced the same bytes. No old filled polygon was copied as valid. `verify_text.json` proves the whole serialized board apart from fill flag/polygons is unchanged: 533 track/via objects, 102 footprints, all 366 physical pads, outline, rules, zone settings. Source/project/library files unchanged. No signal added, footprint moved, rule relaxed, or GND slot cut.

## Actual result: 2 violations / 232 unconnected / 0 parity

Full native CLI uses `--all-track-errors --schematic-parity --severity-all --exit-code-violations`, exit 5. Warnings are **not waived**:
- AON input via `(11.9,83.9)` is still dangling. Original AON zone ends at **x=11.5**; its 0.30 mm annulus radius only reaches x=11.6, leaving 0.10 mm physical gap even before useful overlap/width requirements. Merely filling cannot connect this entry. Need a separately screened >=0.5 mm local connection; do not enlarge plane blindly across surrounding signal/keepout clearance.
- In2 AON filled region is isolated from the source. The old floating AON bridge now touches this island, eliminating its two dangling warnings but NOT becoming powered.

Finite-copper graph uses actual pad IsOnLayer and subtracts via drills. All 19 prior whole nets and 14 endpoint chains remain. **Only J106.2 (1/39 AON physical pads) is on AON source core. Only J106.3 and J301.2 (2/102 physical GND pads) connect to GND source core.** Repeated U101.57 exposed-pad physical islands are UUID-disambiguated, not silently collapsed. `analysis.json` contains every physical AON/GND pad, actual copper layers, exact position, movement vs 9a03, old/new core membership and all open groups.

Four GND plane fragments are in the J106.3 component. Removing the one new GND core via in a non-mutating finite-copper counterfactual removes all four plane fragments from that core while preserving local J106/J301 connection. `region.json` records this; it is **not** a native CLI negative-board claim.

## Local connections still required

38 AON and 100 GND physical pads need connection. Most are SMT and cannot meet inner planes without a fanout/via. No full old load path was restored. Moved AON pads needing new placement-aware fanout: C201.1/C203.1/C205.1, U201.1/U202.1/U203.1/.2/.3. Moved unconnected GND pads include translator/decoupling cluster, J105/J107, R206, camera bias resistors; full explicit list in analysis JSON. Unmoved pads also need their missing fanout: movement is not the only cause. J202 seven grounds remain open, and no local decoupling loop is qualified.

## Clearance, references and neck limitations

200 foreign-via/zone-layer checks (all current through vias, including new 16 signal and power vias) find zero intersection between fresh zone copper and foreign via copper expanded by 0.15 mm. This is supplemental geometry, not a substitute for CLI rules/antipad inspection. Full DRC found no new short/clearance error.

At zero erosion all five zones have one polygon each (AON still electrically isolated). In1/In4 main zone **each splits into 11 fragments under 0.25 mm erosion**; AON into 7. This is a warning against declaring >=0.5 mm everywhere. `region.json` gives fragment area/bounding boxes. Some split regions are large (not merely tiny nubs); no load-path ampacity or at-least-old-return claim is made. Original same-zone erosions are recorded for context (58 fragments at that radius), but less fragmentation cannot prove better return or equivalent complete routing: most old copper/fanouts are absent. No neck was thinned to obtain a pass.

64 SENS track projections were screened against adjacent GND layers (F->In1, B/In3->In4). 32 are not fully covered at 0.99999 threshold; minimum area coverage 0.500769. Via antipads/ends contribute. This does not determine SI or return transfer across layers. Coverage alone cannot qualify reference continuity; all signal-via return stitching and J202 grounds still need work.

## Reproducibility / scope stop

`fill.py`: fresh-fill and reload determinism. `analyze.py`: multiset/source, finite-core pad groups, antipads, zone erosion, reference projection (normal and `-O` byte-identical). `region.py`: core-region graph plus single-via negative. `verify_text.py`: serialized non-fill invariance. `draw.py`: actual saved polygons; PNG visually inspected. `rejected_fillflag_comparison.log` documents initial overly strict comparison that included fill-state; definition comparison was corrected transparently, not waived.

This bounded zone-only experiment is complete. Candidate is research evidence, not production release. Next stage must first design the AON entry-to-plane connection and local AON/GND fanouts against current geometry, then fresh-fill/path-specific neck/reference tests again. **JP301 remains OPEN; no charging commissioning, unknown-camera power, procurement or upload.** Formal historical 9a03 baseline is not replaced.
