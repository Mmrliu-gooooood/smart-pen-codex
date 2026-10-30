# Independent pressure seven-link native review

**NOFAB / NOPOWER.113 unresolved board links remain; pressure copper closure is not physical switch, wakeup, safety or manufacturing qualification.**

Author543-file manifest `8008036551b67603d8a84ed39b523fa3808aeab58c3b4ca0be53fc0638495755`; PCB `69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`; parentd6c913. Plan manifest ab0e1c38c3319afe962bed6a646323ca3949368b58c2d72dad022eb5829561d6. Mandatory separate underbody review manifest ca320f8c14b398bcaf709e6dcbfc15da057bdb5afd18ddb2f548d64c33ff4347 read/verified. All these manifests/files and declared dependencies intact at completion; no initial snapshot claimed. Frozen source unchanged, no upload/power/fabrication action.

## Actual native and physical graph

Fresh bound KiCad9.0.2 full all-track/severity/parity **0/113/0**, exit5; ERC0errors/1existing warning.821parent−4STRAP escape+32new=849copper objects. All817 other copper objects unchanged; full source/native noncopper,102FP/366physical pad positions/nets,mask rules unchanged. Independent S-expression and fresh netlist source comparison passed. R503 remains47k1%,RC0603FR-0747KL; U101 package7=GPIO2/RTC_GPIO2, STRAP package8=GPIO3, not mixed up.

Independent finite actual-six-layer graph uses physical pad UUIDs, ring minus drill, guarded native zone decoding/all-drill subtraction. AON36/39, GND70/102, SENS12/12; every old physical pad component retained, including separate same-number MCU EP pads. New core pads R503.1,C504.2,J103.2; all NIB U101.7/C504.1/R503.2/R504.1 and CONTACT J103.1/R504.2 joined; STRAP U101.8↔R103.1 preserved,78old STRAP objects retained. Reproduced19complete nets/12DVP chains,IMU14 supply pads and EXTCLK endpoints; no complete-board claim.

Five new vias actual annulus AND drill versus all pads on every layer including same-net: no intersections. Reproduced finite new/old clearance, hole spacing, outline/native rules no conflicts. Original pose/source domains retained. Normal/-O independent and reproduced checks identical. No voltage-domain reinterpretation or mask override.

## Six real cuts and rollback

Separate-process actual native delete/save/refill/fullCLI: STRAP escape2/114/0; longNIB2/114/0; C504ground1/114/0; CONTACT1/114/0; R503AONvia1/114/0; J103GNDvia1/114/0. Only expected dangling types; target source pads disconnect. Independent finite graph separately checks each cause. All32 removed and original4 restored yields0/120/0 and **raw parentd6c913 byte-exact**, no format repair. Forward replay all native files byte-equal. Normal/-O native negative results agree.

## Reference/long high-impedance caveat

NIB long signal uses In3, not a long In1/In4 plane slot. Main planes retain guarded.25mm-eroded connectivity; old signal projection losses absent. Independent exact_holes.py subtracts **only actual native endpoint hole contours** from new In3 finite projection: residual0. Intermediate strips have no uncovered area; terminal raw gaps≈.0654034/.0649507mm².

Important: MCU endpoint hole is **1.341×.951mm merged native hole containing an existing BOOT_N via plus new NIB via**. Far endpoint hole is.751×.751mm with only NIB via. These are not two isolated ideal circular antipads and residual0 is not SI/return-current approval or a blanket merged-hole waiver. Author frozen README References paragraph correctly says actual decoded endpoint holes, discloses other centers in JSON and expressly rejects blanket merged-hole waiver; it does not claim isolated own holes, so no correction to that frozen text is required. Downstream summaries must carry this merged BOOT/NIB-hole boundary and inspect the JSON bounds/contained centers rather than report only residual0. Hole geometry/contained centers preserved in reference_and_length.json. Clock planar length46.2625mm unchanged; NIB53.2674mm/contact2.5464mm.47µs open and≈.979µs closed nominal1nF RC omit cable/trace/input parasitics and are **not debounce**. Noise/ESD/threshold/real ramp tests remain.

## Mandatory underbody-via DFM evidence

Re-ran immutable independent underbody inspector in this review copy. Actual U203 Value SN74AXC4T245PWR, no separate specified MPN; TSSOP16_4.4x5/P0.65,16perimeter pads. [TI RevB official datasheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf) PW package is TSSOP, unlike BQB/QFN exposed-pad version. No designated PW central exposed thermal pad. That does not claim absence of internal leadframe or authorize underbody holes.

Via(5.4,55),.60/.30GND lies beneath molded U203 body. Nominal closest U203 pad gap.8374158mm; closest opposite-face R222.1 pad.2254005mm. All layer-pad screens clear but R222 B courtyard overlap≈.004035mm² remains. Native front/back mode FROM_RULES, effective tented both, HasSolderMask false; no local opening override. **Tenting is not filling**, actual Gerber mask/process/registration/pinhole/residue/solder behavior not qualified. Underbody review is linked, not converted into a manufacture waiver.

NIB via(1.85,9.5) also overlaps U101 courtyard≈.015775mm²; existing MCU8EP via-in-pad/23.8µm edge,short-escape current,IMU stress,clock dynamics and full assembly gates persist. Resolve/qualify package-underbody and opposite-face courtyard with fab/assembler before manufacturing; no generic0DRC exception.

## Physical pressure/product limits

R504 remains B54.25,far from MCU-local C504B9.75; connector J103 nativeB52 still conflicts with virtualB70.5. Harness interface not moved or resolved by copper.47k minimum-load model still requires actualAON≥3V and explicit tolerance/leakage conditions; SPVE50,000-cycle rating is not consumer pen lifetime. ESD,contact actuation,bounce,wake/debounce firmware/provider-null,temperature/endurance remain open. JP301 OPEN,unknown camera/battery/charger NOPOWER unchanged. No privacy/data transport behavior was altered by this copper-only revision.

## Reproduction and stageability

Review_manifest allowlist only; copied native/replay/negative source trees excluded. Reconstruct immutable author native/,verify.py,physical.py,materialize.py,run_checks.py,native_negative.py,reference_and_length.py,reproducibility.py,materialization.json plus declared dependencies at same relative paths. Preserve review's independent.py,source_check.py,all_components.py,exact_holes.py,native_polygon.py and underbody_inspect.py (only root-path adaptation from immutable package reviewer). Run checks normal/-O as files indicate; replay PRESSURE_NATIVE_OUTPUT=<review>/replay/native; reproducibility.py checks exact outputs. chains.py is copied from immutable imu_j107_clock_native_0405/chains.py. Review graphs and geometry do not substitute powered timing/EM/assembly validation.
