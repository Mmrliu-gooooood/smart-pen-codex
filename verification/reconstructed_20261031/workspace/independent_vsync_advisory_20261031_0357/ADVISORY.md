# VSYNC independent reference/PDN advisory — NOT full acceptance

Selected exact **5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433**, copied read-only from reconstruction_vsync_20261031_0322/refined_candidate_DIAGNOSTIC before analysis. Baseline accepted **d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b**. No conclusions are bound to moving intermediate a040. Author selected the alternate MCU-first route and source via(6.4,14.9); comparisons to rejected east-gateway movement are bounded trials, not global impossibility.

## Disposition
Proceed to full frozen static review with the following explicit exceptions. No disconnected live power-core/island or new C104 copper-return-change blocker was found. Several real foreign-reference effects remain on data, PCLK/HREF, SENS_D5 and OE; they are not own-antipad-only or zero regression. This advisory does not approve capture, timing, SI, PDN, power, assembly or manufacture.

## Exact baseline preservation and source
Own native comparison: one old SENS_D6 track UUID7536cae6-fbca-555e-a61d-9079d587d78c replaced by four F tracks; no other old copper object changed/removed. New VSYNC157tracks6vias, no new In2 tracks. All existing AON/GND copper and all footprint poses/values exact; no direct C104/AON return modification. This does not mean plane impedance unchanged.

Intended VSYNC U202.5(1A2)→U101.22 GPIO16/XTAL32K_N and B.Cu-mounted R219100k output bias. U202 is SN74AXC4T245PWR, DIRlow makes B sensor-domain→A AON-domain when enabled, OE remains CAM_ISO_OE_N. MCU GPIO16 input ownership must exclude crystal/UART/analog functions. [TI AXC4T245](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), [Espressif PICO-1 pin/domain datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf). No firmware or loaded-threshold test occurred; historical excluded vendor bytes are not newly recovered.

## Retained projection causality
Own **2765** retained projection checks reproduce11 per-track reports. Overlapping D3 objects must not be summed. Matched-project prefill bytes are exact for all seven independent refills (NONE and each of six new vias removed separately); deleted circuits are diagnostic, never candidate alternatives.

- East VSYNC via(8.925,15.525) causes D3 In3→In4GND and secondary In2AON grazing. Two overlapping UUID785fa…/a1cb… individually report2.077412e−5 and2.07722805e−5mm²; **union-before-subtraction ≈2.07732665e−5mm² per reference plane**, not twice this. Remove east via→remaining reported loss0. The tested further east movement conflicts with actual NIB copper, so cannot be presumed feasible.
- Source VSYNC via(6.4,14.9) causes retained PCLK F/In1 **.0007125011615mm²**, HREF F/In1 **.000661924169mm²**, and D5 In3/secondaryIn2 **.1968285mm²**. Removing only this via restores all three major patches. The D5 patch is remote from the via: the source-associated connected lost-In2 region spans x6.1505..8.0495,y14.431347..18.322486 and totals1.647670344245mm². With no new In2 traces, this is **via-triggered nonlocal filled-region removal**, not a new signal-trace slot. Zone minimum thickness is.15mm. Exact fill response is demonstrated; do not claim an unmeasured physical impedance or uniquely proven fill-algorithm mechanism.
- Driver-side VSYNC via(8.575,41.45) causes retained PCLK B/In4 **.000436073499mm²** and CAM_ISO_OE_N B/In4 **≈.0000213120595mm²**. Removing only this via eliminates both.
- Bias VSYNC via(3.875,38.275) causes SENS_D5 F/In1 **.0002087646735mm²**, fully restored by its removal.
- D6 In4 report **9.163e−9mm²** is at native polygon precision scale; union-first calculation1.44525e−8mm². Preserve these nonzero values and exact operation order, do not call them substantive calibrated electrical loss or silently zero them.

**Precision control matters:** NONE counterfactual, despite byte-identical prefill, yields ≈8.395e−9mm² apparent D3 recovered intersection due Boolean/refill polygon representation/order. Removing unrelated vias gives the same floor; it is not evidence that those remote vias causally restore D3. D3 union and original-track order differ slightly; OE raw report2.1310686e−5 versus union2.13120595e−5mm². No widened mask/acceptance threshold is used. Major attribution above is vastly larger and localized; tiny residuals remain explicit.

## New route references
VSYNC In3 foreign-only actual-ground-hole union **.000123707314mm²** comprises three separated grazes: SENS_D4 via(5.025,38)3.223926e−6; SENS_VIO via(10.975,35.9625)6.0242069e−5; AON via(10.975,30.2375)6.0241319e−5mm². Other new net/layer rows have no foreign-only hole union. All classified missing projection lies inside actual plane holes, not outside the filled-plane boundary. Shared own/foreign holes remain coupling conditions; own-net via membership does not waive them. New SENS_D6 leaf has no foreign-only reference-hole loss in this test.

## PDN and C104 continuity
Actual finite cores remain **AON41/GND94/SENS_VIO12**, including current supply-entry and powered domain pads; AONIn2 stays one mainland with the same inherited out-of-plane via(11.9,83.9). No AON via center lies in newly removed plane copper. An old removed anchor is never used as a live supply criterion.

C104 direct2.55mm/.254F feed, AONvia5.4/14.75 and GNDvia7.85/15.2 plus1.231107mm/.15F return are unchanged from accepted d855. All tested .15/.3/.5 GND corridors to three existing U101 anchors are exactly unchanged. Same actual-via AON visibility graph and bent corridor5.4/14.75→5.175/18.9→6.45/17 remain at.15/.3 widths. One already-clipped .5 AON straight-corridor calculation changes by1.7166e−8mm² only; other measured corridor areas unchanged. Retain the prior d855 return/secondary-slot penalties; no new decoupling improvement or PDN equivalence claim follows from unchanged paths.

## Length/loading/skew context
Own terminal graph, planar centerlines excluding vertical via delay:
- VSYNC MCU22→U202.5 **40.781416mm /5 layer changes**.
- U202.5→R219.1 **40.970498mm /4 changes**; MCU22→R219.1 **38.901635mm /3 changes**. These share routing and are **not pure stub lengths**. The bias branch topology/loading warrants explicit waveform analysis rather than labeling the40.97mm number a standalone stub.
- PCLK MCU→U202 remains33.807217mm/4 changes; HREF39.412240mm/4 changes. Data8 paths are unchanged, using separate AXC8T245 U201.

No length comparison establishes capture timing. Need sensor launch/sample polarity/setup/hold, MCU input-matrix configuration, actual translator minimum/maximum propagation at supplies/load/PVT, cross-device AXC4-vs-AXC8 skew, via-return transitions, branch capacitance and loaded edges. Low frame rate or nominal matched-looking length is not an edge/coupling waiver.

## Actionable next gate
Freeze only with these exact foreign/reference and precision disclosures; then full native/source/finite/negative/replay/mechanical review. Avoid mandatory whole-route cosmetic expansion merely to achieve numeric zero. If later edge/PDN evidence demands a reduction, prioritize a locally checked source-via/return geometry or small lateral insets at the two power-via grazes; none is preapproved or tested here. Any modification must re-run whole-net finite/reference/current-core checks and preserve actual bodies/keepouts. Ordinary courtyard-only passages are separately process-classified, not blanket bans or manufacturing waivers.

NOFAB / NO POWER / providerNULL / JP201/JP202/JP301 OPEN. No frozen author or remote content modified. Advisory only; full acceptance awaits immutable author package.
