# Independent ECAD review — distributed J107 / short USB_EN2

Candidate `617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5`, exact accepted24 parent `dcaaafa93bde51e58a96d9443cb77031773fc42a16ad3db20210b53f0394b052`. Earlier978/7d22 HOLD candidates are not the baseline or replay dependencies.

## Disposition
**Independent native and conditional geometry checks PASS for a static WIP milestone**, subject to design acceptance and accompanying independent plane/MCAD reviews. This is not a manufacturing release, safe-power/boot/SI/PDN qualification or a proven assembled wire interface. NOFAB / NO POWER. EN1 remains open;23 native opens remain overall.

## Native circuit and complete-project proof
- Independently replayed actual CLI: **0 violations /23 opens /0 schematic parity errors**.
- Exactly23 parent tracks removed:22 degree-two ILLUM In2 chain segments and old J107.3 ground stub. Exactly20 additions:4 B ILLUM tracks,9 USB_EN2 tracks+2 through-vias,5 .30 mm B ground tracks. All retained copper bytes unchanged.
- ILLUM full existing-via-to-existing-via B replacement is16.2262311228 mm. USB_EN2 is22.6436265945 mm including source/terminal leads, only2 new vias. J107 GND dogleg is7.2881956420 mm to an existing ground via. These are geometric lengths, not timing/current ratings.
- All92 finite native pad partitions independently recomputed. ONLY USB_EN2 changes `{J107.2}` + `{U101.27}` → `{J107.2,U101.27}`. Ground103-pad, AON41-pad and VIO12-pad cores remain exact; ILLUM restored. Every added object reaches a native pad-connected component; both new vias have positive annular track contact on at least two layers.
- No control reassignment: source netlist USB_EN1 is U101.24 GPIO18→J107.1, USB_EN2 is U101.27 GPIO21→J107.2. EN1 unchanged/open.
- Only J107 native footprint changed; other102 footprint blocks exact. All nonrouting nonfootprint data, board zone definitions/rules/keepouts unchanged.
- Project excluding UI .prl increases **53→54 payload files**: new `GateStudy.pretty/J107_DistributedWireLands3_NOFAB.kicad_mod`; the sole changed nonboard file is `schematic/usb_entry.kicad_sch`, byte-identical except its one footprint association string. Of52 baseline nonboard dependencies,51 are byte-identical; the schematic association is the sole modified dependency. The added library makes53 candidate nonboard dependencies.
- Inverse deletes20 new objects, restores23 original tracks and original native J107, reverses the schematic association and removes the new custom library. Matched native refill returns exact dcaa24; **the entire non-UI project matches the parent**, not merely its PCB.

## Custom footprint is explicit, not an unchanged rigid connector
J107 remains same reference/value/path/footprint UUID with same pad UUIDs, numbers and nets. B-side origin now(6.4,31.66),0°. Actual pads:
-1 EN1 (5.22,34.31),270°;
-2 EN2 (7.2,25.38),270°;
-3 GND (6.4,31.66),180°.

Each retains native unrotated1.5×2 mm copper and +.04 mm mask expansion. Pad1 is **rectangular**; its inactive default roundrect-radius parameter is not a physical .375 mm radius. Pads2/3 retain their original .05 mm rounded corners. No shrink or solder-mask reinterpretation.

The actual new library was reloaded independently, attached to a temporary BOARD, mirrored to B and placed at the native origin. Pad positions/angles/shape/size/layers/attribute/mask margins match native exactly. Per-terminal labels, their positions, mirrored .8 mm text/.12 mm strokes and front/back courtyard polygons also match. Blank Datasheet/Description fields and annotation UUIDs are regenerated in the new footprint; this does not change logical component identity. No stock-connector MPN or one rigid three-pin connector body is implied.

Harness note: pcbnew flipping an unattached library FOOTPRINT can segfault; final library comparison attaches to a temporary in-memory BOARD first. Layer-set SWIG wrappers are compared by actual ordered layer IDs, not Python object identity. No native design change or waived check resulted from these harness corrections.

## TWO newly proven owned terminal geometries
Independent `terminal_geometry.py` screens every new B trace/via disc against all three declared, nonshrunken2mm-high J107 packing prisms using actual rotated native pad polygons and actual .04 mask offset. Only two out-of-pad intersections exist:
- **EN2 north .15 mm:** exact(7.2,24.33)↔(7.2,25.38), body[6.1,24.48,8.3,26.28]. Out-of-pad joint neck .0225 mm² = .006 nominal exposed + .0165 nominal mask-covered.
- **GND west .30 mm:** exact(6.4,31.66)↔(5.33,31.66), body[5.5,30.56,7.3,32.76]. Out-of-pad joint neck .045 mm² = .012 exposed + .033 mask-covered.

These are owning-pad/net/layer/width/axis/endpoint-bound conditional joint semantics, not translated old tail-J107 exceptions, blanket own-body access or fully masked neck claims. No EN1 escape is authorized. Wire insulation, solder volume/fillet, mask registration, bending/strain relief, tool approach and service access remain unqualified. Independent MCAD separately checks the full104 and whole known scene, including retained exterior copper against the relocated lands.

## Nominal copper/drill minima
Native25nm outside copper polygons,1nm collision binary bracket; circular hole distances analytic. All foreign-net copper on all common layers tested; distinct hole UUIDs tested regardless of net.
- Minimum added copper gap **.150267–.150268 mm**, requirement .15: USB track `5b6b6c64-06ae-4407-8b44-78bb104a35a4` to U101 unconnected pad28 `830663d0-b130-494d-9d9d-9c67a3d10f81`. Only approximately .267 µm nominal surplus; not fabrication/process margin qualification.
- Minimum new hole-edge gap **.4504462863061 mm**, requirement .25: USB via `6d44229a-c9c7-451e-a930-84035c87bf7e` to retained ILLUM via `1df5bc9a-84a4-4cc3-8b3e-687ddde25ebc`.
- Both new vias nominal .45/.2 mm, radial annulus .125 mm vs .1 minimum. Native rules unchanged; CLI is rule authority.

## Independent plane binding
`independent_interface_planes_20261102_0624/manifest.json`,151 payloads, SHA `d90097bb8d9c2140f698284a76e4f2fce82aa379c8e89e4289f5743d5f718cc5`.
All3895 retained projections have no positive loss in that reviewer's native50nm method; author Boolean differences ≤2.2e-8 mm² are separately identified as numerical-scale. Ground corridors unchanged from24. AON MCU fixed-window corridor improves approximately .857177→1.149414 mm; other AON corridors remain1.149414 mm.36 supply-cap terminal/reference checks pass; all three planes remain one island. New USB/ILLUM reference gaps and positive residuals near via-edge envelopes are quantified, not assumed zero; new ground route fully referenced. Six normal/-O result pairs and negative guards pass. These are geometric/copper facts, not impedance/current/boot proof.

## Replay
Run from a COPY; scripts generate inverse/negative fixture projects:
```
/usr/bin/python3 review.py
/usr/bin/python3 -O review.py candidate_native/mainboard_revD.kicad_pcb review_O.json
/usr/bin/python3 clearance.py
/usr/bin/python3 functional.py
/usr/bin/python3 terminal_geometry.py
/usr/bin/python3 negative.py
/usr/bin/python3 inverse.py
kicad-cli pcb drc --format json --severity-all -o drc.json candidate_native/mainboard_revD.kicad_pcb
```
Nine mutations × normal/-O explicitly reject: missing USB via, missing B strobe segment, wrong serialized net, GND-neck width, EN2-neck endpoint, native pad mask, native pad size, library mask and schematic association. Native/custom library/92-net, clearance and terminal geometry normal/-O outputs match. Parent/candidate complete projects and helper inputs are included; old978/7d22 projects are not required. External plane/MCAD packages must accompany their manifest bindings for full replay. No publication/adoption performed by this reviewer.

## Final MCAD and mandatory prose erratum bindings
Original frozen MCAD: `independent_interface_mechanics_20261102_0624/manifest.json`,15 payloads, SHA `3ac35318f5a0b6407a1fcf51737808a5c618defb088ff986ccbb26032419e94b`.
Mandatory companion erratum: `independent_interface_padshape_erratum_20261102_0635/manifest.json`,4 payloads, SHA `e0f6d0895fdebc49047b6b29e68416437e045dbac2e78aaf9d908be6cf6d1cdf`. The original MCAD prose incorrectly calls pad1's inactive .375 roundrect field a physical radius. Native pad1 RECT polygons remain4 vertices/3 mm² in parent and candidate; polygon-based geometry checks were correct. The separate erratum preserves the original freeze and corrects that prose; it MUST accompany it. EN2/GND active .05 radii and owned-ring classifications are unchanged.

MCAD checks full104 and all retained exterior copper against relocated J107 budgets. Whole known214-shape scene has only3 J107 prisms changed;211 unchanged. Each prism retains7.92 mm³/2 mm height. No new solid intersection; nominal closest gap EN2 to POWER_SCREEN_C6 .163395702816 mm. This is not tolerance-certified assembly fit. Historical locked-cap-vs-pack conflict44.244881 mm³, default known-only scene limits, and unknown operation/probe/harness/tool/power-service envelopes remain unresolved. No new prior-copper body-projection exemption is required by this candidate.
