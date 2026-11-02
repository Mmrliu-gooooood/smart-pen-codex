> 历史限定：本合同与测试只绑定617a／23项快照，未在此声明适配当前f763。物理线束未采纳。

# Current-native binding of the candidate T–P–M return tree

2026-11-02. **READ-ONLY LOGICAL CANDIDATE / NOFAB / NO POWER. The physical harness is not adopted.** This derived checkpoint binds the existing hardened wirelist to the exact supplied mainboard `617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5` and power RevB `94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc`. Native release status is controlled by the matching electrical/mechanical reviews, not by this topology check.

## What is current and what remains only a proposal

The new J107 footprint relocates its three solder lands without changing pin roles:

- J107.1 USB_EN1: B side (5.22,34.31)mm,270°.
- J107.2 USB_EN2: B side (7.20,25.38)mm,270°.
- J107.3 GND: B side (6.40,31.66)mm,180°.

All three native pad sizes remain1.5×2.0mm and local mask margins0.04mm. This checker verifies those exact current coordinates, orientations, sizes, side and net roles. It also re-reads the unchanged main J106/J109 and power J1/J2/J3/J4/J5/J104/JP1 roles. Moving J107.3 does not create a separate ground domain: it remains native GND. The new0.30mm B-side ground feed does **not** establish wire, pad, trace or joint ampacity or fault-energy survival.

The candidate external return graph remains T–P–M, where T=USB tail common ground, P=power-board common ground, M=mainboard common ground:

1. T → power J2.2 is the complete intended USB input return.
2. Power J3.2 → main J106.3 is the complete intended mainboard return, with J106 retained as a **logical existing endpoint only**.
3. Candidate extra ground wires to main J109.3 and between power J5.3/main J107.3 remain omitted. These native pads are not deleted, disconnected or treated as zero-volume installation entities.
4. EN1/EN2 retain main J107.1/.2 → power J5.1/.2; D+/D− retain tail → main J109.1/.2. Main J106.1 VBUS is externally unwired in this candidate.

**The old physical J106 power-harness route is still unresolved/rejected by prior assembly work.** J107 relocation does not solve it, install the harness, or qualify the complete pen. A new power-entry site/complete positive-return pair still needs coordinated native and assembly design.

## Retained safety and geometry conditions

- Preserve all104 installation entities and all three full2mm-high J107 solder/wire budgets. Geometry/whole-scene binding belongs to the matching independent mechanical review; this logical checker does not replace it.
- Power J1 and power J104 are separate thermistor interfaces. Keep both independently defined temperature channels, and never confuse power J104 with main J104. The third pack lead is not assumed to be an NTC; no bare CELL− connection or protection bypass is permitted.
- Protected-pack dimensions, charging voltage tolerance, NTC configuration, current-time limits and protection thresholds remain unqualified. No battery ordering, powering or charge enable follows from this report. JP1 remains OPEN.
- All seven power service envelopes, including J5 solder/wire/tool volumes, remain unresolved. Full solder, insulation, bend, retention, assembly and tolerance closure is required; no zero-volume substitution.
- A tree eliminates the intended thin-wire parallel-return branch only. On a single open ground, data/control protection, USB shield, camera/FPC, conductive mount/chassis or test-instrument paths can become unintended returns. The graph is not a fault-safe isolation proof or a complete external-conductor inventory.
- Direct T–M USB D+/D− with return T–P–M may enlarge reference loops and common-mode impedance. USB signaling and charger-mode LOW/HIGH margins must be checked with actual ground drop and load transients. Charge-disable/input suspend are not a de-energized-system guarantee.

For the reduced DC model, V_M−V_T=I_USB·R_TP+I_MAIN·R_PM and V_M−V_P=I_MAIN·R_PM. These are symbolic relations, not measured load, selected wire resistance or allowable drop. A direct T–M reference branch is an alternative only if explicitly modeled and power/fault-qualified; it cannot be called “signal-only.” No ground resistor/ferrite/diode/fuse shortcut is selected.

## Verification and provenance

The original hardened eight-payload checkpoint is immutable. This directory is a **derived current-native binding**, not an overwritten old result; its `contract.json` is byte-identical to that prior logical contract. Only source binding, current J107 checks, portable input arguments and documentation were added. It includes no old native-board copy and no third-party/private source documents.

The executable enforces the full endpoint/role mapping, every signal/supply wire, both unwired lists and protected-pack/thermal definitions. It rejects16 endpoint/role mutations using the same live validator, plus5 topology negative cases. Both single-edge cuts and3 normalized KCL examples pass. Examples use arbitrary units, not amperes. Ordinary and optimized Python produce identical JSON. Exact input hashes are checked before and after reading; no PCB is saved.

This is not DRC, connected-copper partition review, full104 geometry replay, plane/reference/PDN analysis, SI, thermal/ampacity, hardware test or manufacturing acceptance. Those matching current-native reviews remain separate gates.

## Portable replay

Use an installed KiCad Python environment providing `pcbnew` (the checked environment uses `/usr/bin/python3`). Supply the actual native-file paths; no private workspace path is embedded:

```sh
/usr/bin/python3 check.py \
  --main /path/to/current/mainboard_revD.kicad_pcb \
  --power /path/to/power_integrated_study.kicad_pcb \
  --output /tmp/return-tree-normal.json
/usr/bin/python3 -O check.py \
  --main /path/to/current/mainboard_revD.kicad_pcb \
  --power /path/to/power_integrated_study.kicad_pcb \
  --output /tmp/return-tree-optimized.json
cmp /tmp/return-tree-normal.json /tmp/return-tree-optimized.json
```

A different native hash is rejected rather than silently inheriting this result. `source_binding.json` identifies the exact inputs and unchanged logical-contract provenance. The files can be included beside the current native design without duplicating either board.
