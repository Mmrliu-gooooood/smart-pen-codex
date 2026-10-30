# Independent full IMU-control native review

**NOFAB / NOPOWER.106 airwires remain. The new actual EXTCLK reference loss and all DFM/current/timing gates remain OPEN.** Review verifies evidence, not consumer/manufacturing quality or electrical acceptance of the clock regression. No automatic reroute, thresholds loosened, source edits, uploads or power actions.

Author729-file manifest `9d1d11dbb75099679c047113bb1f266e3098a69eebe8c0173001188950a32bf9`; candidate `5ed5f0ad90f5f15830f50479e0ecc48fe0685ffaff1819ff642a300f9550a1e9`; parent69d93e9 pressure candidate. Final visibility model9283c89b… and earlier full-model416a3ac6…/left-fence7401617a… manifests/files and their dependencies verified intact at completion; full hashes in integrity_final.json. No initial hash snapshot claimed. Formal accepted9a03 not replaced.

## Fresh native and source results

KiCad9.0.2 bound full all-track/severity/parity CLI **0/106/0**, exit5; ERC0errors/1existing warning. Exact137new objects/13vias,3old AON tracks replaced,983total. NoFP/pad/net/value/source/rule changes. Actual final coordinates,widths,drills match selected model; source parser and fresh netlist preserved. Source10k1% R501/R502 unchanged. Independent finite physical UUID/all-six-layer graph (via drill subtraction and guarded raw zone normalization) confirms AON38/39,GND70/102,SENS12/12 and all previous physical pad components (including separate same-number EP islands). Pressure NIB/CONTACT/STRAP,IMU14supply pads,19complete nets/12DVP and existing clock remain connected.

SCL R501.2/U101.10(GPIO5)/U501.1; SDA R502.2/U101.11(GPIO6)/U501.4; IRQ U101.6(GPIO1)/U501.12(INT1). Both pullup AON terminals core-connected.13new vias independently checked annulus AND drill against every actual pad layer including same-net: no pad intersections. Reproduced finite clearance,edge,hole/native-rule audit passes nominal geometry, not assembly process.

## Independently confirmed reference regression — do not erase

Unchanged EXTCLK UUIDeba5b185-27fd-57f9-b1a5-37b4fa4d4ec8 has **additional projection loss0.0017414094705mm² on BOTH In2 and In4**, confirmed by a separate finite-polygon implementation normal/-O. Loss bbox(4.175,80.068649,.15,.107654)mm. Not subtracted away as an allowed own-hole and not rounded to zero. Earlier model-zero prediction is superseded by actual native fill, as author README explicitly states; downstream summaries must retain this boundary.

IRQ via(4.7,80.125) and old clock via(4.25,79.7) share native hole bbox(3.8745,79.3245,1.201,1.176). Added edge loss does not cross centerline, but that fact does not prove SI acceptance. Reproduced full centerline intervals,actual contours and predicate controls retained; reference_delta.png visually inspected. Independent core-GND-via graph gives nearest return via(2.65,83.3),distance3.779302mm; all13new via return distances are in return_distances.json. No inference of acceptable return inductance/impedance/crosstalk from distance alone. Explicit clock review/test/design decision still required before fabrication.

## AON morphology and merged holes

Independent guarded once-native normalization +.25mm erosion reproduces two AON components: main759.077146217768mm² and tiny.0058354382355mm² island bbox(2.7255,13.660878,.129029,.164881). Count1→2 does not prove the main backbone has split; conversely area/core38 does not certify current,transient or neck robustness. Author .1/.15/.2/.25screens reproduced and preserved,including existing small fragments.

MCU SDA via(2.575,13.1) is part of the actual In2 merged7-via hole bbox(.8845,9.1245,3.866,11.326). AON/SDA MEMS-side ground hole bbox(1.9995,81.6245,1.026,1.426). Neither is an isolated ideal own-circle allowance. Keep every actual hole's contained centers and topology in physical.json; do not flatten into a zero-gap claim. Earlier pressure BOOT/NIB merged-hole and U203/R222 underbody gates persist.

## Native counterfactuals / replay

Ten actual isolated native delete/refill/fullCLI cases reproduced normal/-O: nine functional cuts each107unconnected with exact expected dangling types; full backout0/113/0 **raw parent69d93e9 bytes exact**. Covers3long signals,GPIO1source,2pullup signal legs,2pullup AON legs,CS/SA0supply and rollback. Pressure/STRAP/clock preserved outside intended targets. Forward replay all native resources plus materialization map byte-identical; repeated fill stable. No normalized-only/property-format caveat. Normal/-O verification,physical,reference,neck,source and negatives agree.

## Metrics, firmware and manufacturing limits

Actual SCL81.004717mm/35segments/4vias, SDA83.185206mm/50segments/3vias, IRQ77.440401mm/30segments/4vias.53sub.1mmsegments remain (21/29/3), improved from model366 but not manufacturing elegance/current/SI qualification. No long In1/In4 signal track.

[ST DS11811 Rev9 CTRL3 Table34](https://www.st.com/resource/en/datasheet/lis2dw12.pdf) rechecked: interrupt defaults push-pull,active-high,not latched. PICKUP_INT_N spelling does not configure polarity; wake routing also requires registers. Actual application board_provider_absent.c still returnsNULL/0 (path/hash/text observed). Copper connectivity is not prewake,first-stroke capture,correct sampling or working firmware.10k pullups,long buses,capacitance/edge timings need real budget/configuration/test.

Recorded via courtyard intersections U501,U101,backC504,R501,J301,JP201,backJ105 remain open;13pad-clear vias do not waive tenting/paste/stencil/stress/registration. Existing8EP in-pad vias,23.8µm edge,narrow supply escapes,cell/charging,RF/thermal,unknown camera and actual optical tests unresolved. J103B52 versus virtualB70.5 harness mismatch remains. JP301 OPEN and unknown camera disconnected.106remaining airwires never dismissed.

## Reproduction and stageability

Only review_manifest allowlist is independent review delivery; local copied native/replay/negative resource trees excluded. Reconstruct author's native/,verify.py,physical_native.py,geometry_native.py,reference_delta.py,aon_neck_screen.py,source_contract.py,materialize.py,run_checks.py,native_negative.py,reproducibility.py,materialization.json plus exact dependency paths. Keep independent.py,all_components.py,source_check.py,reference_independent.py,return_distances.py,native_polygon.py. chains.py comes from earlier immutable imu_j107_clock_native_0405. Run all listed checks normal/-O; replay IMU_NATIVE_OUTPUT=<review>/replay/native; reproducibility.py. Reviews are bounded evidence, not permission to fabricate.
