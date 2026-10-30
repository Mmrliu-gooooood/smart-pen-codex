# Complete conditional pressure copper — native research candidate 04:33 UTC

**NOFAB / NOPOWER. Engineering candidate only, not a complete pen, manufacturing release or qualified pressure interface.** All 113 other unresolved links and existing hardware/assembly/optics/power gates remain. JP301 commissioning links stay OPEN; never energize unknown camera/battery hardware.

## Immutable inputs and exact allowed delta
Parent: `../imu_j107_clock_native_0405/native/mainboard_revD.kicad_pcb`, SHA256 `d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22`.
Approved readonly plan: `../../docs/electronics/pressure_joint_topology_0429`, manifest `ab0e1c38c3319afe962bed6a646323ca3949368b58c2d72dad022eb5829561d6`.
Candidate PCB: `native/mainboard_revD.kicad_pcb`, SHA256 **`69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`**.

Exactly 32 planned copper objects are added and 4 explicit old STRAP local escape objects removed, leaving 849 copper objects. All other old copper, including full DVP and SENS_EXTCLK geometry/length, is unchanged. No footprint, pad, source net, source schematic, project, rule or mask-setting changes. Entire native source/resource tree is compared byte-for-byte. Five new vias: three explicit .45/.20 signal transitions permitted by existing rules, two standard .60/.30 power/return transitions. No hidden minimum-rule reduction. All 102 footprints / 366 physical pads (including mechanical pads and distinct same-number EP pads) remain.

## Actual checks, not a completion claim
KiCad CLI 9.0.2. Full commands/return values and raw reports in `cli_results.json` and `checks/`.
- Fresh fill stable on repeated save/load; full **all-track DRC / unconnected / schematic parity = 0 / 113 / 0**, from parent 0 / 120 / 0. CLI exit5 remains expected due unresolved airwires.
- ERC **0 errors / 1 existing dangling-global-label warning**.
- Seven pressure missing links closed: AON1, GND2, CONTACT1, NIB_CONTACT_N3.
- Supply-core physical pads **AON 35→36 (R503.1), GND 68→70 (C504.2/J103.2), SENS12 unchanged**. Every old physical pad component remains connected; no source pad sacrificed.
- Full STRAP_GPIO3 graph **U101.8↔R103.1**, 78 old objects retained plus exact replacement. Full NIB graph **U101.7↔C504.1↔R503.2↔R504.1**; CONTACT **J103.1↔R504.2**.
- All new vias checked against every actual copper layer and all pads, **including same-net pad overlap**, plus finite clearance, hole spacing, outline and rule areas: zero errors. This does not waive courtyard/assembly gates below.
- Normal Python and `python -O` checks agree; runtime checks are not removable assertions.
- Six actual native cut/refill cases each disconnect the intended source endpoint and increase airwires to114; only expected dangling copper violations arise. Cases: STRAP escape, long NIB, C504 ground, CONTACT, R503 AON via, J103 GND via. Full copper rollback restores **0/120/0 and raw parent PCB bytes exactly**, without a source-format repair. Full replay native files match byte-for-byte. See `negative*.json` and `reproducibility.json`.

## Source and physical pressure contract retained
Actual selected R503 **YAGEO RC0603FR-0747KL, 47k ±1%**; R5041k and C5041n unchanged. Source netlist explicitly identifies **U101 package pin7 = GPIO2 / RTC_GPIO2**, not GPIO7; strap pin8 = GPIO3. Minimum contact-load calculation remains conditional on actual AON≥3V and other assumptions in source correction0318. No contact lifetime, actuation force, ESD, bounce, temperature or firmware wake qualification is inferred.

R503/C504 are MCU-local; R504 remains connector-local B54.25. J103 is actual native B52, **not** virtual mechanical B70.5. No port was moved to conceal that mechanical mismatch. The complete routing is conditional on resolving the physical harness/interface.

## References, parasitics and ground return
Long NIB routing uses **In3 only**; no new In1/In4 long signal tracks. Old signal ground/power-reference projection has no new loss. Ground main regions remain one component after guarded native-hole decoding and 0.25mm erosion. Actual local antipad area changes are recorded in `verification.json`.

Every intermediate long-In3 segment has complete In4 ground projection. Two terminal segments have actual uncovered areas 0.0654034 and 0.0649507 mm²; subtracting the **actual decoded native endpoint holes** leaves zero additional gap. Hole bounds and any other via centers inside those native holes are disclosed in `reference_and_length.json`; this is not an ideal-circle allowance or blanket merged-hole waiver. Clock planar copper length remains46.2625mm unchanged. No SI/EMI qualification is claimed.

Total NIB planar copper53.2674mm, CONTACT2.5464mm. Nominal open RC=47µs and closed R503||R504 RC≈0.979µs using only1nF; excludes trace/cable/MCU parasitics, thresholds and tolerances. This is **not switch debounce**. Long high-impedance contact routing and absent qualified ESD/noise strategy remain test/design gates.

## Explicit assembly / DFM gates
`physical.json` identifies new via courtyard intersections, none hidden as pad-clearance success:
- NIB via index7 `(1.85,9.5)`, .45/.20: U101 F.Courtyard0.015775mm²; package-edge/tenting/process review remains.
- J103 GND via index18 `(5.4,55)`, .60/.30: under U203 F.Courtyard and small R222 B.Courtyard intersection0.004035mm². Both PCB sides matter.

Actual U203 instance **Value** is **SN74AXC4T245PWR**; its separate MPN field is absent/empty (not retrospectively supplied). Its footprint is TSSOP-16_4.4x5mm_P0.65mm. Independent package reviewer confirmed TI **PW0016A molded TSSOP16 has no designated exposed thermal pad** (do not substitute BQB/QFN assumptions). Actual candidate via inherits board front/back tenting: FROM_RULES both sides, effective IsTented true / HasSolderMask false, no local opening override. Native copper ring-to-nearest R222.1 B pad nominal gap0.2254005mm, U203 nearest pad0.8374158mm. These nominal facts allow research review, **not fabrication approval**: actual Gerber mask output/stack and manufacturing process, tenting ability, registration, pinholes, via fill/plug requirement, solder migration/assembly yield and tolerances must be reviewed with manufacturer/assembler. No via-in-pad permission, mask opening, solder-fill claim or process capability was added. Authoritative independent package report: `../../docs/electronics/u203_underbody_via_review_0436`, manifest `ca320f8c14b398bcaf709e6dcbfc15da057bdb5afd18ddb2f548d64c33ff4347`. Its actual TI drawing p38 inspection distinguishes PW from exposed-pad packages.

All inherited MCU EP via-in-pad, narrow escape-current, IMU stress/assembly, clock timing, harness, radio, cell/charging and thermal gates remain unresolved. No purchase, fabrication, powering or remote publication was performed here.

## Reproduction
Use `/usr/bin/python3 materialize.py`, `run_checks.py`, `verify.py`, `physical.py`, `reference_and_length.py`, `native_negative.py`, then `reproducibility.py`, with existing output manifests treated as frozen evidence. For replay set `PRESSURE_NATIVE_OUTPUT` to a new native directory. Helpers/input hashes are enumerated in `dependencies.json`. `native_negative/` contains intentionally disconnected boards and is **not** a release folder. `replay/` is evidence, not a second design variant. Prefer separate-process cases (the scripts do this) to avoid KiCad SWIG lifetime issues.
