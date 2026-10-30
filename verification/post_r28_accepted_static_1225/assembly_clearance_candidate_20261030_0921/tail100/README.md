# Tail shortening / J202 placement candidate — NOFAB / NO POWER

Frozen `ground_recovery_native_0818` is unchanged. No RF keepout, antenna, footprint identities, nets, component envelopes or cell assumptions have been reduced. This isolated candidate has **14 × 99.8 mm nominal Edge.Cuts** (RF end −6.5 retained; tail95→93.3). J202 moves upstream1.7mm toB(7,88.8),180°. All other footprint poses remain fixed. Source code, hashes, actual native copy and native DRC are retained here.

## Direct clipping is rejected

Native J202 mounting copper pads end aty93.65; edge93.5 clips0.15mm, edge93.3 clips0.35mm. Native B.Fab body ends94.0. The retained full open installation envelope extends to95.0. Therefore a simple tail cut is not a valid remedy. See `native_limits.json` and reproducer.

Moving J202 and tail together1.7mm preserves original1.35mm mounting-pad-to-edge and1.0mm body-to-edge gaps, while the open-operation envelope terminates at the new edge. These are nominal geometric values, not solder/process/FFC qualification. The99.8mm nominal target has0.2mm total headroom; an actual fabrication length tolerance must be established before claiming every finished board≤100mm. No accepted courtyard exists on this custom footprint, and its absence must not be interpreted as no access requirement.

## Full retained mechanical budget

`screen.py` synchronizes all available103-ref ledger entries simultaneously against each frozen RevC, RevD external bench, ACCESS19, ACCESS20 CAD context, removes stale legacy component entities, and applies J202 translations0/1.5/1.7/2.0mm without shrinking its13.9×5.5×2.22mm retained open envelope. All translated variants have zero finite positive-volume intersections with modeled obstacles. At1.7mm, closest obstacle is J107.3 solder/wire budget,0.4mm nominal, in all four contexts; ACCESS compliant frame is0.52223079mm away. At1.5mm, J107.3 gap0.6mm; at2.0mm it is0.1mm, so unnecessary upstream movement erodes margin. This finite comparison is not a continuous optimum.

Coverage limitations are explicitly listed per result: missing JP201/JP202/C106/C107/J104 operation envelopes; U205/C209 provisional package-plus-assumed-solder budgets are included per parent README (not physical installation qualification), unknown actual FPC bend/insertion/tool envelope, wire assembly and manufacturing tolerances. Existing shell/harness consistency and battery qualification are not closed. No complete product compatibility claim.

## Actual native electrical rejection / next repair

`build_native.py` copies frozen source privately, changes only J202 pose and three outline segment endpoints, refills zones, saves. Actual KiCad CLI schematic-parity DRC gives **17 violations /79 unconnected /0 parity**, exit5. Baseline is0/76/0. Of17,14 are dangling terminal tracks after relocating pads, three are clearance errors:

- J202.2 vs SENS_D1 via(11.75,88.85):0.125mm against0.15mm rule.
- J202.11 vs SENS_D7 B trace x7.4:0.125mm against0.15mm rule.
- J202.6 vs SENS_D2 via(10.75,88.35):0.139mm against0.15mm rule.

**Candidate is not electrically accepted and is not a manufacturing board.** Local J202 fanout reroute and connectivity/reference-plane checks are required; hardware routing owner was sent exact candidate path/results. No intentional old copper routing edit was made to hide these defects.

## Reproduce

Use `/usr/bin/python3 native_limits.py`, `screen.py`, `build_native.py` from this directory (paths resolved relative to script). Then `kicad-cli pcb drc --format json --schematic-parity --exit-code-violations -o drc.json native_placement_ONLY_NOFAB/mainboard_revD.kicad_pcb`, using writable XDG config/cache directories. `screen.py` verifies original CAD hashes before reads. Parent source remains frozen and unchanged.
