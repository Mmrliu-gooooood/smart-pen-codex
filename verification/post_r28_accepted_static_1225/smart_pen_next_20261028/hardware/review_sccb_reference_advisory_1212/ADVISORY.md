# SCCB reference advisory — read-only, 2026-10-30

## Decision
A blanket prohibition on any uncovered projection or any shared via clearance is a conservative routing preference, not a demonstrated TI/Espressif electrical requirement for this link. Do not declare SI passed at 100 kHz, and do not prefer the much longer comparison merely to improve that Boolean classifier. Prefer the smallest targeted local repair for subsequent independent static review; permit consideration of an explicitly recorded bounded source-transition exception while leaving electrical/EMI qualification open. This advisory is not adoption, fabrication or power authorization.

Pinned diagnostic PCB: faf2912fb2896891b21c1e7f96f8bdc65253cac04ec47b31bfde81e3ded3e424 (sccb_bypass_native_1131). Own measurements.json and stitch_screen.json were produced against a copy. Matching project and rule files are essential for refill: initial measure.log lacked these and is superseded by measure_projectmatched.log/measurements.json.

## Geometry and interpretation
- In3-to-In4 GND separation is nominal 0.13 mm; In3-to-In2 AON is 0.2028 mm. Requiring total coverage by BOTH layers improperly treats mixed AON coverage as an independent mandatory ground plane. Closer In4 is a plausible dominant reference, not proof of exclusive return or qualified stackup.
- Source SDA via (6.25,67.65) shares a bounded clearance hole with CAM_CT/CAM_ON. The categorical 0.066487 mm² non-isolated-hole result mostly includes its own transition antipad. In a diagnostic counterfactual ONLY, removing CT/ON vias and refilling the copied board with matching rules recovers 0.001599384 mm² F/In1 and 0.0010442354 mm² In3/In4 projection. This is not a proposed board edit, nor an inductance/noise estimate.
- A move to (6.075,67.6) cannot preserve a ~6 µm nominal web with the actual 0.15 mm zone minimum thickness. Native refill, not ideal circular masks, decides clearance topology.
- Separate PRELINK grazing on In3 segment (10.525,73.85) to (10.175,73.8) occupies about 0.00005034757 mm² in the union analysis. A local southward elbow is preferable to a board-wide detour. Small area alone neither establishes nor disproves electrical significance.
- Existing nearest GND-via distances are 1.909 mm at source and 5.443 mm at sink. These are descriptors, not acceptance thresholds. Eight local candidate ground-stitch sites screened here fail copper/mechanical constraints; no untested stitch location is endorsed.
- CAM_CT is the TPS22918 slew-control capacitor node; CAM_ON is its enable network. Preserve these functions and assess coupled disturbance, especially startup/high-impedance states; do not move/delete them to satisfy the classifier.

Author comparison1204 b4c41c09bba8959e93602f4c3b9fde078ee028b4f4adbc3cf3777111e44c6abd reports SDA 36.942642 mm and 3 vias versus diagnostic 18.280243 mm and 2, but source hole still merges. It is not preferred on the current evidence.

Author local repair1216 dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697 was independently hash-checked here. Author delta/classification reports add only a local SDA elbow and C301 power dogleg, unchanged vias/filled planes, remove PRELINK grazing and give SDA18.332142 mm (+0.051899) with the same2 vias. This is the preferred next independent static-review target; those full verification claims are not independently reproduced by this advisory.

## Defensible gates
1. Preserve actual native DRC, exact intended partitions, finite copper paths, retained-route references, replay/rollback and full mechanical/drill/enclosure checks. These added links join U204 to pull-ups; U101 SDA/SCL remain separate in the diagnostic, so they do NOT constitute a fully connected operational MCU bus.
2. Inspect actual filled same-net unions after refill. Establish common GND islands and available return paths at both F/In3 transitions; document bounded void extent and stitches. Do not cross a genuine plane split or accept an isolated return island merely because total uncovered area is small. Do not expand artificial masks or tolerances to force a pass.
3. Preserve close 100 nF decoupling, valid AON feed/return and C301 clearance repair. Prior C207 geometric advisory does not demonstrate loop-inductance improvement over baseline.
4. For later electrical qualification, determine actual rails, per-buffer-side capacitance and parallel pull-ups; check source/sink currents and device-specific VIH/VIL/VOL, including TCA9517 B-side offset. Calculate rise-time limits and evaluate fastest falling edges, propagation, settling, ringing, false transitions and coupling into CT/ON. Then verify setup/hold, ACK and power sequencing under representative worst-case load/supply/temperature when authorized. NO POWER remains in force now.

## Source-based electrical rationale
TI gives tr=0.8473*Rp*Cb and a 1000 ns Standard-mode rise-time limit. A 10 kΩ pull-up implies about118 pF nominal or116.85 pF at +1% resistance, before other uncertainties. It is not automatically invalid, nor validated without actual per-side capacitance. Buffer-separated loads must not simply be summed as one bus. https://www.ti.com/lit/an/slva689/slva689.pdf

TCA9517 transition timing depends on test loading and pull-ups; its active low transitions are not set by the 100 kHz transaction rate. Device-specific static-offset thresholds and close supply bypassing matter. No numerical shared-antipad ban is specified. https://www.ti.com/lit/ds/symlink/tca9517.pdf

Espressif supports100 kHz Standard-mode and emphasizes capacitance-dependent external pull-up selection; its usual2–5 kΩ recommendation is not a command to change the existing10 kΩ without loading/current analysis. https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/i2c.html

General TI layout guidance supports return continuity and avoiding splits, but its high-speed examples do not establish an SCCB-specific numerical zero-projection rule. https://www.ti.com/lit/an/sbaa405b/sbaa405b.pdf

Remaining uncertainty: actual fastest edges, bus capacitance, sensor/FPC load, production stackup, transition return impedance, CT/ON noise and EMC behavior. A bounded static layout exception can be documented without pretending these are resolved. The absence of a path in the bounded strict router is not a global routing impossibility proof.
