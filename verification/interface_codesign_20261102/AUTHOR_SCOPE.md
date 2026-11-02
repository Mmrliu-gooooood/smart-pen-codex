# Distributed J107 + short USB_EN2 — native review checkpoint

**WIP / NOFAB / NO POWER.** This is not a completed pen or a fabrication/assembly release. Following independent ECAD, plane and MCAD checks, the supervising design task accepted this exact native as the new **conditional static WIP baseline** on 2026-11-02. See `ACCEPTANCE.json`; this is not manufacturing, electrical safety or assembly qualification.

- Exact parent24: `dcaaafa93bde51e58a96d9443cb77031773fc42a16ad3db20210b53f0394b052`.
- Candidate23: `617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5`.
- KiCad 9.0.2: **0 violations, 23 unconnected, 0 schematic parity issues**, including fresh isolated XDG configuration replay.
- `parent/` contains 53 project files; `candidate/` contains 54. Machine-local `.kicad_prl` preferences are intentionally excluded. New file is the custom J107 footprint; existing `schematic/usb_entry.kicad_sch` changes only its footprint association.

## Actual design change

J107 is explicitly **three distributed custom plated wire lands, not a stock connector**. Its former arbitrary tail placement was not a hard user constraint. All three pad numbers, nets, unrotated 1.5×2 mm copper sizes, active shapes and +0.04 mm mask margins are retained. Pad1 is rectangular; pads2/3 are roundrect with 0.05 mm corner radius. Full 2 mm-high per-terminal packing budgets remain intact.

| Terminal | Net | New native center mm | Pad angle |
|---|---|---|---|
| J107.1 | USB_EN1 | (5.22,34.31) |270°|
| J107.2 | USB_EN2 | (7.20,25.38) |270°|
| J107.3 | GND | (6.40,31.66) |180°|

- USB_EN2 U101.27→J107.2 now closes end-to-end: approximately **22.644 mm**, **2 new through-vias**, no MCU pin remap. USB_EN1 was open in the parent and remains open; it is not presented as functional completion.
- ILLUM_STROBE retains its two existing endpoint through-vias and all terminal connectivity. Its original 22-segment In2 chain is replaced by four B.Cu segments, approximately **16.226 mm**, with no new strobe holes. This is a routing/return-reference change, not timing or SI qualification.
- GND land receives an explicit **0.30 mm B.Cu, 7.288 mm** dogleg to the existing grounded via at (1.5,33.725). Only the original J107.3 ground incident stub is removed; no old ground via or plane is removed. No assumed B-side ground pour or external harness ground is used to claim continuity.
- Total delta: **23 tracks removed, 18 tracks + 2 vias added**. All 3118 retained copper blocks are byte-identical. Other102 footprints and native rules/zone definitions remain unchanged.

## Exact narrow terminal ownership, not a body waiver

The full wire/solder packing prisms are not proven solid copper keepouts at the board surface. Only these owner/net/layer/width/position-bound joint necks are classified separately:

- EN2 north, 0.15 mm B: (7.2,25.38)→(7.2,24.33). Outside-pad owned ring X7.125..7.275 /Y24.48..24.63 = **0.0225 mm²**. Existing mask exposes0.006; nominally covers0.0165.
- GND west, 0.30 mm B: (6.4,31.66)→(5.33,31.66). Outside-pad ring X5.50..5.65 /Y31.51..31.81 = **0.045 mm²**. Existing mask exposes0.012; nominally covers0.033.

No whole-footprint exemption, foreign-net/via allowance, new mask opening, or reused old-position J107 waiver. EN1 has no authorized neck in this candidate. Actual solder/insulation/strain relief/tool approach and harness remain unqualified.

## Verification and remaining limits

- All92 net terminal partitions checked: the **only change** merges the prior USB_EN2 {J107.2}/{U101.27} components. GND/AON/VIO cores remain103/41/12 terminals.
- Exact inverse: remove20 added objects, restore23 original tracks and old J107 footprint/project dependencies, refill → exact parent24 SHA above.
- Author verification normal/-O results equal. Eight negative runs explicitly reject wrong J107 pose, wrong pad net, changed retained copper and missing new ground-feed copper.
- Reloading the actual new footprint library, flipping and placing it reproduces the three pad positions/angles/sizes/shapes/masks. Schematic parity is zero. Native silk labels comply with unchanged0.8 mm minimum height.
- Each GND reference plane loses0.857227 mm² to two new via apertures. AON plane loses0.576852 and gains6.171267 mm² from removal of the old strobe slot. All three saved planes remain one island. **This is not ampacity, impedance, voltage-drop or PDN qualification.**
- Author retained-projection audit reports no material clock/strap reference regression. Small matched numerical loss/gain values (largest2.19335e-8 mm²) are retained verbatim in `references.json`, not silently rounded away. New endpoint-via reference gaps remain explicit; no SI pass is claimed.
- Minimum new-hole edge gaps0.450446 /1.157200 mm exceed the unchanged0.25 mm rule. Independent nominal copper minimum is0.150267–0.150268 mm against the unchanged0.15 mm rule. Native clearance pass is nominal, not manufacturing-tolerance certification.
- Independent fixed-port tests preserve GND source→MCU1.979614 mm and source→U201/U202/U2032.532593 mm geometric lower bounds. AON source→MCU improves0.857178→1.149414 mm; AON source→U201/U202/U203 remains1.149414 mm. These finite-window erosion metrics are not universal minimum necks or ampacity. Independent36-terminal/18-capacitor tests find no tested connectivity/reference loss.
- Full104/whole known214-scene review is separately hash-bound. The closest reported new joint-budget/model gap is EN2→power C6 approximately0.1634 mm: nominal model spacing only. Existing unknown operations, historical cap/pack conflict and battery/optics/thermal/wire qualification remain unresolved.

## Replay

Use Linux KiCad9.0.2 Python bindings and CLI. Geometry helpers are included; no old978/7d22 trial or external author search directory is required.

```sh
export XDG_CONFIG_HOME=/tmp/pen617a-config
export XDG_CACHE_HOME=/tmp/pen617a-cache
export XDG_DATA_HOME=/tmp/pen617a-data
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
/usr/bin/python3 verify_candidate.py
/usr/bin/python3 -O verify_candidate.py
/usr/bin/python3 library_check.py
/usr/bin/python3 negative_checks.py
/usr/bin/python3 references.py
kicad-cli pcb drc --format json --schematic-parity \
  --output replay_drc.json candidate/mainboard_revD.kicad_pcb
```

In a fresh copy, `python3 inverse.py` (using `/usr/bin/python3`) creates `inverse/`, refuses to overwrite an existing inverse workspace, and must recover the exact parent hash. No local PCB library update or automatic schematic-to-PCB update is required for replay.

`preview/combined_native_preview.png` is an actual native SVG export rendered to PNG and visually inspected, not a generated concept image. Native files contain the actual design; preview caption remains explicitly unconnected/NOFAB.

## Excluded unsuccessful alternatives

Earlier978/7d22 long-USB routes remain HOLD and are not ancestors of this candidate. Their 11 USB vias and moved strobe inner-plane cuts caused reference/neck regressions; none is imported here. In this fresh24-derived design, a standalone shortest B strobe route initially blocked the source via pocket; joint routing instead reserves the checked upper-pocket escape. Graph-only path candidates were not accepted until finite checks and native DRC passed. Intermediate silk warnings were corrected without changing board rules. Only the selected final geometry is included.
