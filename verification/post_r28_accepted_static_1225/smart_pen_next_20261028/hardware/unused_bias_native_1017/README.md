# Existing unused-input bias routing — static candidate, NOFAB / NO POWER

Parent: accepted `ground_pair_native_1007`, PCB `6d05642f7d15ba10c22266e551d72b8457d703bd7328dca79ff5c1c50812b4d9`.
Candidate: `native/mainboard_revD.kicad_pcb`, SHA256 `2a5400724239f11fe6f589c4f954441deea3c89b0659d1a6292062c99e3e0866`.

## Useful change
- Connect existing 10k pulldowns: U202.10 (2B2, F) to R206.1 (B); U203.7 (2A2, F) to R207.1 (F). Their ground pads were already in core GND. No resistor value, source or pin-role changes.
- Fourteen 0.15 mm tracks and one through via at (9.1,47.025), diameter/drill 0.45/0.2 mm. A route 12.286838865 mm, B route 7.179453690 mm planar. No segments below 0.1 mm.
- Fresh all-severity/all-track/parity DRC: **0 / 73 / 0 → 0 / 71 / 0**. ERC retains zero errors and one inherited warning.
- Exactly these two pairs merge; every other physical net partition stays unchanged. Core GND/AON/SENS remain 94/41/12 pads. All old copper, all 103 footprint/pad contracts, source files and outline remain unchanged. Outline 14 × 99.8 mm, RF extent −6.5 mm retained.

## Evidence and reproduction
Run `/usr/bin/python3 run_checks.py`, then `verify.py`, `physical.py`, `raw_delta.py`, `replay_rollback.py`, `negative.py`, `new_reference_hole.py`, `source_roles.py`, with normal and `-O` interpreters. Materialization pins both parent PCB and route-model SHA, deterministic UUIDs and fill/reload stability. `replay_rollback.py` reproduces all 54 native files byte-for-byte and applies the real inverse diff, restoring exact parent and 0/73/0 DRC. Negative cuts remove each input path, both paths, and only the via: expected 0/72/0, 0/72/0, 0/73/0 and 2 dangling /72/0 respectively. `render.py` produces F/B views.

All 1,136 retained-net reference projections were compared, including GND/power: no additional old-route uncovered area at the recorded numerical tolerance. New A path has zero nominal uncovered projection. New B path has **0.0657901081895 mm² F/In1 and 0.064927444105 mm² B/In4 uncovered**, entirely within its own isolated actual native via clearance hole (0.445512997293 mm²). Exact native-hole geometry, not an expanded ideal mask, classifies this. The new via does not merge its hole with neighboring OE copper. This is not a zero-uncovered or signal-integrity claim.

Finite copper, actual drill/pad/edge and native courtyard checks pass. External full installation-envelope review is separate and must identify this exact SHA; native courtyard pass is not physical assembly approval.

## Roles and unresolved gates
Frozen source ties U202.2DIR to GND (B→A when enabled), U203.2DIR to AON (A→B when enabled). Cached [TI SN74AXC4T245 datasheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), SCES877B revised April 2024, page 20 Table 7-1, supports this role interpretation; input circuits remain active. `source_roles.json` hashes the cached document; no claim it is latest. U202.7 and U203.10 remain source-marked NC and physically copper-free. This work does **not** qualify all unused-port states, floating-node behavior, powered thresholds, leakage, dynamic OE, loaded VOH, sequencing or brownout.

JP201/202/301 stay OPEN; firmware provider stays NULL. No sensor or FPC attached. Existing interface/RF GND gates remain. Prior clock-length increase 3.379458606 mm, 0.05 mm nominal open-envelope margin (not manufacturing margin), inherited D0 broad-open projection overlap and earlier VIO own-antipad delta remain disclosed, not waived. Actual FPC, installation, tenting, fabrication tolerance, electrical timing, power, battery and thermal approvals remain open. NOFAB / NO POWER; not a release.

## Artifact policy
Manifest is an explicit allowlist. Bounded planner, simplified/merged-hole trial, failed approach, exploratory boards/logs and negative native specimens are local forensic material only and excluded from publication. Never bundle the directory wholesale. No remote upload authorization is implied. Frozen parents untouched.
