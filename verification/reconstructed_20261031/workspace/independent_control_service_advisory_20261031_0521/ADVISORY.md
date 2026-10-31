# Control/service routing — bounded electrical/PDN advisory

Diagnostic, not full acceptance. Baseline 6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08; original diagnostic 6902e59c0bd6cd76053f228343ea6859c4b5bac00d08abfcbd5b15971882aee6. Read-only source, own native/project/rules copies and refilled counterfactuals. NOFAB / NO POWER / provider NULL / JP201, JP202, JP301 OPEN.

## Useful result

No new disconnection of a current power core, and no loss in 3,363 retained track/reference projections was reproduced. This is not zero new-route return disruption or unchanged PDN. The right-side control additions remove actual plane copper and introduce shared return holes; a long service/control route remains unqualified electrically. The source net alias PWDN does **not** establish the sensor function: U203.6 maps to .11 SENS_TRIG_IN.

## Actual source and operation gates

Own source/pad checks reproduce the actual SiP49 GPIO43/U0TXD and SiP50 GPIO44/U0RXD, CPU I/O domain supplied by AON. U203.5 1A2→.12 SENS_XSHUTDN_N and .6 2A1→.11 SENS_TRIG_IN; DIR pins high AON, VCCA3.3/AON, VCCB1.8/SENS_VIO, active-low OE CAM_ISO_OE_N. R222/R223 are existing100k1% B-side-mounted *A-input net* pulldowns, not 1.8V-output loads. J104.1/.2 join these same MCU nets; connector value explicitly camera-off-only. These checks establish wiring, not sensor reset polarity or trigger/power-down equivalence. [Actual SiP pin table](https://www.espressif.com/sites/default/files/documentation/esp32-s3-pico-1_datasheet_en.pdf)

GPIO43/44 default to UART0, with weak pullups/input enable at and after reset; ROM UART output is normally enabled. Firmware/bootloader/ROM ownership and transition to camera controls must be established: a100k pulldown does not guarantee low against an enabled pullup or driven UART. Camera disable must cover reset, download, boot logs, firmware crashes and service, not just normal application mux changes. No eFuse programming proposed. [ESP32-S3 datasheet, tables2-1/2-4 and §3.3](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)

Service must be valid3.3V logic/common reference, never5V/RS232; external adapter TX may drive MCU RX only in the explicitly owned camera-off service state. In camera mode GPIO44 may be an output: an attached adapter can contend. Verify output-disable/power-sequencing, powered/unpowered connection and actual cable/probe loading; board label alone is not an interlock. Espressif recommends499Ω series on U0TXD for harmonic suppression; absent here, explicitly unresolved for UART/EMI claims, not silently inserted. [Official UART guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html)

AXC4 A inputs at3–3.6V require VIH≥2V/VIL≤.8V and input transition rate≤10ns/V. Need actual loaded MCU/adapter VOH/VOL and edge margins, UART idle/baud and reset/trigger pulse widths, B-output levels vs actual sensor thresholds, and OE/power sequencing. Nominal slow command frequency does not constrain edge speed or avoid shared-hole coupling;100k is not a series terminator. No provider voltage/polarity/timing is known. [TI AXC4 datasheet §5.3 and operation](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf)

## PDN geometry and current nodes

All old non-zone UUID blocks exact: old copper including C104 direct/return/AON tracks, footprints, values and poses unchanged. 476tracks/7vias added, no removals in6902. This does NOT mean filled planes unchanged.

AON main island840.689329542806→838.802878976095mm² (net−1.886450566711); raw loss1.8864506574885/gain7.3662e−8 are independently reported and differ at polygon-operation precision. GND In1 and In4 each lose3.0987258113445mm² with1.206e−9 gain. One actual AON island remains with the same20 via centers; inherited via11.9,83.9 outside-plane unchanged. Finite current cores are GND94, AON41, SENS_VIO12, anchored to J106.3/J106.2/J202.23, not obsolete diagnostic anchors.

Actual-via corridor graph at widths.15/.3/.5mm is unchanged, including C104 feed; C104 GND nearest-anchor corridors unchanged. One *already obstructed* AON straight diagnostic5.4,14.75→7.4,4.8 differs by1.8094e−8mm², not a newly required feed path. Full crosssections49.8–52.2 remain exactly equal. Constructive bounded .25mm-grid U202/C203 supply anchor9.575,42.2375→U203/C205 anchor9.575,52.0375 paths retain19.030633mm(.3wide)/19.237740mm(.5wide). This preserves the earlier XCLK detour, not its qualification; these are geometric paths, not actual current trajectories, impedance/current capacity or globally minimal neck proofs.

Actual deletion/refill counterfactuals: removing only new In2 tracks gives AON839.2422002486516mm²; removing only all seven new vias gives839.9442861160355mm². Effects overlap; do not sum them as independent losses. Removing edge via13.35,37.025 does not change AON area (outside its right edge). All matched pre-refills byte-equal6902. No current supply island split or new loss in examined current-feed corridors demonstrated; supply droop/EMI/decoupling impedance remains unmeasured.

## Reference attribution

Actual stackup references: F→In1GND; B→In4GND; In2→In1GND(.13mm); In3→In4GND(.13mm) with secondary In2AON(.2028mm). Zero retained projection loss is narrowly true. PWDN new In3 projection3.0413335079525mm² is wholly outside secondary AON; dominant GND still applies. Do not mislabel AON as ground or impose an arbitrary all-adjacent-plane zero rule.

Own union-before-hole classification finds foreign-only dominant-hole unions: RESET B1.9338812e−5mm²; RESET In2 3.222054e−6; PWDN B8.160926e−6; PWDN In3 3.222054e−6. Others zero foreign-only enclosed-hole union. These are not the complete foreign contribution: source hole contains old IO_EN and both new control vias, and other own holes merge with the opposite control net. Removing old IO_ENvia6.875,5.775 alone restores RESET B .0014289556225mm². Removing all foreign-net vias restores RESET B .0014482820295mm², RESET In2/PWDN In3 each3.222054e−6, and PWDN B8.230939e−6 including NONE Boolean floor7.0013e−8. Broad foreign deletion is causal diagnostic only, not a legal replacement design.

PWDN B .0672331491835 and In3 .0649894137275mm² lie outside *enclosed* holes because own via13.35,37.025 clearance joins the plane edge. Removing ONLY that via restores those exact areas. This is an edge-connected own antipad, not evidence of an unrelated return break; it still interrupts local return spreading and is not an SI waiver. Preserve exact geometries rather than inflating masks to relabel missing area.

## Disposition before freeze

This advisory finds no additional mandatory redesign from the sampled current-feed continuity or retained-reference checks. Preserve explicit new/shared-hole and plane-area tradeoffs; do not claim electrical completion. The actionable blockers to operational use are actual sensor role/polarity contract, boot/service ownership/no contention, missing UART suppression rationale and measured/simulated loaded edges/thresholds/PDN. Any routing correction must preserve finite clearance/full mechanical budgets and be rebound to exact bytes. Full native/replay/negative/contract review is separate.

## Selected exact successor / path geometry

Selected7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1 is independently copied with project/rules. `selected_delta.json` proves only new PWDN F UUID5c11a7ef-7ebc-4120-9932-d9ac83cf2b37 endpoint changes10.475,56.9→10.462785,56.924530. Segment length1.06066017178→1.08667770159mm; every other raw UUID block and filled contour vertex exact. Old segment, new segment and added projection all have zero missing GND reference. Thus all above original6902 plane/CF findings bind to7522 without pretending the two PCBs hash-identical. Fresh selected reference computation again has3,363 retained projections/no loss. This is explicit junction normalization, not a broad finite-contact shortcut.

Independent graph recreation additionally removes each private-arm junction and verifies that it separates that terminal from all three others, after zero-length edge contraction. Planar nominal paths (vertical via length/delay excluded):

| Net | MCU→U203 | Layer sequence | True J104 private arm | True bias private arm |
|---|---:|---|---:|---:|
| RESET/TX |66.925530119mm|F/B/In2/F|2.345721925mm|6.264473616mm|
| PWDN alias/RX |74.345167339mm|F/B/In3/B/In2/F|2.024845673mm|8.848699388mm|

All six terminal-pair paths/net are saved, not only MCU→driver. RESET bias/service articulation is B.Cu(7.65427807,53); PWDN bias articulation is F.Cu(10.47289417,56.9142575); PWDN service articulation is B.Cu(11.9,55.5). Degree4 includes actual tiny overhangs, not four functional loads. The graph retains explicitly modeled short in-plane track-to-via-center connectors and does not convert finite-copper track overlap into arbitrary short circuits. Unchanged inherited U203→bias distances21.157251457/15.878596428mm are shared endpoint paths, NOT the private arms. Service adapter/cable adds an external electrical branch beyond these on-board metrics; its load is unspecified. No timing or stub-length limit invented.

Fresh selected native CLI independently reports0 violations/37 unconnected/0 schematic parity. This is a diagnostic spot-check, not the pending full negative/replay/contract review. Tool note: an initial CLI help query attempted default read-only home cache locations; actual DRC used explicit writable /tmp XDG paths. No source files edited. Primary sources were current official web reads, not recovered historical vendor PDF bytes.
