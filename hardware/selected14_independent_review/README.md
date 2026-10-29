# Independent whole selected-board review — NOFAB

Bound to **016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e**, stepped 14 mm candidate, not an arithmetic combination of branch results. Author source untouched. Review native snapshot is read-only input; deliberately corrupt test fixtures are excluded from delivery.

## Fresh native results
- Selected-board ERC: **0 errors / 1 VBUS_5V cross-board boundary warning**, exit **5**.
- Complete selected-board DRC with all track errors, all severities and schematic parity: **0 geometry / 0 unconnected / 4 missing footprints**, exit **5**. Missing J103 pickup, J104 UART service, J105 ADC service, J202 semantic sensor interface remain real implementation gates.
- Fresh master ERC: 0; fresh fixture ERC: 0. Selected PCB rechecked against complete master: **0 geometry / 0 unconnected / 14 missing footprints**, exit 5. Cross-board functions were not deleted to make the selected-board result look clean.
- Exact units: selected source **83 component entities / 303 pin endpoints / 83 nets**, **79 placed footprints**. Master **93 entities / 383 endpoints**; original 380 endpoint identities preserved, added JF1 contributes three. Ownership allocation **95 physical-source entities = 83 mainboard + 9 tail + 3 fixture**. This is not the master's entity count: replacement cross-board interfaces and tail wire lands make the source views different.

## Independently recomputed copper and source
`audit.py` builds all-pad connectivity from finite copper polygons, actual filled-zone islands, annular vias with drill holes removed, and intersection on each of six layers. It does not join objects merely because they have the same net name. Every multi-pad net has one connected physical component; **78 actual GND pad shapes** belong to one component, including widened-plane connected copper and new J109 return. Native DRC independently checks geometric clearance and missing pads.

Every present footprint's value, library ID, root/sheet/symbol identity and every actual pad net matches a fresh exported XML. All selected source sheets match frozen v3. The source/ownership test checks retained full component attributes, old endpoint identities, moved switch UUIDs, four unresolved interfaces, and single ownership. J108 actual probe pads match the captured fixture contract including F/B sides, not just pin order. This does not qualify a physical double-sided fixture, contact order or live probing.

Source-preserved ports are listed in `source_audit.json`: J106 VBUS/3V3/GND; J107 EN1/EN2/GND; J108 EN/BOOT/GND; J109 USB_DP/USB_DM/GND. J202 is an **18-pin semantic 1.8 V interface**, not the purchased camera's verified FPC pinout or a completed camera supply design. JP201/JP202 DNP commissioning links remain source-declared; no permission to close them or power an unknown camera.

## USB, EN1, RF and returns
- USB_EN1: **83.545563 mm**, two through-vias, F/B outer routing, same GPIO/function. Actual pad connectivity checked.
- USB trace-only DP **10.245889 mm**, DM **11.878911 mm**, mismatch **1.633022 mm**. All four USB nets entirely F.Cu with actual filled In1 reference under their finite trace shapes. Excludes pads, resistor packages, harness and tail. Nonuniform differential spacing and side-envelope gaps mean this is **not** USB impedance/SI/functional qualification.
- RF remains F.Cu, no RF via, width **0.1814 mm**. Actual filled In1 covers referenced finite trace; y<0 terminal remains intentionally unreferenced. Six-layer radiator region checked against finite copper, permitting only antenna pads and its declared F.Cu terminal. AE101 pad 2 remains NC; matching parts remain unqualified tuning placeholders.
- Named stackup contract hash **49221b6c461fa8203b1777fdc7848bd346d5adf589ed53667895ee166b457809** matches source. Width is conditional on that unqualified fabricator stack, not proof of whole-path 50 ohms; launches, nearby ground, matching pads and terminal still require RF qualification.
- Independently compared every baseline AON/GND track/via: no old power/ground conductor removed; no old power/GND via moved; exactly eight declared capacitor terminal branches recentered. All other original power trunks unchanged. This establishes copper continuity/preservation, **not** HF loop inductance, temperature rise, source impedance, transient or battery safety.

## Current power handoff
Rev B harness manifest **7c789f8e99f0592979a7a3d0058f00aa4e93fd8f656a28e03f162be0a4bec48b** independently hash-verified. Target PCB **94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc** actual J5 pads checked: 1 /core/USB_EN1, 2 /core/USB_EN2, 3 GND. Normal/optimized harness suites each rerun eight cases; stale same-pin board, legacy four-pin board and CE injection rejected. This is a logical contract, not assembled wiring or charging authorization. Commissioning stays OPEN.

## Limits and reproduction
Fresh commands: `kicad-cli sch export netlist --format kicadxml`, `sch erc --exit-code-violations --severity-all`, `pcb drc --exit-code-violations --all-track-errors --schematic-parity --severity-all` against review snapshots; reports and exit codes retained. Run `/usr/bin/python3 [ -O ] audit.py`, `source_audit.py`, `provenance.py`, and `negative_tests.py`. Normal/-O core outputs are identical. Geometry tests use explicit exceptions rather than removable assertions.

No manufacturing, purchase, GitHub publication, RF/USB bench certification, cell qualification or consumer-product release. Four interfaces, camera power/optics/pinout, exact parts, mechanical tolerances, harness/ESD, power/charging/thermal tests, fabrication stack quote and ≤380 CNY/unit cost remain open.

## Negative tests and audit-development notes
Seven corrupt native-board cases each rejected with deliberate RuntimeError in normal and optimized Python (14 rejections): remove longest USB source track, remove longest EN1 track, remove RF source track, wrong RF width, In3 copper intrusion into radiator keepout, wrong strap pad net, and a fractured/serialized actual In1 reference-fill hole. Four source ownership corruptions and eight RevB harness cases also reproduced in both modes. The first exploratory EN1 mutation removed a short redundant pad-overlapped segment and correctly did not disconnect; the final negative fixture removes a necessary longest segment. This was a test-fixture selection issue, not a discovered EN1 defect. An exploratory source-check run omitted writable XDG configuration and printed config warnings; the recorded final source checks were rerun with writable XDG.

## Actual mechanical-input linkage (conditional only)
Copied `mechanical_binding/` is the mechanical author's frozen exact-input screen; manifest **2055b0f56a3f11a86b9646649e71e5ce8e65fb033ed6b5a8af4eca88acf314b4**, every file hash independently checked, evaluator/guard reproduced normal and optimized. It binds **this exact 016d PCB and all 79 extracted entities**, not the old 11ae/all+.15 board. C203 is the unique entity-envelope difference relative to that older snapshot.

Under the stated **19 mm OD**/wall/thickness/heights/assembly assumptions, both boards must move together: main B datum **2.264793176**, F **3.194793176**, power bottom **−3.635206824 mm**. Worst radial remainder **0.112368629 mm**, only **0.012368629 mm** beyond its 0.10 screening threshold; interboard remainder 0.10. The old B datum 2.288511 gives **0.098378650 mm and FAILS**. This is a reproduced conditional representative-envelope calculation, not an independent 3D shell/harness/interference certification. New FPC/other absent connectors are outside its scope; supplier heights, solder envelopes, holder tolerances, power-envelope assumptions, housing and assembly must be verified. The user's hoped-for 15–18 mm grip envelope is not established by a 19 mm OD screen.

## Review disposition
**Accept bounded selected-board source identity, finite-copper connectivity and native geometric feasibility, with explicit open gates. NOFAB.** No new electrical geometry defect found for this frozen selected source/PCB pair. No claim that the complete pen mainboard, camera subsystem, physical fixture/harness, final mechanics, product safety or cost are finished.
