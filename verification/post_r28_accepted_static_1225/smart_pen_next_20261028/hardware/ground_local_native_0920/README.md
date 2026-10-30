# R218 ground-only candidate — pending independent review

**NO FAB / NO POWER. JP201/JP202/JP301 OPEN; firmware provider NULL.**

Parent0818 PCB `abd8a388a606582e80ebe5f59da7579f7020cd44be6af494e032b8f69fde8ca0`.
Candidate PCB `ff70d9171b364e2d89ce13d109f22a2362afe76c340d384e194fb541bed6af8a`.

## Implemented and checked
Two B.Cu GND tracks, each0.3mm, no new vias:
R218.2(5.325,41.5) → (3.825,42.4) → R225.2(5.325,43.3)mm.
3.498571mm total centerline length. R225 retains the accepted R220 core branch; this adds a dependent ground leaf, not an independently redundant return path. All1229 old copper objects and103 footprints retained;1231 copper objects now. Full54-file native diff changes PCB only.

Real all-severity/all-track/schematic-parity DRC: parent0/76/0 → candidate0/75/0. ERC0errors/1 inherited dangling-global-label warning. Actual finite copper graph GND91→92/103, AON41/41, SENS12/12. Only R218.2 joins GND core, every non-GND component is exactly unchanged. Remaining11 grounds include R104, six J202 pins, R219/R229/J105/J107. No camera signal or source edits.

Finite foreign copper/edge/rule/drill checks pass. No new via, hence no new via/pad or via/courtyard overlap. Native normalized filled-plane comparison finds no additional retained signal-reference projection loss. Historical losses are not erased or reclassified as an SI pass. Raw balanced-block comparison verifies every old copper/footprint byte-identical. Native source/rules/stack and provider unchanged.

Actual negative cut removes both added tracks, refills/reloads and restores every parent's net component exactly plus DRC0/76/0; R218 returns singleton. Fresh reconstruction matches all54 native files. Actual reverse unified diff restores all54 parent native files byte-for-byte and real rollback DRC0/76/0. Normal/-O verification, physical, negative, raw delta and replay reports match. All failures use explicit exceptions, not removable assertions.

## Scope and unresolved gates
No assembly or mechanical approval. Board outline remains x0..14,y−6.5..95 =101.5mm total; **does not meet the newly emphasized≤100mm requirement**. This local routing candidate is not that mechanical correction. J202 tail/connector gate, R104 RF gates, J104 physical probe/mask/tenting gates and all historical thermal/EP/DFM gates remain. No RF or J202 changes.

Static routing does not resolve dynamic five-OE load/edges, loaded GPIO VOH, real supply sequence/brownout, camera identity/voltage, firmware operation, battery/charging safety, cost or manufacturing readiness. No purchase/upload/power/fabrication performed by this worker.

## Reproduction
Use `/usr/bin/python3` with pcbnew9.0.2, kicad-cli, GNU diff/patch; always isolated copy. `materialize.py` rebuilds from pinned parent and `selected_final.json`; `GROUND_NATIVE_OUTPUT` redirects reconstruction. Then `run_checks.py`, `verify.py`, `physical.py`, `negative.py`, `replay_rollback.py`, `raw_delta.py`, `render.py`; repeat validation scripts with `-O`. No planner needed for reproduction. `manifest.json` is an explicit validated-evidence allowlist; excluded exploration is not a release payload.

## Local diagnostic disclosure — excluded from upload allowlist
An initial search used PAD.GetLayer instead of actual IsOnLayer copper membership. DRC count alone dropped but wrong named target remained disconnected; target-specific finite graph rejected it. Corrected search uses IsOnLayer and the final candidate above. `rejected_wrong_pad_layer/` preserves rejected-local forensic files, explicitly NOT validated release evidence. Search scripts/logs/alternate selected candidates are local exploratory artifacts, excluded from manifest; no automatic upload authorization. This failure demonstrates why named-pad physical verification is required in addition to DRC totals.
