# Receive PCLK/HREF — independent PDN/reference advisory, NOT full acceptance

Pinned original diagnostic **a7713a113d76041201bf9cd3a9e76d6b32b8f026ad2cd383f5a37de70821749e**, then independently rebound to selected **d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b**. Baseline accepted SCCB **c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855**. Both candidate snapshots were copied before analysis; author files never edited. Final local delta is exactly six existing track/via objects: PCLK/HREF source vias y14.25→14.30 and four incident F/In2 endpoints, no copper object addition/removal between these snapshots.

## Disposition
No new disconnected power-core/island blocker was found. The selected local correction meaningfully removes the avoidable D5 dominant-ground graze without altering the larger routing concept. This supports proceeding to bounded full static review, **not acceptance of PDN, edge integrity, capture timing, assembly or power operation**. Real feed/return geometry penalties remain below. Neither an arbitrary zero-projection rule nor a universal corridor-width threshold is justified by these measurements.

## Actual powered nodes and feed continuity
Independent finite physical graph preserves AON41 (including J106.2 supply entry, C104.1 and U101.20), GND94 and SENS_VIO12. In2 AON has one current mainland; the only out-of-plane AON via remains inherited(11.9,83.9). Obsolete removed anchors are not used as supply criteria. Via-to-plane tests and actual copper connectivity together, rather than a stale point-to-point test, establish this limited conclusion.

Original C104 direct cap→U101 feed remains **2.55mm/.254F**, exact three track geometries; AON stitch(5.4,14.75) and C104 pose remain fixed. But new source In2 crossover clearances interrupt the formerly direct plane corridor from this stitch to current via(6.45,17): outside-plane areas at .15/.3/.5mm exploratory corridor widths are approximately .155687/.311373/.525687mm². Secondary-plane loss does not mean AON is cut off.

A constructive **fully filled .15/.3mm bent corridor** exists via actual AON node(5.175,18.9) to(6.45,17): 6.444244mm geometric centerline versus old straight2.482942mm. No copper edit is proposed by this test; the corridor is already within the plane. The old .5mm corridor to(5.175,18.9) already clips .010503842669mm². A restricted graph bending only at existing vias has no .5mm alternative; this is NOT a global bottleneck proof, a current-flow path, or a required PDN width. General plane spreading remains unmodeled. Retain actual feed-loop/PDN impedance and simultaneous-switching validation as electrical gates.

## C104 ground-return trade
Old cap-pad2(6.775,15.8)→GNDvia(6.775,14.8):1.0mm/.15F. Selected via(7.85,15.2),same.6/.3 diameter/drill:1.231107mm/.15F. To nearest selected existing U101 ground anchor(7.5,11.5), straight span3.716517mm; sum lead+span increases **.568923mm** versus baseline. This sum is descriptive, not inductance or loop-area proof.

Actual In1/In4 GND corridors to nearest(7.5,11.5) remain fully filled at all .15/.3/.5 widths. To farther(6,11.5), .15 clear but .3/.5 clip .020035322666/.074237887185mm²; to(4.5,11.5), all three clip .1085688431955/.2119107644505/.3299232279935mm². Baseline was clear to all three at these widths. Thus nearest return is continuous but return spreading changes; cannot call this improvement or unchanged decoupling. Author's selected-topology old-via restoration conflicts support a bounded routing constraint, not global impossibility or a waiver.

## Retained reference attribution
Own union-based comparison of **2509 retained projections** on d855 yields four losses:
- AON F→In1:1.889415e−6 and .0006174770325mm² near new PCLK source via(5.9375,14.30), total **.0006193664475mm²**. This is foreign signal-via impact on retained power-reference geometry, NOT an own-AON-via-only hole.
- D3 In3→secondary In2AON: **.0929360006185mm²**.
- D5 In3→secondary In2AON: **.19140339425mm²**.
No corresponding retained D3/D5 dominant In4GND loss remains after the bounded source-via shift. In3's dominant adjacent ground is In4; In2 is secondary AON, not mislabeled as GND. New In2 source signals use In1 ground as adjacent reference.

Five isolated fresh-project counterfactuals (NONE, PCLK source via, HREF source via, new In2 tracks, C104 ground via) each verify byte-identical prefill before deletion/refill. NONE recovers nothing. PCLK source deletion leaves zero reported AON residual; first patch recovered intersection is1.889098e−6 versus original1.889415e−6, a **3.17e−10mm² Boolean-order/precision discrepancy** retained explicitly, not inflated into electrical significance or silently rounded away. Removing only new In2 tracks restores all D3 loss and .19134315 of D5. Removing moved C104 GNDvia restores remaining D5 secondary **.00006024425mm²**. These deleted circuits are diagnostics, never candidates.

Original a771 had D5 retained dominant and secondary patches .000100738mm² each: PCLK and HREF source vias each causally contributed .000050369. Selected six-object shift eliminates those patches and reduces AON loss from .00064750852. It does NOT repair the much larger secondary In2 clearance slot; disclose rather than claim zero regression.

## New paths
Selected new foreign-only dominant-ground grazing unions (mm²): PCLK/B **.000003222054**, PCLK/In2 **.000003223926**, PCLK/In3 **.000008160926**, HREF/In2 **.000003221901**. Others reported zero foreign-only union; all uncovered projections lie in actual plane holes, not outside plane boundaries. Hole membership is not harmlessness: shared own/foreign via holes remain coupling conditions. Do not sum overlapping segment areas or require cosmetic whole-route expansion solely to force these polygon values to zero.

## Source/timing gates and actionable next steps
Source netlist is **SN74AXC4T245PWR U202**, not AXC4T774. Actual DIR2/3 are GND; output enables14/15 CAM_ISO_OE_N; A-side1 is AON3.3, B-side16 SENS_VIO1.8. Enabled B→A PCLK output U202.4(1A1) reaches U101.21 GPIO15/XTAL32K_P, HREF U202.6(2A1) reaches U101.23 GPIO17. MCU input ownership must exclude alternate crystal/UART/analog functions. [TI AXC4T245 datasheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), [Espressif PICO-1 pin/domain datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf).

PCLK/HREF use U202 while data use separate AXC8T245 U201: family membership and nominal equal supply do not establish matched propagation, cross-device skew, or setup/hold. Need actual sensor launch/sample edge, MCU camera routing/capture configuration, device min/max propagation at actual supplies/load/PVT, trace/via return transitions, driver edges, bias-stub loading, and measured/simulated waveform/timing budget. VSYNC remains unresolved; static four closures cannot establish capture functionality.

Preferred bounded next action is to retain the tested source-via correction, carry the explicit In2 slot/C104-return trade into full review, and avoid further geometry churn merely to erase tiny projection numbers. If later PDN/edge evidence requires improvement, search a local In2 crossover reroute that preserves or restores the short AON plane corridor, or a separately verified return attachment; re-evaluate finite/native/body geometry and all-net reference deltas. Do not move C104 or insert a ground stitch without full local clearance/reference checks. No tested additional stitch is recommended here.

NOFAB / NO POWER / providerNULL / JP201/202/301 OPEN. No author/frozen/public edits. This advisory does not replace full native/source/negative/replay/mechanical review of an eventual freeze.
