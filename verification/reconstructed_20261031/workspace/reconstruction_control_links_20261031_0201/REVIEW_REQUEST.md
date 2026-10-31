# NEW MCU SCCB pair — frozen review target, NOFAB / NO POWER

**Native:** `final_candidate/mainboard_revD.kicad_pcb`
SHA256 **c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855**.
Parent is checked/private-checkpointed NEW data-only f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71. This is not a recovery of lost historical51 hardware.

## Useful result and limits
Actual KiCad9.0.2 `--schematic-parity --all-track-errors`: **0 violations /49 unconnected /0 parity issues**. Two complete physical joins:
- CAM_SCL: U101.44(GPIO39/MTCK) joins existing U204.7(SCLB)/R240.1.
- CAM_SDA: U101.45(GPIO40/MTDO) joins existing U204.6(SDAB)/R241.1.

All baseline copper UUIDs/geometries retained EXACTLY; no removals, old reroutes, footprint moves, values/net/pad changes, power/return modifications or rule changes. All eight data paths remain intact. Every other physical partition is unchanged; GND94/AON41/SENS_VIO12 cores remain. Actual14×99.8 outline/fullRF/native stackup/keepout flags unchanged. Original C104 direct bypass and GND return remain exact. ProviderNULL, JP201/202/301OPEN, NOFAB/NO POWER unchanged.

Remaining PCLK/VSYNC/HREF MCU+bias six closures are NOT implemented. Joint source prefilter found old VSYNC/HREF reservations collide with the original restored C104 GND; north SCCB pair was selected to make coherent progress without adding a bypass penalty. No provisional receive stubs are added.

## Actual source applicability
U204 is TCA9517DGKR, bidirectional open-drain buffer: B-side3V3_AON, A-sideSENS_VIO1V8, EN=SCCB_EN_SAFE. R240/R241 remain10k1% INITIAL_100kHz. Actual source netlist/pins/values are checked in `source_roles.json`.
TI SCPS242D requires B-side external devices to pull below0.4V; actual loaded MCU VOL and pullup/RC compatibility remain unqualified. GPIO39/40 share MTCK/MTDO ownership; GPIO3/eFuse JTAG startup selection and actual open-drain firmware configuration remain gates, not solved by static continuity. No eFuse programming or physical power occurred. Unknown sensor, actual EN/power sequence, clock stretching, bus capacitance, rise/fall/falling-edge coupling and timing remain open; a nominal100kHz label does not waive edge analysis. Primary URLs/version and scope are in CONTRACT.md.

## Routing and practical geometry
148 new tracks (97 exterior/51 inner),5 new through vias; widths .15mm and via .45/.20mm. F/B/In3 only; NO new In2 signal crossover. Project FineSignal127 class does not lower this group's width.
Added conductor totals: SCL66.3009753mm (3newvias), SDA71.3784093mm (2newvias). Retained U204/pullup network totals7.3165718/18.3321423mm respectively are not falsely called pure branch-stub lengths. These conductor lengths are NOT complete electromagnetic delay or length-matched timing. There are99 added segments shorter than.1mm and67 shorter than.05mm (minimum.025); actual grid bends are disclosed. Two optional collinear merges were NOT adopted because finite native polygons differed by2.99e−9mm²; source remains the checked geometry, not a claimed exact simplification.

First whole-path prototype had two via-to-FULL-installation-budget gaps of.025mm, not merely courtyard gaps. Final bounded repair moves SCL gateway to(10.6,41.8) and destination to(11.425,68.625): both full-budget gaps are now **.200000mm**, against R231F and U301B. Incident local paths were adjusted; no whole old path moved. R112-adjacent source via retains.15mm nominal full-body gap, SDA/R231 .240026881mm. These are geometric prototype margins, NOT supplier assembly tolerance qualification.

Ordinary courtyard-only crossings are enumerated by exact mechanics, separate from full-body/Fab/tool/mating/operational exclusions. Native tenting intent does not mean supplier-filled/capped/tented-hole qualification. Only the two exact U101 pad-ended north escapes have intended terminal body/Fab overlap; no blanket target-net waiver. All new vias lie outside full bodies/Fab. Missing service/commissioning envelopes remain unqualified.

## Reference/PDN disclosure
2318 retained projections compared against actual f27. The ONLY retained loss is .016327425941mm² on existing CAM_SCL F→In1; matched-project counterfactual removal of its own new destination via recovers the whole patch. This is an own transition-antipad attribution, NOT a harmlessness or SI claim. No other retained-net reference loss is reported, including the existing eight-data group and power paths.

Two25µm lateral insets of long new runs remove six power-via-hole grazes without adding vias. The practical gateway move also removes the new SDA/SCL foreign-hole graze. One new foreign-only dominant-GND graze remains: SCL/In3 **.000003223985mm²** near the unchanged CAM_RESET_UART_TX via(11.475,54.75). It is explicitly NONZERO, not an invented acceptance threshold. New transition holes can contain own and other net vias; own-net membership is not a blanket own-only attribution. All classified new uncovered projection lies within actual plane holes, not outside the plane boundary; coupling/return impedance remains unqualified.

Current In2 AON remains one island with the same inherited out-of-plane via at(11.9,83.9); no obsolete removed endpoint is used as a continuity criterion. `plane_delta_final.json` reports all filled-plane loss/gain areas caused by five new via clearances. Same-island DC continuity and no direct PDN copper edit do not establish unchanged PDN impedance. In3 dominant adjacent reference is In4GND, secondary In2AON separately reported—not mislabeled as ground.

## Reproducible checks and handoff
- `final_drc.json`: actual full native DRC/parity0/49/0.
- `final_verification*.json`:305 explicit normal/-O gates, all retained copper/pads/poses/partitions, widths/cores/metrics.
- `final_native_contract.json`, `final_fill_reload.json`: outline/zone/rules/thickness unchanged; byte-exact refill/reload.
- `final_validation/negative*.json`: two MCU terminal cut negatives, normal/-O; original physical separation detected. Exact native text replay both directions.
- `final_validation/saved_cut_*_drc.json`: project-matched saved cuts each detect **1 dangling warning /50 unconnected /0 parity**, versus final0/49/0. Negative boards are diagnostics, not release circuits; their bytes are not silently bundled as accepted candidates.
- `final_reference.json`, `newpaths_final.json`, `causal_final.json`, `plane_islands_final.json`, `plane_delta_final.json`: full explicit reference/plane characterization.
- Independent final whole mechanics binds exact c698 separately. Full independent electrical acceptance is still required.

Copy only the manifest allowlist into a NEW review directory before rerunning scripts; they regenerate reports locally. Run verify_final.py normal/-O, native_contract_final.py, source_roles.py, fill_reload_final.py, reference_check.py, newpaths_final.py, plane_islands_final.py and causal_final.py. Run negatives_final.py with0 and1, each in its own process normal/-O; repeated in-process KiCad ownership issues were avoided. saved_cut.py reproduces intentionally failing native cuts, not a manufacturing alternate. No frozen author files should be edited.
