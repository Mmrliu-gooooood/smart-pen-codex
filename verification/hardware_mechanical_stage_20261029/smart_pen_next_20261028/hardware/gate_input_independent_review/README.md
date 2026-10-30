# Independent gate-input block review — NOFAB

**Accept only input/ground connectivity and bounded source/geometry delta. Gate function, HF/PI and manufacturing remain incomplete.**

PCB **ae805cea5d51e864588bdf052b64e1bacce118a122b9f98ce21ddaa15345a691**, author manifest **6c6c93af899a132c19bcb04fa51918fdae25c73c7b09ec636fe911791d94953b** (87 files). Isolated native snapshot; author files untouched. Baseline dd55 and source authority are referenced by verified manifests instead of copying their reports/libraries again. `source_rules.json` records dependencies and source hashes.

## Fresh native and independent geometry
KiCad 9.0.2, same-basename `.kicad_pcb/.kicad_pro/.kicad_dru/.kicad_sch`:
```
kicad-cli pcb drc --format json --exit-code-violations --all-track-errors --schematic-parity --severity-all -o drc.json native_snapshot/mainboard_revD.kicad_pcb
kicad-cli sch export netlist --format kicadxml -o fresh.xml native_snapshot/mainboard_revD.kicad_sch
kicad-cli sch erc --format json --exit-code-violations --severity-all -o erc.json native_snapshot/mainboard_revD.kicad_sch
```
- **135 violations / 54 unconnected / parity 0**, DRC exit 5. dd55 was 135/58/0. Exact full violation **multiset**, including item UUID identities, unchanged: no new/resolved violation. Existing shorts/clearance/mask issues prohibit energizing or fabrication.
- Fresh export exit 0; ERC exit 5, zero errors and inherited VBUS boundary warning only.
- **102 entities / 356 pin endpoints**. Every source value, footprint, symbol path and actual pad net checked. No component/pad geometry moved or resized.
- Exactly three old control tracks removed, 17 tracks + 3 vias added. Every surviving old conductor geometry unchanged. New geometry/net/width/layer checked by UUID.
- Independent finite pad/track copper polygons, annular vias with drill holes removed, and actual filled-zone islands intersected on six layers. All old pad subsets remain connected. AON **3→1** includes U301.1/C301.1 and original core. GND **17→15** includes U301.2/C301.2 and core. Remaining GND components are not hidden.
- Exact actual filled-plane/via polygon test shows no intrusion into MEMS x3..5/y81..83; six-layer no-plane/no-via flags remain. JP301 retains OPEN declaration, distinct source nets and separated physical pads. This is not a power-on permission while other shorts remain.

## Local input and reroutes
New actual B-side AON escapes are **.50 mm**, C301 .582843 mm and U301 VIN .223607 mm, to .60/.30 mm through-vias. Via separation **1.25 mm**; conduction between them uses actual filled AON copper, not an invented direct trace. C301 ground .807107 mm/.30 width ends at existing shared core via (10,63.4); U301 ground .20 mm/.40 width ends at new via (11.3,67). Ground-via planar separation **3.827532 mm**.

These trace lengths exclude current spreading within overlapping pads, via barrels and plane return. Separation is not actual loop length or inductance. Shared cap ground and separated local returns retain a PI/noise/transient gate; width alone proves no current/thermal rating. [TI TPS22918 Rev C §11.1](https://www.ti.com/lit/ds/symlink/tps22918.pdf) calls for short/wide power paths and nearby low-ESR ceramic bypass. Connectivity alone does not establish compliance with the electrical purpose of those recommendations.

|Control net|Layer|Removed mm|Replacement mm|
|---|---|---:|---:|
|CAM_IO_EN|F.Cu|6.700000|7.611270|
|CAM_ISO_OE_N|F.Cu|3.000000|3.041421|
|USB_EN1|B.Cu|36.250000|36.457107|

Measured from actual native conductors, not only route declarations. These are low-speed enable/isolation/mode controls, **not DVP/XCLK/PCLK/USB data**. Source default/pull networks and old pad connectivity preserved; physical startup/switching remains untested.

## Native MPN and configuration binding
Source manifest **d9ee61999f3520b4ddd34ccc2bf32919809f872f04905611f2bfae4abba374b8** (`gate_supply_native_mpn_source`) verified. Every native source sheet matches; endpoint nets/values/footprints/UUIDs unchanged relative to dd55. **Ten native Manufacturer/MPN/ProcurementStatus fields** in fresh XML equal the frozen contract, correcting the earlier external-only-MPN export limitation for those ten refs. Conditional procurement status is retained. C302 remains its explicit inherited 10 V NRND candidate; it has not silently become an alternative. Unlisted wirelands/commissioning geometry have no invented purchased MPN.

Same-basename project SHA **2927268f27542ce291be8aaa6b6bf4bfe9bc90d02fa259f9335487d1edc5b08e**, custom-rule SHA **5f62979bab670d6fbd32966656d9a1418499c265a842e4d48baf9bb255e8e9b7**, netclass canonical SHA **e4f5dac073d8f63e7e1f5240cbda8c0a1e62a1d9bd3746e060e7b4b0b8285a53** match dd55. Explicit conditional six-layer .83 mm stack retained (.93 mechanical bound). Material defaults are unqualified, not an impedance guarantee. Manufacturing-mode preflight deliberately rejects absent manufacturer/process/material/quote confirmations.

## Verification scope and remaining gates
Run `/usr/bin/python3 [ -O ] audit.py`, `source_rules.py`, `config_negative.py`; normal/optimized results agree. `negative_tests.py` requires rejection of seven copper/source/OPEN corruptions in both modes, including deleted new VIN via and wrong C301 pad net. Five configuration-file corruptions (missing project/rules, changed netclass/centre dielectric, removed stackup) also rejected in both modes. Bad fixtures excluded from delivery manifest.

**ON/EN, CT, QOD and controlled-output wiring are not completed. JP301 stays OPEN.** Nominal CIN 10 µF/local COUT 1 µF does not prove a 10:1 effective ratio against unknown camera bulk; bias/inrush/reverse-current/IO backfeed and actual load remain unverified. TPS22918 is not an overcurrent protection guarantee. No inherited whole-pen mechanical certification: no bodies moved, but complete harness/head/assembly still needs review. Full DRC/routing, HF/PI, safety and ≤760 CNY pair cost remain open. No architecture expansion, procurement, publication or fabrication performed.
