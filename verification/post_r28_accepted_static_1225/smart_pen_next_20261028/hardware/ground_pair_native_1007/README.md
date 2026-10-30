# R219 + R229 ground group — pending independent review

**NO FAB / NO POWER. JP201/JP202/JP301 OPEN; provider NULL.**
Parent0949 PCB `8684d20fa449402ab1309b9af17d1cb64e0e6c4935532a36febaf362b0060f09`.
Candidate PCB `6d05642f7d15ba10c22266e551d72b8457d703bd7328dca79ff5c1c50812b4d9`.

## Actual progress
Five0.3mm GND tracks, **zero new/moved vias**, zero old-copper removals or edits:
- R219.2 B(8.325,41.5)→(8.025,41.6)→existing core R226.2(8.325,44),2.734905091mm.
- R229.2 F(5.325,40.9)→(5.325,41.5)→(3.825,41.7)→existing core U202.8(3.725,43.1375),3.554248658mm.

Actual all-track/all-severity/schematic-parity DRC **0/75/0→0/73/0**. ERC0errors/1 inherited global-label warning. Finite GND core92→94/103, AON41/41,SENS12/12 unchanged. Exactly the two named targets join the core; every non-GND physical component is EXACTLY unchanged.1244 prior copper objects retained,1249 total.

R219.1=CAM_VSYNC and R229.1=SENS_D5 are untouched; this ground-only work does not close their signal-side routing or claim functional VSYNC/D5 bias. Remaining73 comprises9 ground singleton gaps plus64 others. Remaining grounds: R104.2, J202.1/.4/.7/.10/.13/.17, J105.2, J107.3. RF/sensor-interface/ADC/charger-mode gates are not bypassed by this count.

## Strong preservation evidence
All103 footprints/pads, outline/drawings and every old copper raw block remain byte-identical. PCB is sole changed file in54-native-file tree; source/rules/BOM/provider unchanged. Nominal99.8mm outline and full RF area retained.

After actual native refill/reload, **all nine filled-zone/rule-area raw blocks are byte-identical** (`plane_identity.json`). Together with unchanged old copper/pads this preserves all previous net reference projections, including supply nets; no projection threshold was increased and no prior uncovered region is hidden. Separate normalized plane comparison also reports no additional retained signal loss. This does not erase inherited0949 VIO own-antipad change, D0/D1/D2 own-antipad coverage, historical CAM/reference limits, or clock +3.379458606mm length and actual timing gate.

All five new tracks pass finite foreign-copper/outline/rule checks. No new holes or via/pad/courtyard interactions. Full component envelopes and actual pad sides unchanged. Surface trace geometry is not an approval of mask, solder process, thermal/current capacity or installation.

## Real negative and reconstruction checks
Independent native cut specimens remove each target's entire added branch separately and both together. Each is refilled/reloaded and physically graphed: exactly selected target(s) return singleton; all other net partitions remain. Real DRC each single cut0/74/0; combined cut0/75/0. Anchors are pre-existing core objects, no hidden dependency between the two new leaves.

Fresh deterministic materialization matches all54 native files. Actual inverse unified patch restores all54 parent files byte-for-byte; real rollback0/75/0. Normal/-O verification, physical, raw delta, zone identity, negative and replay reports match. No correctness relies on removable assertions.

One initial in-process multi-board negative runner hit pcbnew/SWIG object-lifetime failure on a later reload. Diagnostic retained locally; it did not pass. Final runner uses a fresh Python subprocess for each cut (`cut_one.py`), with real fresh board load/fill/CLI and strict expected outputs. SWIG teardown warnings remain in individual logs; JSON is written explicitly. No frozen source was altered or denied operation bypassed.

## Reproduce and boundaries
Use isolated copy, `/usr/bin/python3` pcbnew9.0.2,kicad-cli,GNU diff/patch. Run materialize.py,run_checks.py,verify.py,physical.py,raw_delta.py,plane_identity.py,negative.py,replay_rollback.py,render.py; repeat checks with`-O`. `GROUND_NATIVE_OUTPUT` redirects materialization. Parent and final explicit geometry are hash-pinned. Search scripts are not required for reconstruction.

`manifest.json` is an explicit final-evidence allowlist; local exploratory search/failed harness diagnostics and broken native cut boards are excluded from release payload. No remote upload, purchase, fabrication, bridge or power action performed. All accepted old candidates remain unchanged.

Independent electrical review remains required. Actual camera/FPC, loadedGPIO VOH, dynamic five-OE edges/load, startup/brownout/real sequencing, clock timing/EMI, firmware behavior, battery/charging, full mechanics/process/finished outline tolerance and manufacturing authorization remain open. The inherited0.05mm nominal clock-to-full-J202 margin is not a manufacturing margin; unchanged D0 broad-open projection overlap remains separately disclosed.
