# Local translator supply / return candidate — 2026-10-30 01:43 UTC

**NOFAB / NOPOWER / limited local-domain research.** This does not replace the formally accepted 9a03 baseline and does not finish the pen. Native full DRC is **0 violations /149 unconnected /0 parity, exit5**. The external `J202.23` sensor-reference input remains isolated. Do not connect the unknown vendor30-pin camera.

## Exact change

Parent PCB `77537f15c2beff27ec3098c0ccd9d3dd5cd10ac335b74c4909954f2fedcf4a24`, source102 footprints/366 physical pads. New PCB `7c81674ef29dc3e176055a823adacd5ef9847b8becd40fef520f832377dc909c`.

- Exchange only C207/C208 positions: C207 `(2,65) -> (10,65)` and C208 `(10,65) -> (2,65)`, both F-side90°. Their UUIDs, source net identities, nominal100n X7R value and0603 footprint are unchanged. This is **not** a supply-net swap.
- Remove exactly original C207 AON branch track `65eab90d-6060-4683-a290-98053d52e2b9` and via `4840f47d-9bac-414c-95e5-5f939fd72d28`; they would touch the newly placed C208 sensor pad. Reconnect C207 AON on the right with the explicit new branch.
- Preserve all other679 copper objects exactly. Add57 objects (37 tracks,20 standard0.60/0.30mm vias); new total736. No plane boundary, rule, outline, source, other footprint or earlier MCU EP via is changed.
- Adjacent AXC local links use0.3mm tracks; TCA doglegs use0.254mm. These are project geometry choices, **not manufacturer current ratings or mandatory vendor widths**.
- All current physical pads formerly in a same-net connected component retain that connectivity, including the two moved capacitors.

## Actual source-domain contract

| Device | AON3.3V pin | External SENS reference pin | Local bypass |
|---|---|---|---|
| U201 AXC8 | VCCA1 | VCCB23/24 | C201=AON, C202=SENS |
| U202 AXC4 | VCCA1 | VCCB16 | C203=AON, C204=SENS |
| U203 AXC4 | VCCA1 | VCCB16 | C205=AON, C206=SENS |
| U204 TCA9517 | **VCCB8** | **VCCA1** | C207=AON, C208=SENS |

U204's A/B naming differs from the AXC parts. `SENS_VIO_1V8` is an **external head reference input**, not an on-board1.8V regulator. No AON/SENS short or substituted local regulator has been introduced. DIR pins retain the original source ties.

## Evidence

- Full CLI uses bound same-basename`.pro`/`.dru`, `--all-track-errors --schematic-parity --severity-all --exit-code-violations`. 149 unconnected items remain; zero violations is not completion.
- Finite copper connectivity with actual layer membership and physical-pad identity: AON J106.2 core **14→23/39**; GND J106.3 core **39→57/102**. All required U201–204 local ground/control ties and C201–208 ground pads reach the GND core. All local AON pins/caps reach the AON core.
- All nine local supply-to-cap pairs connect. SENS input core remains **1/12**, exactly J202.23. The four local SENS-cap islands are not a powered reference network.
- `verification.json` and optimized run are identical. Domain-deletion finite-copper negatives reject; three actual native deletion+fresh-fill+CLI counterfactuals detect additional unconnected items.
- Exact replay produces the same new SHA. Removing57 additions, restoring the exact two old objects and two old poses, **saving/reloading/building connectivity before fill**, precisely restores parent SHA and0/181/0. A rejected first counterfactual that filled after live pose mutation without reloading left a stale AON clearance image; it is retained as a tool-state failure, not a valid test.
- All new through-via disks avoid every physical pad on all actual copper layers, including same-net pads. This avoids the earlier C504 drill/pad mistake but is not a mask, tolerance or wicking qualification.
- Refilled planes are measured with guarded one-shot conversion of raw KiCad fractured paths. Existing signal-reference projections show no additional lost area above the documented numerical reporting threshold. Main GND areas lose2.565012mm² and gain0.646573mm² each; small GND areas lose0.005452mm² each; AON loses8.295841mm². All normalized0.25mm-eroded outlines in this limited check remain one component. These measures establish neither ampacity nor transient/EMI performance.
- Actual native F-copper plot was inspected. The exchanged cap pair has identical nominal aggregate pad/courtyard/model geometry and occupies the same two sites. The source-pin to bypass-pad straight-line distance falls from about6.358mm to2.574mm each; new TCA routed centerline is3.6375mm. This is a placement improvement, not an inductance or frequency-domain guarantee.

## Bounded failures and remaining gates

An initial no-swap local model is retained as planning only. Eighteen simple left-side SENS trunks on B/In3 with fixed branches were collision-rejected; they are **not** a proof that the reference rail is impossible to route. No sensor through-vias from that failed model were instantiated. A future bounded topology must jointly route J202.23 and the local islands/pullups without compromising return references.

TCA nominal cap occupancy is unchanged, but actual capacitor MPN, effective capacitance/DC bias, package-height and assembled solder envelope remain procurement/assembly gates. New vias are outside pad copper nominally; hole treatment/mask openings, registration, clearance tolerance, cap loop inductance and supply ramp/back-power behavior remain unqualified. Earlier MCU23.8µm EP-hole margin and eight in-pad vias are **unchanged unresolved manufacturing risks**. Main analog MCU supplies, remaining ground/other signals, battery/charging qualification, camera power and physical tests remain incomplete. JP301 remains OPEN.

## Primary sources checked 2026-10-30

- [TI SN74AXC8T245 datasheet, Rev.C, §8.3–8.4](https://www.ti.com/lit/ds/symlink/sn74axc8t245.pdf): ground reference first, supply bypassing and short routing. It does not provide a trace-width/ampacity approval for this board.
- [TI SN74AXC4T245 datasheet, Rev.B, §8.3–8.4](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf): ground reference first and bypass capacitors close to supply pins; domain naming/pin functions independently match the native embedded source.
- [TI TCA9517 datasheet, Rev.D, §11–12](https://www.ti.com/lit/ds/symlink/tca9517.pdf): approximately100nF bypassing close to both supplies; A and B voltage ranges differ. Existing source uses its low-voltage A side for SENS and B side for AON.

No purchasing, manufacturing, powered tests, radio, flashing or GitHub publication was performed in this task.
