# Independent bounded seven-object gate-power review

**NOFAB / NOPOWER. Formal accepted 9a03 is unchanged. Not whole-board or complete-power qualification.**

Author `hardware/gate_power_candidate_0228`: 102-file manifest SHA `e9f8a362c5ca924969d7304ed59733635c3d3dcd0adbca972ef83f1f2179263f`; PCB `66d5343409eaf0cf58458759f033e9eea74865e1ea85b83ecc0c3068d2032141`. Parent `ca66f962b84eb96367d52a6b6fc400617c9706bfe666cf964638956cd57f4c5a`. All author file/dependency hashes intact before and after; original candidate files were not modified.

## Results

- Fresh KiCad9.0.2 full CLI with bound same-basename project/rules/source, `--all-track-errors --schematic-parity --severity-all --exit-code-violations`: **0 violations /137 unconnected /0 parity, exit5**. Remaining137 prevents completion claims.
- Independent finite physical-UUID copper graph: **AON25/39, GND61/102, SENS12/12**. Existing nine translator bypass relationships remain; reproduced author eight gate/cap/return relationships and every prior pad component retained.
- All773 prior copper objects retained unchanged; seven additions, total780. Actual AON additions are **two 0.5mm-wide B.Cu tracks**, not a2.5mm width: U301.1(10.8,66.05) to old AON access(10.9,64.875), onward C301.1(10.95,64). Ground additions are four0.3mm tracks and one0.60/0.30mm through-via(12,67). Native details saved in independent.json.
- All102 footprint identities/poses and366 physical pads unchanged. Reproduced native-text stripping confirms exact noncopper/zone definitions/source/rules/outline; exact gate3 plan replay equals candidate bytes after fresh-fill stability check.
- Independent annulus AND drill screen against all actual physical pad layers, including same-net: no new-via overlap. Deliberately moving the new GND via into C301.2 is detected by the drill screen. Reproduced author full new/old clearance, hole/edge/rule and built-courtyard checks pass nominal geometry.
- Independent SENS versus AON/GND/CAM_SW copper intersections absent; external SENS remains a reference input, not an on-board supply. JP301 pad1=CAM_3V3_PRELINK, pad2=CAM_3V3_SW; direct actual-layer copper intersections between these two nets absent. Unchanged footprint/source remains OPEN, no commissioning bridge.
- Normal/-O independent checks and reproduced author checks byte-identical. Actual native_view.png inspected.

## Plane precision and nominal margins

Guarded one-shot raw-native Unfracture, not repeated normalization or raw fractured erosion, reproduces five filled-plane0.25mm eroded outlines each one component and no additional previous signal reference projection loss above model threshold. **AON subtraction is not exactly zero**:1.8674e-08mm², bbox[8.5495,67.151613,0.012235,0.045660]mm. Other plane deltas zero. This numerical-scale remote difference is retained, not rounded into an exact-preservation claim.

New via center to actual AON copper0.500mm; nominal exclusion radius0.450mm; remaining nominal margin0.050mm and exclusion overlap0. This margin is not fabrication/registration tolerance qualification and does not establish current, temperature, transient, or IPC adequacy. Full evidence in reproduced_physical.json and reproduced_plane_detail.json.

## Native counterfactual and negatives

Independent review copy remove-all-seven/rebuild/fill returns exact parent ca66 SHA and **0/143/0**, exit5. Exact replay returns66d534 SHA. Reproduced five actual native deletions, each freshly refilled/fullCLI plus physical pad disconnect checks: AON two tracks **0/139/0**; U301 ground via **1/138/0** (expected dangling-track warning); output capacitor, timing capacitor and pulldown returns each **0/138/0**. Independent finite graph separately checks all five intended disconnections. See reproduced_negative.json and native_negative/*/drc.json; no hypothetical native results substituted.

## Remaining gates

JP301 stays OPEN. Gate enable path,137 remaining connections, actual camera pinout, external-reference load/startup capacity and sequence/back-power, battery/charging, load peaks/temperature and product tests unqualified. 0.5mm VIN/0.3mm returns are chosen nominal geometry, not rated-current evidence. Prior8 MCU in-pad holes and23.8µm nominal EP hole-edge margin remain unresolved manufacturing risks. No power, procurement, fab, radio, flashing or upload occurred. Scope was the seven-object block, not expansion into unrelated routing.

## Reproduction / publication

Only review_manifest.json allowlisted files are review publication artifacts. Local native/support duplicates excluded. Reconstruct at hardware/<review> under the same repo root using immutable author native/, verify.py, finite_copper.py, native_polygon.py, materialization.json, drc.json, native_negative.py, materialize.py, noncopper.py, physical.py, plane_detail.py and declared dependencies (including remaining_power_return_plan_0208). Keep this review's own independent.py and counterfactual.py. Run /usr/bin/python3 independent.py and verify.py normal/-O; counterfactual.py; native_negative.py; noncopper.py; physical.py; plane_detail.py. Replay materialize.py with GATE_NATIVE_OUTPUT=<review>/replay/native. Source recovery note docs/electronics/gate_power_recovery_0232 was read only. All stageability is limited to allowlists, not duplicate experimental directory trees.
