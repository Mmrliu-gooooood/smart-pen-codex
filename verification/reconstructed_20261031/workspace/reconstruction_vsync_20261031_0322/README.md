# VSYNC two-closure topology — bounded static research candidate

Native: `final_candidate/mainboard_revD.kicad_pcb`
SHA256 **5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433**.
Parent accepted/private-roundtrip-backed-up d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b.

**This is not capture/SI/PDN/manufacturing approval. In particular, the long VSYNC bias branch remains an explicit layout/edge-loading gate, not hidden by the improved unconnected count.**

## Actual result
- KiCad9.0.2 all-track and schematic-parity DRC **0/43/0**, down from0/45/0.
- Only physical partition change is merging U101.22, U202.5 and R219.1 on CAM_VSYNC: two closures. All earlier8data, SCCB, PCLK/HREF and other physical pad partitions remain intact; cores GND94/AON41/VIO12.
- All103 footprint/pad/value/pose contracts and full104 installation envelopes remain unchanged; actual14×99.8mm/fullRF/stackup/rules/keepout flags preserved.
- One old SENS_D6 F track7536cae6-fbca-555e-a61d-9079d587d78c is replaced by four .15F tracks with identical U201.15 pad and existing-via endpoints: (3.725,36.8625)→(3.725,37.8)→(3.4,38.05)→(3.4,38.9)→(3.725,39.3). Length2.4375→2.712918690mm, +.275418690mm. Logical SENS_D6 connectivity and its still-isolated R230 bias leaf are unchanged.
- Every other old copper object is exact. No AON/GND, USB, CHIP_EN, BOOT or other existing source route replacement; no new In2 tracks. C104 direct2.55mm/.254F, current AON/GND stitches and previous d855 return trade remain exact.
- Added161tracks (68 exterior/93 inner),6vias. VSYNC157tracks/.15mm,6×Ø.45/.20 vias; SENS_D6 four replacement tracks. Native rules were not lowered.

## Joint construction and bounded alternatives
Actual source/bias/sink preflight used the current d855 board, not missing historical bytes. Corrected MCU source elbow(6.4,14.175) avoids current HREF; old elbow14.1 conflicts. Bias gateway(3.875,38.275) requires the declared SENS_D6 fanout replacement. The first direct B bias approach collides with existing SENS_D5 via and was replaced by an explicitly checked dogleg.

Both complete routing orders were tested. MCU-first saves .600610mm added conductor and66 track objects versus bias-first a040, with the same number of added trunk vias. The selected source-via shift(6.4,14.8)→(6.4,14.9) reduces real PCLK/HREF reference loss while retaining.2mm full-C104-envelope gap. An east-gateway shift8.925→8.95 failed actual NIB_CONTACT_N B copper; it was not adopted. An unused planned sinkvia6.15/41.5 was removed because both final incident tracks join on F.Cu; no dangling stub was left.

A later explicit **local PCLK/VSYNC shortening proposal** is preserved in `local_junction_prefilter/`: PCLK bias via6.625/41.875→6.875/41.975 with repaired B dogleg/F attachment, plus short VSYNC bias gateway6.675/41.4. It fails finite B.Cu clearance against PCLK and retained shared-GND stitch/lead b36a1e0c…; no native board was saved or adopted. This is a coordinate-specific joint topology rejection, not proof all shorter layouts are impossible. Larger local layer-transition/copper redesign remains possible but unverified; no further blind grid expansion was used.

## Length and branch-loading gate
Added VSYNC conductor total **60.326774984mm**. Centerline terminal geometry (vertical via delays excluded):

| Terminals | Planar mm | Layer changes |
|---|---:|---:|
| U101.22→U202.5 |40.781416496|5|
| U202.5→R219.1 |40.970498354|4|
| U101.22→R219.1 |38.901635118|3|

The40.9705mm number includes shared routing and is **not a pure stub**. Independent branch supplement0411 (manifest8d6cc143b526c19a7e0178ec6ea3699847982705fde170fbb95fffe88489742f; exact5files copied under review_dependencies/branch_supplement) verifies an actual **19.5453584876mm unshared R219 arm**, from B.Cu pad5.375/39.5 through privatevia3.875/38.275 to In3 junction11.25/28.9 at sharedvia2de832fa…. Junction removal after zero-edge contraction separates R219 from both functional terminals, so this is an actual articulation, not just a distance formula. One private B→In3 transition; vertical delay excluded. The100k resistor is a high-resistance load, not a matched termination or literal open circuit. The long branch needs actual edge/load/reflection assessment or later layout improvement; no arbitrary hard length limit is invented and no acceptance follows from VSYNC/frame frequency. PCLK33.807217mm/4 changes and HREF39.412240mm/4 changes remain unchanged; AXC4 control/clock versus AXC8 data delay/skew still requires actual supply/load/PVT timing budget.

84 VSYNC segments are <.05mm,108 <.1mm, minimum.025mm. Exact integer collinear-adjacency screen finds zero mergeable pairs. No cosmetic non-collinear smoothing or hidden reference alteration.

## Reference and PDN exceptions — not zero regression
Independent advisory `independent_vsync_advisory_20261031_0357`, manifest **ce2793ff59040c00a5251af6eae98cde28609c97b1d8a081db2cfe2b372fad1f**, supports full static review only.

2765 retained projections produce11 per-track loss reports; overlapping D3 objects must not be double-counted. Major causal findings:
- Sourcevia6.4/14.9 affects retained **PCLK In2→In1** .0007125011615mm² and **HREF In2→In1** .000661924169mm² (these tracks are In2, not F).
- It also triggers **nonlocal In2 filled-region removal**: D5 secondary-reference loss.1968285mm²; source-associated connected lost-plane region1.647670344245mm², bboxx6.1505..8.0495,y14.431347..18.322486. There are no new In2 signal tracks. Do not rename this a new trace-slot or assert a uniquely proven physical impedance/fill mechanism.
- Driver-sidevia8.575/41.45 causes PCLK B/In4 .000436073499 and CAM_ISO_OE_N B/In4 raw2.1310686e−5mm².
- Biasvia3.875/38.275 causes SENS_D5 F/In1 .0002087646735mm².
- Eastvia8.925/15.525 causes overlapping D3 In3→In4 and secondaryIn2 grazing. Union-before-subtraction≈2.07732665e−5mm² per plane; author post-subtraction union2.07766905e−5. Do not sum both old track reports as distinct physical area.
- D6 individual9.163e−9mm², union-first1.44525e−8 and post-union0 expose polygon operation-order precision, not calibrated electrical loss or a claimed zero. NONE counterfactual has D3 apparent recovered floor≈8.395e−9mm²; unrelated-via removals show the same floor and are not causal restoration.

New VSYNC/In3 foreign-only GND-hole union.000123707314mm²: SENS_D4via5.025/38 at3.223926e−6, SENS_VIOvia10.975/35.9625 at6.0242069e−5, AONvia10.975/30.2375 at6.0241319e−5mm². All missing projections lie in plane holes, not beyond plane boundaries; shared holes are still coupling conditions. New SENS_D6 replacement has no foreign-only reference-hole loss in this test.

Current AONIn2 remains one mainland with the same inherited outside-plane via11.9/83.9. No current AONvia center lies in removed plane copper. All tested C104 GND corridors and actual-via AON visibility paths remain unchanged apart from stated numerical-scale calculation variation. This is continuity evidence, **not unchanged PDN impedance**, and inherits the prior d855 return/secondary-plane penalties.

## Mechanics/process scope
Exact whole-path mechanics retains all bodies/poses. Only four explicitly pad-ended body exits: U101.22, U202.5, R219.1 and replacement U201.15. All six vias clear full bodies/Fab; native prohibited areas pass. Ordinary courtyard overlap is not a body waiver or manufacturing qualification: vias11.25/28.9 vs R210 F and6.4/14.9 vs C104 F each project.009664624028mm² onto courtyard but retain.2mm full-envelope gap. East sourcevia/R503 courtyard gap.025mm/full gap.275mm remains disclosed. Native tenting intent is not assumed hole filling/capping or supplier process approval.

## Reproducible static checks / remaining gates
312 normal/-O native/physical checks; whole finite copper/full-budget checks normal/-O; source roles; native wrapped-via regression; actual all-track/parity0/43/0; fresh normal/-O byte-identical refill; three terminal-cut negatives in both modes (MCU VSYNC, bias VSYNC, replaced SENS_D6) and six saved nativecut DRCs1/44/0; exact reversible raw native replay; reference/island characterization. Independent mechanics and advisory remain separate evidence; author checks do not self-accept the candidate.

R219 is B.Cu-mounted100k1% **A-port output bias**, not translator B-port input pull. U202.5(1A2) enabled DIRlow is B sensor-domain→A AON-domain; MCU GPIO16/XTAL32K_N must be configured as the intended input, excluding incompatible RTC/crystal/UART/analog ownership. Loaded thresholds, dynamic OE, actual power sequence, translator cross-device skew, sensor identity/edge/polarity/setup/hold, branch loading, actual camera configuration and measured waveforms remain open. Physical net closure is not capture functionality.

**NOFAB / NO POWER / providerNULL / JP201/202/301 OPEN.** Frozen allowlist excludes all rejected/planning/cut native boards and failed partial materializations; labeled negative reports/scripts remain reproducible. Private checkpoint follows independent scoped review before a long successor.
