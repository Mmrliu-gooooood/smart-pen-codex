# 14 mm port/left-column refinement — conditional mechanical entry gate

2026-10-28. **NOFAB. No native PCB changed, no completed harness or selected diameter.** This separate supplement preserves the prior `width14_gate` freeze and uses the same79-footprint native source `f27cd35dcaf51fd33078b60a7029f6f63fba9c58f1d2791488e8a1721330080c`.

## Scope and important changed input

Global assembly transform is fixedX=sourceX−7; no optional RF left expansion is adopted. Mainboard B-face is at chosenY, front faceY+0.93. Power follows the same0.30 nominal backside gap, retaining0.10 after0.20 differential loss. Wall/assembly/radial residual budget is unchanged:19 OD requires represented radius≤7.9 for0.10 residual.

The previous quick port screen used the1.4×1.8 copper-pad envelope with2.0 height. The USB worker supplied a wider **hypothetical complete wire/solder/bend envelope1.8×2.2 per pad**, still2.0 high above the F face. This supplement uses that largerXY envelope: centre±0.9 inX and±1.1 in sourceY. It is not measured or qualified; do not describe it as actual wire dimensions. No height is quietly reduced to obtain a pass. Final strain relief, insulation, wire gauge, solder fillet, thermal process and bend radius remain required.

Component envelopes use **actual F.Fab/B.Fab plus pad bounds**, not the courtyard extruded as a body. Unknown passives retain1.3+0.15 solder; the explicitR112/R113 proposal retains1.0+0.15. The bounding prisms are conservative and may be tightened only after genuine part/body/solder qualification.

## Uniform inward moves tested

Thirteen source references are tested with identical rightwardΔX:

R221, C103, C203, R224, R233, R104, R218, R210, R228, C201, R236, R240, C205.

A previous short coordination message called these12; the actual extraction and every numerical report contain13. All are the identified left-edge envelope violators; no unrelated placement is changed in the calculation.

| Uniform ΔX | J109 centreX | Optimized B-faceY | Worst radial remainder at19 | Board gap remainder |0.10 screen|
|---|---:|---:|---:|---:|---|
|0.25|12.50|1.940|-0.042487|0.100|fail|
|0.25|12.25|2.118|0.043568|0.100|fail|
|0.25|12.00|2.187|0.076215|0.100|fail|
|0.30|12.50|1.940|-0.042487|0.100|fail|
|0.30|12.25|2.118|0.043568|0.100|fail|
|0.30|12.00|2.226|0.094415|0.100|fail|
|0.35|12.50|1.940|-0.042487|0.100|fail|
|0.35|12.25|2.118|0.043568|0.100|fail|
|0.35|12.00|2.265|0.112247|0.100|conditional pass|
|0.40|12.50|1.940|-0.042487|0.100|fail|
|0.40|12.25|2.118|0.043568|0.100|fail|
|0.40|12.00|2.288|0.123037|0.100|conditional pass|

The useful next-prelayout candidates are **ΔX+0.35 /J109X12.0 /B-faceY2.265** or **ΔX+0.40 /J109X12.0 /B-faceY2.288**. They leave only0.01225 or0.02304 radial surplus beyond the explicit0.10 screen, respectively. These tiny additional margins are not a manufacturing robustness claim. Keep the same2.0 wire height and full1.8 width when the next native revision is built.

No newly intersecting same-side conservative component envelopes were found relative to the unchanged source; this is not KiCad DRC, complete pad clearance, route feasibility, SI/EMC or final three-dimensional harness approval. Moving13 parts can require extensive copper rework. Do not preserve old traces blindly. RF and full assembly mapping also change withX−7: the priorX−6 antenna-location report cannot be inherited unchanged.

## Fixed-datum port-edge/height relationship

For the positive/right side and fixed globalX offset7, the radial envelope bound is:

`allowable absolute X edge = sqrt(7.9² − (B_face_Y + 0.93 + H)²)`

`allowable source right edge = 7 + allowable absolute X edge`

`allowable J109 centreX = allowable source right edge − 0.9`

H is the total assembly height above the F copper surface, including solder and wire. These equations only describe available geometric space. SmallerH rows do not qualify a lower harness.

| B-faceY | H above F | AbsoluteX outer edge limit | SourceX right edge limit | J109 centreX limit for1.8 width |
|---:|---:|---:|---:|---:|
|2.24|0.80|6.83001|13.83001|12.93001|
|2.24|1.00|6.70978|13.70978|12.80978|
|2.24|1.20|6.58127|13.58127|12.68127|
|2.24|1.50|6.37190|13.37190|12.47190|
|2.24|2.00|5.97337|12.97337|12.07337|
|2.24|2.50|5.50101|12.50101|11.60101|
|2.74|0.80|6.51376|13.51376|12.61376|
|2.74|1.00|6.37190|13.37190|12.47190|
|2.74|1.20|6.22038|13.22038|12.32038|
|2.74|1.50|5.97337|12.97337|12.07337|
|2.74|2.00|5.50101|12.50101|11.60101|
|2.74|2.50|4.93367|11.93367|11.03367|

AtB-faceY2.24/H2, centreX≤12.07337. At the formerY2.74/H2, centreX≤11.60101. This is why changing the true mounting datum/board position matters and why the old board-centre approximation cannot be used.

## Practical interface requirements still open

- Preserve three physical pads and their specified electrical order. A new pad-centre placement must keep the complete solder/wire envelope, not just copper within the barrel.
- The repeated padY positions19.2/21.6/24 imply separate2.2-long diagnostic envelopes; the bounding-span screen coversY18.1..25.1. It does not define a continuous approved cable path, bend loop or clamp.
- Wires following the board axis still need controlled routing and mechanical strain relief. A clip/rib cannot be added outside the envelope without rerunning the near-zero surplus; do not rely on the solder joints as the load path.
- Route toward the RF-safe corridor before the radiator region. The fixedX−7 transform moves its projected coordinates; update the RF/harness3D check using the new native board.
- J106/J107 power/mode harnesses and actual service access are not fully represented; their final shapes can overturn this conditional gate.
- All source/schematic/PCB parity, native DRC, actual power/ground contacts, board stack, unplaced circuits and complete tolerance chain remain electrical/whole-system gates.

Reproduce with `analyze.py`; validate `verify.py` normally and with`-O`. The check preserves the original10-file gate freeze, verifies unchanged native input,13refs, exact radial equations, the wider wire envelope and both positive/negative threshold cases. No prior evidence is overwritten.
