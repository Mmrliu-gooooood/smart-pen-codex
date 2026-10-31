# NEW control / camera-off service group — bounded static research

**NOFAB / NO POWER / provider NULL / JP201, JP202, JP301 OPEN. Not operational camera, UART, SI, PDN, assembly or manufacturing qualification.**

Selected native: `final_candidate/mainboard_revD.kicad_pcb`, SHA256 `7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1`.
Parent accepted XCLK native: `6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08`; private checkpoint roundtrip verified before this NEW stage. No lost historical artifact recovery claim.

## Implemented result and important naming limitation

Fresh KiCad9.0.2 all-track/schematic-parity DRC **0/37/0**, from0/41. Exactly four physical joins, merging the three existing components of each of these two nets:

| Actual net | MCU | Existing input/bias core | New service terminal |
|---|---|---|---|
| CAM_RESET_UART_TX | U101.49 GPIO43/U0TXD | U203.5 1A2 + R222.1 | J104.1 |
| CAM_PWDN_UART_RX | U101.50 GPIO44/U0RXD | U203.6 2A1 + R223.1 | J104.2 |

**CAM_PWDN_UART_RX is a naming alias, not a validated PWDN function:** actual U203.6→.11 maps to **SENS_TRIG_IN**. RESET maps U203.5→.12 SENS_XSHUTDN_N. Provider/vendor polarity, trigger/reset/power-down roles and timing remain unresolved; the user's functional RESET/PWDN requirement is NOT established by this routing. Camera-side unknown connections are unchanged.

R222/R223 are actual **B.Cu-mounted 100k1% pulldowns on A-port input nets**, not translator B-port output loads. U203 DIRhigh and OElow select A→B, VCCA=AON3.3V, VCCB=SENS_VIO1.8V. All other pad partitions preserved, including eight MCU data links, SCCB, three receive links and XCLK. GND/AON/VIO cores remain94/41/12. All103 footprint/pad/value/pose contracts, full104 installation budgets, actual14×99.8mm outline/fullRF, native keepouts, rules and stackup remain unchanged.

## Exact geometry

476 new tracks +7 through vias; **zero old copper removals or edits**. New signal widths .15mm; vias Ø.45/.20mm. No new In1/In4 tracks, power tracks, pose or USB changes. This does **not** mean unchanged PDN: new In2 tracks and via clearances remove filled plane copper.

Joint source escapes use (6.35,5.4)/(5.55,5.4). Local J104 branches were joined before long MCU trunks. Both complete trunk orders individually consumed the same transition corridor; native-aware source component mapping identified the second entry site. Final staggered gateways (11.6,47) and (11.125,46.625) use an explicit In2 policy window x11..13.6/y46.3..58.6. Earlier x11.2 boundary excluded the second legal entry, even after Y expansion. `ordinary_layer_component_evidence.json`, boundary/window regressions disclose artificial-boundary effects; no finite-grid/global-impossibility claim. No blanket In2 permission.

| Net | Added conductor | In2 portion | MCU→U203 nominal centerline | Actual layer changes | True service arm | True bias arm |
|---|---:|---:|---:|---:|---:|---:|
| RESET/TX |62.633211mm|8.526650mm|66.925530mm|3|2.345722mm|6.264474mm|
| PWDN alias/RX |69.354528mm|10.478427mm|74.345167mm|5|2.024846mm|8.848699mm|

Strict graph includes all six terminal pairs per net and exact zero-edge-contracted private arms. Vertical barrel length/delay excluded. Inherited U203→bias paths21.157251/15.878596mm remain unchanged and are NOT mislabeled private stubs. Degree4 junctions include tiny actual centerline overhangs, not four functional loads. External service cable/probe adds unspecified loading.

One new PWDN F endpoint was extended from(10.475,56.9) to(10.462785,56.924530) through the old same-net centerline. Original6902 was already finite/native connected; this normalizes a rounded endpoint, not repair of an electrical DRC disconnect. `junction_exact_delta.json` proves only that new endpoint changed and **all filled contour vertices remain exact**. All other copper unchanged. Native strict graph now connected without a broad finite-contact shortcut.

299 new segments shorter than.05mm;387 shorter than.1mm; minimum.025mm. Exact collinearity screen finds one pair at the declared J104.1 terminal-exit boundary x8.6; retained deliberately to distinguish terminal-ended service escape from the subsequent exterior segment. No other exact collinear-adjacent pair; no aesthetic smoothing or global uniqueness claim.

## Reference / PDN: explicit nonzero trade

3,363 retained reference projections show **zero measured loss**. This is narrow preservation, not new-route SI acceptance. AON main island remains one, same20 current via memberships; inherited11.9,83.9 outside-plane via unchanged. AON raw loss1.8864506574885mm²/gain7.3662e−8; net island area−1.886450566711mm² (operation-order numerical difference disclosed). GND In1/In4 each raw loss3.0987258113445mm²/gain1.206e−9.

Independent actual-via .15/.3/.5mm corridor graph, C104 feed/ground corridors and prior XCLK U202→U203 constructive .3/.5mm detours19.030633/19.237740mm remain unchanged. This preserves inherited detours, not their PDN qualification or current capacity. Pre-existing power copper exact is not unchanged filled-plane material.

New dominant-reference foreign-only enclosed-hole unions: RESET B1.9338812e−5mm², RESET In2 3.222054e−6, alias PWDN B8.160926e−6, In3 3.222054e−6. Shared source holes also contain old IO_EN and both control vias: removing old IO_EN via alone restores RESET B .0014289556225mm²; all-foreign-via diagnostic restores .0014482820295mm². Do not call entire shared holes own-only. Counterfactual deletion is diagnosis, never adopted design.

Alias PWDN B .0672331491835 and In3 .0649894137275mm² outside enclosed-hole classification are **edge-connected own-via antipads** at(13.35,37.025), independently restored by removing that via only. Not a foreign-gap claim, still local return interruption. NONE Boolean floor7.0013e−8 remains explicit. In3 dominant reference is In4 GND; secondary In2 AON is not ground and its complete absence beneath this new In3 projection is disclosed, not hidden or an invented automatic rejection rule. All causal details in the bound independent advisory.

## Mechanical / service / source gates

Whole finite screen: no new nonterminal full-body/Fab or explicit keepout intrusion; all vias clear full bodies/Fab. Closest via/full envelope gap .15mm at(13.35,37.025) against C202, with ordinary court overlap .0263236263165mm². Via edge gap .425mm; minimum all-new finite copper edge gap .325mm. These are nominal, not uniform.2mm/manufacturer tolerances or tenting qualification.

J104 is a separate unqualified service/operation contract. Only two exact B pad-ended escapes enter its actual court: (10,53)→(8.6,53) and(10,54.8)→(11.9,55.5). No unrelated new track/via/re-entry. Actual polygon[9.005,51.805,10.995,57.795]; +.05 planning rectangle is not a measured probe/tool envelope. No access/assembly waiver.

GPIO43/44 default UART0 and have reset weak pullups/input enable; ROM/bootloader/application behavior can drive or bias these nets before application camera mux.100k does not prove startup-low. Camera-off service must cover reset/download/boot logs/crashes and avoid external adapter contention when GPIO44 becomes a camera-mode output. No5V/RS232 assumption or physical power/testing action. Espressif's499Ω U0TXD series recommendation is unresolved for UART/EMI claims; no unapproved resistor/value/eFuse change is inserted. TI AXC4 enabled input transition max10ns/V, loaded VIH/VIL/VOH/VOL, dynamic OE/power sequence, actual firmware, edge/pulse widths and provider levels remain unqualified.

Primary sources: [PICO1 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf), [Espressif UART/reset GPIO guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), [S3 TRM boot controls](https://documentation.espressif.com/esp32-s3_technical_reference_manual_en.pdf), [TI AXC4 RevB](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf). Actual source/native role checks in `source_roles.json`.

## Evidence and adoption boundary

311 native/physical/source-contract checks normal/-O; finite candidate checks and core94/41/12; project-matched refill/reload byte exact normal/-O; four terminal cuts each mode, native saved-cut checks, reversible native replay both directions. Actual wrapped PCB_TRACK/PCB_VIA regression tests9 via objects with all connected native layers. Exact source and full-envelope evidence are separately independently reviewed. See `RUN_CHECKS.md` and final manifest for exact allowlist.

Read-only advisory `../independent_control_service_advisory_20261031_0521`, manifest `ac111af161fa07cd7665c71f2321206209f869f5530afeff69005942ba6e871c` (60 files), is dependency-bound, not full acceptance. Mechanical exact752 package `../reconstruction_control_service_final_mechanics_20261031_0524` awaits author binding. Only final_candidate is offered for independent review; all other native trials/cuts are diagnostic and excluded from publication allowlist. Joint review and private roundtrip backup required before long successor work.
