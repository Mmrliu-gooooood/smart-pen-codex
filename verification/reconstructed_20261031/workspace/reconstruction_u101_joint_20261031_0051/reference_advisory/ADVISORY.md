# Causal reference advisory — new reconstruction, not acceptance

## Scope and useful conclusion
Pinned own copy: **86414a58caa9f8e8feb4b04a37e2bce38156accb33afe3b862b7b06c58742c38**, compared with exact restored59 **4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad**. This is NEW eight-data-link reconstruction, not recovered receive/VSYNC51 hardware. No full-design acceptance or new DRC claim is issued by this advisory.

The retained-loss list mixes three materially different cases: own transition antipads, real foreign-via effects on BOOT_N, and removal of secondary AON-plane coverage under In3 signals. Do not treat all as foreign-ground losses or silently call them zero. The clearest bounded improvement is the CAM_D2 B/In3 gateway near the old BOOT via. Do not reroute the entire bus solely to force every projection to zero.

## Actual layers and source identity
Saved stackup: F–In1 dielectric0.1164mm; In1–In2 .13mm; In2–In3 .2028mm; In3–In4 .13mm; In4–B .1164mm. In1/In4 actual zone net is GND; In2 actual zone net is3V3_AON. Thus In2 signals are closer to GND In1, while In3 signals are closer to GND In4 than secondary AON In2. Dk/loss/material and manufacturing remain explicitly UNQUALIFIED. Closer reference is a geometric inference, not exclusive-return/impedance proof.

Actual finite supply cores remain GND94/AON41/SENS_VIO12. This connectivity is necessary but not a PDN impedance or power-sequencing test. Source-role gates remain: AXC8 A ports are enabled B→A outputs, existing100k branches add output load/stubs, and typical internal288k pulldowns exist. MCU GPIO7–14 ownership, input-matrix/capture timing, actual edges/loads, AXC8 versus future AXC4 clock skew, loaded levels, dynamicOE and sensor/FPC behavior are unqualified. BOOT/reset/strapping behavior must not be inferred from DC continuity alone.

## Retained routes: matched-project causal tests
All ten diagnostic variants first refilled their copied original project and reproduced the pinned PCB bytes exactly. They then removed only the named objects; these are NOT proposed alternate circuits.

| Retained projection | Causal finding |
|---|---|
| C104 AON F/In1 .1396999661545mm² | Removing moved own AONvia(5.4,14.75) recovers the entire loss. Removing the other six vias in its merged source-bank hole recovers zero. This is an own supply-transition aperture at its new position, not measured foreign excess. Still a changed return/reference geometry, not proven harmless. |
| CAM_D2 F/In1 .1122997903245mm² | Entirely recovered by removing its own destination via(4.575,25.125). |
| CAM_D7 F/In1 .112116525276mm² | Entirely recovered by removing its own destination via(3.875,29.975). |
| BOOT_N dominant In1/In4 ≈.0010625mm² | Removing CAM_D2 gatewayvia(4.275,19.325) recovers .001062497970/.0010624626705mm². Removing neighboring D0via(4.2,20.675) alone recovers zero. Small exact Boolean residuals remain disclosed, not threshold-expanded away. |
| BOOT_N secondary In2 | Three patches .016453955020/.015717743800/.011352500091mm² are caused by new AON_I2C_SDA In2 crossover tracks. Their removal recovers .016453952690/.015717743800/.011352497973mm². Additional .0003615545885mm² patch is recovered by D2 gatewayvia removal. This is secondary power-plane coverage, not an additional GND plane. |
| NIB_CONTACT_N In3/In2 .095671532mm² | Removing new CAM_D1 In2 tracks recovers the entire secondary-AON coverage loss. No corresponding retained In4 GND loss was found in the pinned checkpoint. Coupling into a sensitive contact signal is still not qualified. |

BOOT gateway exact adjacent tracks: B(3.35,19.325)→(4.275,19.325), In3(4.275,19.325)→(4.425,19.475). A small via/adjacent-endpoint displacement is the appropriate bounded search, followed by actual refill, finite copper, full budgets and preserved partitions. Complete separation of merged holes is not itself a universal electrical requirement. Later author25/50/75µm trials are not this pinned specimen; their results were not substituted into this report.

## New routes: foreign-only grazings remain explicit
`newpaths.json` uses actual same-net filled unions and identifies seven net/layer unions with foreign-only GND-hole intersections: D1/In2 .000003224676, D1/In3 .000003223926, D2/B .000003224676, D3/B .000008159054, D4/B .000022566041, D5/In3 .000062907038, D6/In3 .000024275753mm². No added-path uncovered projection outside the classified closed holes was found with this calculation.

These are finite native geometric grazings, not numerical zeros or EM coupling measurements. `grazing_segments.json` gives42 segment-hole intersections and exact endpoints/UUIDs; many overlap, so do NOT add their individual areas. The largest union is D5 near old D0via(9,27.15). Source-bank and other own/foreign merged-transition holes are separately retained in `newpaths.json`; a hole containing an own-net via is not automatically an own-only loss.

Treat these as bounded disclosure and possible targeted local-jog opportunities, not a demand for42 cosmetic changes or a whole-bus detour. No sourced SI threshold is established by requiring arbitrary zero area. Any subsequent repair must not trade a small graze for worse skew, extra transitions, lost retained references or mechanical intrusion.

## C104 and actual power-plane continuity
Original C104 ground stitch(6.775,14.8),1mm/.15F lead, and three direct .254F supply tracks totaling2.55mm are retained geometrically. Both GND planes still provide fully filled .15/.3/.5mm straight diagnostic corridors from the original ground stitch to all three lower U101 ground anchors(4.5,11.5),(6,11.5),(7.5,11.5). This is not a measured current path or inductance.

Own AON stitch moves along the retained feed from(5.4,14.2) to(5.4,14.75): pin-to-plane planar feed .775→1.325mm; capacitor-to-plane1.775→1.225mm. Direct capacitor-to-pin length is unchanged. No decoupling improvement is inferred from either number.

Actual candidate In2 AON has ONE connected filled island, area859.301849mm² versus872.995134mm² baseline. All current AON vias except the inherited(11.9,83.9) exception belong to it. New R503-region stitch(6.45,17.0), current C104 stitch and existing downstream(5.175,18.9) feed via are on that island. C104→6.45,17.0 corridors through .5mm remain clear. C104→5.175,18.9 .15/.3mm corridors remain clear; .5mm diagnostic swath clips .010503842669mm². This demonstrates a local available planar path, not a current-capacity or impedance threshold. Direct lines toward upper-domain anchors cross holes and require detours; same-island connectivity does not assert straight unobstructed flow everywhere.

**Correction to preliminary message:** the old point(1.3,12.65) no longer shares the plane because its R503-associated via was deliberately removed. It is obsolete, not a powered current endpoint. The earlier point-to-point diagnostic did NOT establish a new power-plane island or disconnected live pad. `plane_islands.json` records the actual current inventory and this distinction.

## Boundaries
Author reports a later collinear consolidation a93102ae… with identical per-net/layer/width unions; this advisory remains pinned to86414 and does not certify that transfer or later gateway repairs. Frozen source and restored baseline were not edited. Every counterfactual is an own-directory test copy. No publication, power, fabrication, timing, SI, EMC, PDN, assembly or process approval. Whole-route skew, return-transition impedance, source-bank coupling, startup/reset ownership and all historic gates remain open.

## Exact final bounded amendment
An independently copied final specimen **f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71** was checked after the main causal study. Relative to pinned86414, one PICKUP_INT_N collinear degree-two segment was consolidated with exactly unchanged native track union, and the CAM_D2 gateway moved125µm upward to(4.275,19.2), with only its two incident endpoints changed. `final_binding.json` independently verifies the object changes and that no other net/layer/width track union changes.

Final BOOT dominant loss is **2.29745e−8mm² In1 /2.2976e−8mm² In4**, NOT zero. The corresponding secondary In2 patch increases from .0003615545885 to **.0014399687805mm²**. All other listed retained losses remain identical. This is a bounded dominant-GND improvement with an explicit secondary-power-plane trade, not a justification for ignoring all In2 effects. Final actual cores remain94/41/12 and In2 AON remains one island with the same inherited via-outside-plane exception.

`final_newpaths.json` independently confirms all seven foreign-only grazing union areas above are unchanged after this amendment. The broader source-bank, power-feed and timing qualifications remain open. This advisory is therefore applicable to the stated final local trade for review/disclosure, but remains **not full independent final acceptance**: complete native/negative/replay, source semantics and full mechanical acceptance belong to the separate final review. No further source edit is proposed solely to force arbitrary zero projection.
