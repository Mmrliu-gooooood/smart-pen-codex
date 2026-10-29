# Authoritative selected-board feasibility candidate — NO FABRICATION

**Use this directory's `mainboard_revD.kicad_pcb` and native schematic/project/libraries together.** PCB SHA256: `016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e`.

This is the next **six-layer, stepped 14 mm feasibility board**, not a production layer/stackup decision or a complete pen. Native geometry checks do not qualify RF, USB signal integrity, power integrity, battery safety, fabrication process, or regulatory compliance.

## Actual native results
- 79 placed footprints. All their real copper pad components connected; no physical airwires.
- Full native selected-board DRC (`--exit-code-violations --all-track-errors --schematic-parity --severity-all`): **0 geometry violations, 0 unconnected, 4 missing footprints**, exit **5**. Still unimplemented: **J103 pickup, J104 UART service, J105 ADC service, J202 sensor-interface**. Do not delete them to quiet parity.
- Selected source v3: **83 components / 303 endpoints**. ERC **0 errors / 1 warning**, exit **5**: retained cross-board `VBUS_5V` global-label handoff. No warning suppression or invented physical connection.
- Whole system v3 source check separately retained: ERC 0; DRC 0 geometry / 0 unconnected / **14 cross-board missing footprints**. This is intentional allocation evidence, not a clean master parity claim.
- SW101/SW102 were explicitly allocated to the external passive recovery fixture; real J108 stays on this board. Source-v3 ownership, full manifests, and fixture handoff contract are copied under `verification/`. The four interfaces above remain unresolved.
- Actual pad graph, finite GND copper including via holes, both newly added plane wings, six-layer radiator keepout, RF reference copper, USB reference copper, and source identity tests passed normal and optimized Python. All 78 GND pad shapes belong to one finite copper component; the two wing polygons are physically connected, not merely named GND.

## Source and geometry provenance
- Frozen RF source: `../rf_feed_conditional_candidate`, preserving official AE101 pad2 NC, 0402/DNP C106/C107, and moved R104 (3.5,1.7).
- Exact source authority: `../mainboard_fixture_allocation_v3/mainboard_projection`; all child sheets and full symbol paths verified, not root hash alone.
- Earlier reproducible mechanical snapshot: `../rf_width14_usb_prelayout_snapshot`, PCB `11ae9484...5ac8c`. This selected PCB instead uses **C203 +0.10 mm X**, C103/C201/C205 +0.15 mm, J109 x12.0, R112/R113 (11.8,14)/(11.8,16), 180°. Other footprints retain RF baseline placement. Mixed-set mechanical result must bind this exact final SHA before inheritance; earlier all+.15 screen is not silently reused.
- No expansion of RF antenna corner: x12 board edge retained above y6; x14 wing only below y6. All six copper layers retain the true radiator keepout.

## Routed changes
- USB_EN1 function/GPIO unchanged. New route length **83.545563 mm**, endpoint straight distance **77.178725 mm**, ratio **1.082495**; 0.15 mm track, two 0.6/0.3 mm through-vias at (11.4,16.95) and (3.625,89.125). No blind/buried via or arbitrary USB internal transition. Initial 1M search budget exhaustion and succeeding 1.57M-node search retained as evidence.
- USB all four nets are entirely **F.Cu**:
  - `USB_DP_MCU` U101→R112: 4.144975 mm.
  - `USB_DM_MCU` U101→R113: 4.963783 mm.
  - `USB_DP` R112→J109.1: 6.100914 mm.
  - `USB_DM` R113→J109.2: 6.915128 mm.
  - Complete **trace-only** DP 10.245889 mm, DM 11.878911 mm, mismatch 1.633022 mm. These sums exclude pad traversal, resistor/internal package paths, harness and tail PCB. Nonuniform pair spacing: **SI/impedance/USB functional test gate remains open**.
- Actual filled In1 copper covers every USB trace shape; 0.35 mm side-envelope deficits are reported separately, not hidden or treated as qualification.
- In1/In4 ground wings added with finite connectivity checks. J109 GND gets a local 0.3 mm branch and via at (12.1,25.3); original x12 via collided with new EN1 and was corrected **after combined-board DRC**.
- C104 short decoupling loop unchanged. Eight terminal branches of the four relocated capacitors recentered; all old power/GND vias and trunks retained. HREF via y46.525→46.925; D3 via y31.825→31.875; original VSYNC via retained. See `decoupling_delta.json` and rendered `decoupling_before_after.png/svg`. Branch lengths do not imply total rail-load current or verified HF loop inductance.

## Remaining gates / prohibitions
Four real interfaces still need coherent physical implementation; final mechanics/harness/assembly review, exact purchased component contracts, controlled stackup and quote, RF matching/antenna validation, USB SI/ESD testing, actual camera voltage/optics verification, firmware/bench power and safety tests remain. Cost ≤380 per pen is not established by this geometry study. Charge commissioning remains OPEN; unknown camera must not be directly energized. No manufacturing release, purchase, or GitHub publication was performed by this subtask.
