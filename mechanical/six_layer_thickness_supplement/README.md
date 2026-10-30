# Six-layer finished-thickness sensitivity — NOFAB

2026-10-28. Separate numerical supplement; prior CAD, tolerance reports and all34 manifest-listed files remain unchanged. No PCB stackup, outer diameter or manufacturing order is selected.

## Candidate evidence and its limit

The [official JLC calculator](https://jlcpcb.com/pcb-impedance-calculator) observation identifies **JLC06081H-2116(Standard/Finished thickness0.83±0.10mm)**. Source evidence and SHA256 are recorded in `source_evidence.json`; the engineering research package is `docs/research/stackup_qualification` in the electronics tree. The maximum candidate finished thickness is therefore **0.93 mm**, versus the prior0.80 assumption.

The observed copper+dielectric sum is approximately0.8264, but **the calculator label alone does not settle whether its finished-thickness measurement includes soldermask**. Do not infer that scope from the sum. Do not add the copper layers again to a finished-thickness value, and do not invent a mask thickness. Confirm the manufacturing/inspection datum and mask scope before final tolerance qualification.

## Correct assembly datum: increase on one side, not both

The existing geometric model defines the mainboard underside/B-side substrate face at Y, with substrate extending to Y+thickness. Backside component envelope extends to Y−height−solder; front components start at Y+thickness.

With that **model's B-face datum fixed**, increasing0.80→0.93:
- B-side substrate face and backside component lower faces remain fixed.
- F-side substrate face and front component envelopes move **+0.13 mm**.
- The mainboard/power-board spacing does not decrease automatically.
- Total two-sided modeled passive envelope grows by **0.13**, not0.26.

For1.3 mm assumed passive bodies plus0.15 solder on each side, the global modeled two-sided envelope is3.70 /3.73 /3.83 mm for0.80 /0.83 /0.93 substrate thickness. It does not imply front/back highest components occupy the sameXY location. The separate RF antenna has a1.4 maximum body plus0.15 assumed solder; its front envelope must also move with the F face. Its newly introduced components and the eventual complete board require a separate integrated revision check: this supplement's actual placement source remains the earlier sampled HREF3 extraction.

**This mathematical datum is not yet a finished mounting mechanism.** If a real support instead fixes the board centre plane, each face moves0.065 for the0.13 increase: nominal backside gap0.30 becomes0.235 and the previous0.10 residual becomes0.035 after the0.20 relative-placement allowance. If the real support fixes the front face, the entire0.13 grows toward the power board: nominal gap0.17, residual−0.03. These conditional examples must not be confused with the B-face-fixed calculation below.

## Assumptions carried over unchanged

Wall1.2 nominal, worst1.3; radial assembly/board-bow allowance0.2; differential inter-board spacing loss0.2; passives1.3 plus0.15 solder; power total populated thickness budget4.15; explicit residual target0.10; OD treated exact because its tolerance is unspecified. No extra allowances are silently deleted to retain a small diameter.

## Quantitative change

Worst radial clearance after the stated wall and radial allowances, in mm:

| Mainboard thickness / position |18 OD|18.5 OD|19 OD|Radial OD threshold for0.10 residual|
|---|---:|---:|---:|---:|
|0.80 / previous optimized coordinates|−0.147640|0.102360|0.352360|18.495280|
|0.83 / same coordinates|−0.167178|0.082822|0.332822|18.534357|
|0.83 / reoptimized coordinates|−0.155217|0.094783|0.344783|18.510434|
|0.93 / same coordinates|−0.234056|0.015944|0.265944|18.668112|
|0.93 / reoptimized coordinates|−0.180496|0.069504|0.319504|18.560993|

The fixed previous coordinates are main B-faceY2.820 / power bottomY−3.080. At0.93, reoptimization gives main B-faceY**2.740**, F-faceY**3.670**, power bottomY**−3.160** and topY**0.990**. The backside passive lower envelope isY1.290, retaining0.300 nominal gap; after0.200 differential loss, **0.100 remains**. Both boards were translated consistently, rather than reducing the required spacing.

**18.5 no longer meets the0.10 screen, even at nominal0.83 thickness after reoptimization.** The0.93 worstcase moves the approximate optimized mathematical threshold from18.4953 to18.5610 mm, an increase0.0657.19 retains0.3195 mm radial remainder under these particular assumptions; it is still only a candidate, not a selected robust production envelope. Missing parts, tolerances, supports, complete battery/NTC stack, wiring, mask scope and actual mounting datum remain unresolved. The numerical search interval0.001 is calculation resolution, not manufacturing accuracy.

## Axial separation fallback

With the mainboard at the original axial-layout Y1.0 and power in its separate segment centred atY±2.075, mainboard maximum radius grows6.58317→6.64831 mm as thickness rises0.80→0.93. The unchanged power budget radius7.30107 still governs. Thus the18 OD axial260 comparison retains **0.19893 mm worst radial remainder**, and the47 mm length penalty relative213 remains. This does not imply the four-layer power board has the same manufacturing thickness tolerance; its4.15 populated budget needs its own qualification.

## Reproduce and verify

Run `/usr/bin/python3 sweep.py`, then `/usr/bin/python3 verify.py` and `/usr/bin/python3 -O verify.py`.

Checks explicitly test the one-sided0.13 shift, unchanged B-face/back-part/power coordinates, non-double-counted two-sided height, retained0.10 spacing residual,18.5 negative-control result,19 conditional result and preservation of prior34 frozen source hashes. Passing these checks is arithmetic/model consistency, not fabrication or safety approval.
