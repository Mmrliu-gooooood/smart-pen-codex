# Control-pair full-envelope reroute — NOFAB / NO POWER

Accepted parent: `unused_bias_native_1017`, PCB `2a5400724239f11fe6f589c4f954441deea3c89b0659d1a6292062c99e3e0866`.
Candidate: `native/mainboard_revD.kicad_pcb`, SHA256 `8312b1d5ec56f0ab4c396cba2b78449e191f06225bf9aa64ea6522fd1c3c68bb`.

## Useful change
Connect existing 100k pulldowns U203.5 (1A2, F) → R222.1 (B) on CAM_RESET_UART_TX and U203.6 (2A1, F) → R223.1 (B) on CAM_PWDN_UART_RX. Both direction controls U203.2/3 remain in the physical AON core; resistor ground terminals already core GND. No values, nets, sources, footprints, pad contracts or opposite sensor ports changed. J104 and MCU branches remain separately disconnected.

18 new 0.15 mm F/B tracks and two through vias Ø0.45/drill0.2 mm:
- RESET: 11 tracks, via (11.475,54.75), planar branch length **21.157251457 mm**.
- PWDN: 7 tracks, via (11.85,57.6), planar branch length **15.878596428 mm**.
No segments below 0.1 mm. These are CAD branch lengths, not control/UART timing, load or power qualification.

Fresh all-severity/all-track/parity DRC **0/71/0 → 0/69/0**, ERC zero errors/one inherited warning. Exactly these two selected pairs merge; every other physical partition unchanged. All old copper, all 103 footprint/pad contracts and sources unchanged. Outline 14 × 99.8 mm with full RF retained. GND/AON/SENS cores remain 94/41/12.

## Mechanical repair, not adoption of control1041
Electrically reviewed control1041 (`30f015...`) crossed non-target C206's full retained projection and J104 service courtyard. It remains frozen and mechanically gated. This alternative branches from accepted2a540 and replaces all 21 control1041 additions with these 20 additions. `alternative_delta.json` lists exact replacement UUIDs and verifies identical final all-net physical partitions and common-old reference preservation relative to1041.

Both planner and finite shortcut validation prohibit whole finite-width outer tracks from every NON-target native courtyard and every handed-off full installation rectangle. Through vias avoid all native courtyards and ALL full installation rectangles. U203 and the correct destination resistor are the only intended same-face track-body access exceptions. C206 and J104 are NOT exceptions. `installation_obstacles.json` is an exact copy of the mechanical handoff; dependency hash recorded.

The complete J104 service rectangle is additionally inflated by **0.2 mm**, beyond actual track/via copper width. Thus the exploratory requirement is at least0.2 mm nominal separation for all affected tracks and via discs, not centreline-only. Independent exact8312 mechanical screen reports true J104 minimum **0.205 mm at RESET via**, closest track **0.2095892262 mm**; C206 full-budget minimum **0.609135031 mm** at PWDN via. All18tracks2vias have zero non-target full-budget/Fab/courtyard intersections. This is not a manufacturer-qualified tolerance or a selected probe/access envelope. No component/enclosure envelope was reduced. U203/target-pad underbody access still requires normal mask/seating/process approval.

## Electrical/reference evidence
All **1,150 retained-net reference projections**, including power/GND, have no additional uncovered area at the recorded numerical tolerance. New branch projections have nonzero areas within their own isolated actual native clearance holes; `new_reference_hole.json` records absolute F/B amounts. No new-path uncovered area lies outside its own hole. No ideal/expanded mask or relaxed numerical threshold is used. This is not a zero-uncovered or SI claim.

**Classifier correction:** same-net GND planes comprise two overlapping zones (x11.4..11.7 overlap). Extracting holes separately from each zone falsely treated a via crossing that seam as an outer-edge notch. The corrected classifier first unions ALL same-layer filled GND polygons and only then extracts actual holes. It records per-zone counts and union count so this can be independently reproduced. Old-reference checks already used that union. Earlier exploratory statements that moving right necessarily created a physical plane gap are withdrawn; no actual clearance waiver follows from the correction.

## Reproduction and negative tests
Run `run_checks.py`; then `verify.py`, `physical.py`, `raw_delta.py`, `replay_rollback.py`, `new_reference_hole.py`, `alternative_delta.py`, `negative.py` using `/usr/bin/python3` and `-O`. Reports must be byte-identical across modes. Materialization pins exact parent/model hashes and deterministic UUIDs and checks fill/reload byte stability. Replay reproduces all54 native files. Real inverse unified diff restores exact parent and 0/71/0 DRC. Five actual native cuts remove each whole branch, both branches, and each via alone; exact intended splits and predicted dangling UUIDs are checked. Render provides full F/B paths.

All test specimens and bounded exploratory trials (including ~12µm nominal-clearance trial and earlier per-zone hole diagnostics) remain local forensic artifacts, NOT validated release files. Manifest is an explicit allowlist; never upload the whole directory. Frozen parents never edited.

## Gates retained
JP201/202/301 OPEN; provider NULL; NOFAB / NO POWER. No sensor attached. Actual FPC, selected J104 probe/access, fabrication/process tolerance, dynamic OE, loaded VOH, leakage, sequencing, brownout, timing, RF/interface grounds, battery and thermal qualifications remain open. Prior tail clock-length delta, D0 broad-open overlap, prior0.05mm nominal tail margin and VIO own-antipad history are not waived. No real assembly or powered behavior is established by static DRC.
