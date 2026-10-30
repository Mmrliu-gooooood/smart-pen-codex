# Exact courtyard-clear via successor mechanical review — NOFAB / NO POWER

Exact native `smart_pen_next_20261028/hardware/tail_courtyard_native_0949/native/mainboard_revD.kicad_pcb`, SHA256 **8684d20fa449402ab1309b9af17d1cb64e0e6c4935532a36febaf362b0060f09**. Separate successor;0921/0928/0933 frozen reviews and source artifacts unchanged.

## Concrete result

All103 complete native footprint/pad contracts remain equal to the99.8mm placement candidate, including per-pad layers, numbers, nets, geometry, value, DNP and pose. Actual Edge.Cuts14×99.8mm, RF end−6.5 preserved. Full J20213.9×5.5×2.22mm budget remains unshrunk: four-context zero positive-volume collisions, minimum.4mm to J107.3. J108 mixed-side service tests and J103 named joined-interface checks reproduce prior narrowly accepted geometry. Electrical DRC/reference verdict belongs to electrical independent review.

## Via relocation improves explicit geometry, not a process waiver

|Via|Exact position / diameter|Minimum relevant complete-budget planar gap|
|---|---|---|
|GND|(.8,87.4),.6|J202 full open .10mm; R501 .41501748mm|
|VIO|(.8,85.6),.6|R501 .41501748mm; J202 open1.90mm|
|EXTCLK|(2.5,87.525),.45|J202 open .05mm; R501 .325mm; J107.3 .38788253mm|
|D3|(12.1,85.5),.45|J106.3 full solder/wire budget .375mm|

VIO left-edge copper gap.50mm, drill-edge gap.65mm. GND has the same edge gaps. Neither demands a shaved wire/body budget. The three changed GND/VIO/clock via discs are outside the full J202 open-envelope upstream projection. **D0 via(13.1,87.6),.45 from the preceding accepted geometry still overlaps that broad open projection by.025mm**; do not claim every via is outside the operating envelope. This is not actual plastic-body overlap or proof of protrusion.

J202 native B.Courtyard exists: rectangle x0..14,y88.1..92.5, polygon cache61.4161mm². B.Fab static body isx.05..13.95,y88.3..92.3; full open operating envelope isx.05..13.95,y87.8..93.3,depth2.22. These are distinct. Hardware's all-courtyard via checks are not replaced by this body/open-envelope screen.

## Complete changed outer-route projection check

`path_projection.py` compares exact final native to a14b30138 predecessor, constructs finite-width OCC capsule projections for all six added/changed F/B track segments, then tests every same-face retained component/terminal budget. Five segments project into J202's own destination/open budget; **none projects into any other modeled component or wire/solder budget**. One remaining segment has no same-face envelope overlap. Inner routes have no modeled exterior tool volume. These are conductor projections—not fabricated solder height, mask/tenting, connector seating or exposed-copper qualifications. Unknown process protrusions remain open, not assumed absent physically.

## Limits unchanged

98 refs have modeled static budget entities; all103 are accounted, with four declared DNP and J104 operation-budget gaps explicit. U205/C209 source-package bounds plus assumed mounting allowance remain conditional. J108 fixture accuracy/stroke/force, J104 service stage, J103 strain relief/process, actual FPC insertion/bend/tool, battery/material/retention,15–18mm target and two-penCNY760 budget remain open.99.8mm nominal leaves.2mm total length headroom; controlled manufacturing tolerance is required to guarantee all finished boards≤100mm. NOFAB / NO POWER; no purchase or physical operation.

## Reproduce

`/usr/bin/python3 native_contract.py --board PATH`

`/usr/bin/python3 interface_check.py --board PATH`

`/usr/bin/python3 screen.py`

`/usr/bin/python3 path_projection.py`

The exact native contract comparison gates reuse of J202's rigid translation and the static shapes. Unexpected footprint/pad/outline changes raise errors. Geometry results and native SHA are linked by verification.json; manifest binds all outputs. Source CAD hashes and frozen predecessor hashes are preserved.
