# Receive PCLK + HREF — NEW four-closure candidate

**FROZEN CANDIDATE FOR INDEPENDENT STATIC REVIEW, not fabrication/power/capture approval.**

Native: `final_candidate/mainboard_revD.kicad_pcb`
SHA256: `d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b`
Parent: accepted `c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855` (0/49/0, private backup roundtrip verified).

## Useful result and exact functional scope
- Actual KiCad9.0.2 all-track + schematic-parity DRC **0 violations /45 unconnected /0 parity**.
- PCLK merges U101.21, U202.4, R218.1; HREF merges U101.23, U202.6, R220.1. These are **four closures**, not the lost historical receive routing and not complete capture.
- **VSYNC remains three separate pads**. All unused new VSYNC fanout stubs were removed. No function/value/pinmap was deleted to reduce the count.
- All other physical pad partitions exact; cores GND94/AON41/SENS_VIO12. Existing eight data paths and SCCB remain intact.
- 191 new tracks (102 exterior/89 inner),12 vias,9 exact old ground-branch removals. Every other old copper object is exact. Actual14×99.8mm, stackup, rules, fullRF and zone/footprint prohibition flags unchanged.

## Necessary changes within this selected topology
R230 F→(11.1,34.25),90°; R219 B→(6.2,39.5),0°. Values, pad numbers/nets, full bodies/heights and remaining101 footprints unchanged. R230's SENS_D6 signal leaf and R219's VSYNC signal leaf remain isolated as declared; moved ground pads are restored to the full GND core. New shared R229/R219 ground stitch(6.8,40.725); R230 ground stitch(11.1,32.325),Ø.45/.2. No R231 relocation or sensor attachment.

C104 pose, original direct cap→U101 2.55mm/.254F supply link and AONvia(5.4,14.75) remain exact. GNDvia moves to(7.85,15.2),sameØ.6/.3; .15F lead1.231107mm. Lead plus selected nearest straight ground-anchor span increases **.568923mm**. This is a real geometric return trade, NOT a PDN improvement/equivalence claim. Exact selected-d855 original-ground restoration gives19 all-track native violations with HREF escape; original R219 restoration gives51 all-track violations with PCLK/ground topology. Earlier a771 default-report counts4/47 were preliminary, not the selected all-track counts. These finite comparisons reject blind restoration, not all possible redesigns.

The original six-link plan was bounded: six trunk orders, bias-first/full-net-first studies, extra-margin comparison and explicit local transitions. A native PCB_VIA may be a PCB_TRACK Python wrapper; the old isinstance anchor bug was corrected and nine actual final wrapped-via fixtures pass normal/-O. Corrected searches still encountered shared local topology conflicts; no mathematical global-impossibility claim. Failed trials remain outside the frozen candidate allowlist.

## Actual layer use, path geometry and roughness
Signals remain .15mm; signal viasØ.45/.20. No rule lowering. New In2 signal centerlines are ONLY in the source crossover x4..8.5,y13.5..19 (finite trace width extends beyond the search-centerline boundary); the exploratory U202 window was unused and is not an adopted plane cut. In2 is mixed AON, with adjacent In1 GND; In3 dominant adjacent GND is In4, secondary In2 is not ground.

| Geometric terminal path | Planar centerline mm | Layer changes |
|---|---:|---:|
| U101.21→U202.4 PCLK |33.807217|4|
| U202.4→R218.1 bias |7.158752|1|
| U101.23→U202.6 HREF |39.412240|4|
| U202.6→R220.1 bias |6.845952|1|

These include centerline-to-via in-plane connectors but exclude vertical-via electrical delay. Bias paths are not falsely labeled pure unterminated stubs. Added conductor totals PCLK39.597534mm/5vias, HREF42.983192mm/4vias, GND5.160754mm/3vias. 87 signal segments <.05mm and103 <.1mm, minimum.025mm; exact integer collinear-adjacency consolidation finds **zero** remaining pairs. No cosmetic reroute was used to conceal roughness or alter references. Timing is not matched or qualified.

## Explicit reference/PDN exceptions
Independent advisory `independent_receive_pair_advisory_20261031_0303` manifest `1d0e123f782d343a62fac865655a31a81dbede2ef9288198839b01d7a93f8071` supports full static review, not PDN/SI acceptance.
- 2509 retained projections: four losses. AON F/In1 total **.0006193664475mm²**, caused by the foreign PCLK source-via interaction; not an own-AON-antipad-only explanation.
- D3 In3/secondaryIn2 loss **.0929360006185mm²**; D5 **.19140339425mm²**, largely new In2 slots plus .00006024425 from moved C104 GNDvia. No retained D3/D5 dominantIn4 loss remains after sourcevias y14.25→14.30; six exact object changes eliminated that avoidable graze.
- Source In2 slots interrupt the formerly direct AON plane corridor5.4/14.75→6.45/17. A filled .15/.3mm bent geometric corridor exists through actual powered node5.175/18.9 (6.444244mm vs2.482942mm straight). This is continuity evidence, not simulated current flow, inductance or a width acceptance limit. One current AON island remains; inherited11.9/83.9 via outside plane unchanged.
- C104 nearest GND return corridor to7.5/11.5 remains filled at.15/.3/.5mm. Other farther-anchor corridors now clip holes: return spreading is changed, not unchanged decoupling.
- New foreign-only dominant-ground grazing unions: PCLK B3.222054e−6, In2 3.223926e−6, In3 8.160926e−6; HREF In2 3.221901e−6mm². All missing projections lie in holes, not outside plane boundaries. Shared own/foreign holes remain coupling conditions, not harmlessness proof.
- Independent causal Boolean recovery discrepancy3.17e−10mm² is disclosed; no threshold widening or fabricated global-zero claim.

## Mechanics/process and functional gates
Exact full104 finite mechanics and four saved assembly contexts retain two declared poses. New vias clear actual full bodies/Fab; minimum full-envelope via gap.2mm at HREF1.625/36.175 and PCLK8.1/41.975. Twenty ordinary courtyard intersections are individually enumerated by mechanics; source via court gaps improve.03→.08mm while full-body gaps improve.275→.325. C104 GNDvia full gap.337377mm but court gap.075. Ordinary courts are placement/process boundaries, not universal track bans; no underbody-via exception, filled/capped hole assumption or manufacturing margin claim. Native tenting intent is not supplier tenting/assembly qualification.

R218/R219/R220 are **B.Cu-mounted output bias resistors**,100k1%. U202 enabled DIRlow B→A output channels feed MCU GPIO15(PCLK)/GPIO17(HREF); GPIO16VSYNC unresolved. Actual GPIO/RTC/32k/analog ownership, LCD_CAM input mapping, loaded VOH, fast-edge coupling, AXC4 clock/control versus AXC8 data propagation/PVT/skew, sensor launch/sample polarity/setup/hold, real loading and bias stubs remain unqualified. Frame/bus rate alone is not an edge-integrity waiver.

## Reproducible validation / archive boundaries
312 explicit native/physical checks normal/-O; exact finite copper and full installation checks; source/native roles; actual all-track/parity DRC; byte-identical fresh normal/optimized refill; four terminal-cut negatives in both modes; eight saved fresh native cut DRCs1/46/0; reversible raw native replay both directions; actual via-wrapper negative fixture; reference and plane-island reports. Mechanical and independent PDN advisory are separate exact-bound evidence; full acceptance still belongs to independent reviewers.

`review_manifest.json` is the immutable author allowlist. It includes final native, exact baseline hardware dependencies, reproducible checks and labeled negative/comparison reports—not rejected trial boards, failed materializer partial outputs, stale copied native reports or UI `.kicad_prl`. Full local forensic trials remain separately labeled and are not release payload. Private backup follows joint review, before long successors.

**NOFAB / NO POWER / provider NULL / JP201,JP202,JP301 OPEN.** No unknown sensor/RF decisions, actual power sequence, dynamic OE, loaded levels, physical assembly or capture operation are approved by static DRC.
