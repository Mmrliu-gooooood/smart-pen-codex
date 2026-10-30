# Local translator domain candidate — independent limited review

**NOFAB / NOPOWER.** This is a static local-domain research review, not a complete pen, safe-off certificate, production release, or replacement of the formal 9a03 baseline.

Reviewed PCB `7c81674ef29dc3e176055a823adacd5ef9847b8becd40fef520f832377dc909c`; author manifest `74eeebcacc1e991103d589c7264b6d8063080d931bfd1bf5c44f10be2cb31c50`. All 112 author files and 53 exact dependencies were verified before and after the review.

## Bounded findings

- Fresh full native KiCad 9.0.2 DRC, bound same-basename project/rules, all-track errors, schematic parity and severity-all: **0 violations / 149 unconnected / 0 parity, exit 5**. This is incomplete, not overall pass.
- Independent finite-copper graph (100 nm approximation, 512-edge drill subtraction, actual `IsOnLayer`, physical pad UUIDs) confirms AON **23/39**, GND **57/102**, and external SENS input **1/12** at their respective core terminals. The only SENS input-core terminal is J202.23; the four local reference islands are not a complete powered reference rail.
- All nine supply-to-bypass pairs connect locally. Independent cross-domain finite-copper comparison finds no AON/SENS copper overlap on any actual copper layer. This does not replace leakage/back-power or supply sequencing verification.
- Exact object delta: two old C207 branch objects removed, 57 new objects added, all 679 remaining original copper objects unchanged. C207/C208 alone exchange positions at F 90°; actual reference, pad UUID, net identity, value/package, layer and orientation remain attached to the original component identity. No supply net swap occurs.
- All twenty new through vias were independently checked against every actual pad on every actual copper layer, including same-net pads. Ring and drill overlap results are zero. An intentionally moved same-net ground via into C201.2 is detected by the drill screen (about 0.070684 mm² overlap), demonstrating why native same-net DRC alone is insufficient.
- Independent whole-domain deletions break the intended local connections. Three real native saved/refilled deletion tests (C201 supply via, U204 ground via, TCA SENS link) each yield **1/150/0**, exit 5. These are deliberate fault cases, not accepted boards.
- Exact materialization replay reproduces the reviewed PCB SHA. Removing all 57 additions, restoring the two old objects and swapping both capacitor poses back, with save/reload/connectivity rebuild before fill, precisely returns parent `77537f15…` and **0/181/0**.
- Independent graph normal and optimized outputs are byte-identical. Author all-net connectivity/reference verification was separately reproduced in an isolated copy, normal/-O identical; previously connected physical-pad components remain intact, including existing DVP chains and restored nets.

## Actual supply naming checked from the source

The manually generated board's `PAD.GetPinFunction()` fields are empty. The first attempted assertion was correctly rejected and retained in `REJECTED_empty_PAD_pin_function.log`; blank fields were **not** taken as evidence of pin function. The independent checker instead parses the actual embedded schematic libraries, resolves the U201–U204 instance libraries, and combines their pin functions with native pad nets and schematic parity.

- U201: VCCA pin 1 = AON; VCCB pins 23/24 = SENS.
- U202/U203: VCCA pin 1 = AON; VCCB pin 16 = SENS.
- U204 TCA9517: **VCCB pin 8 = AON; VCCA pin 1 = SENS**.

Thus TCA A/B names are deliberately opposite to the AXC rail naming. J202.23 remains an external reference input. There is no new local 1.8 V regulator or permission to connect an unknown camera.

## Reference, nominal mechanical scope and unresolved gates

Fresh-fill plane/projection checks were reproduced using the required guarded one-time conversion of known raw-fractured geometry. Prior signal projections show no additional reported uncovered area; normalized erosion is not a current rating, RF/SI qualification, or transient test. The exact plane deltas remain in `author_verify.json`; they must not be reduced to “unchanged planes.” The old-source and new-source ground return, leakage and power-up/off behavior have not been measured.

The actual native local-domain plot was inspected. Reproduced capacitor-envelope comparison confirms equal nominal aggregate package/pad/courtyard/model occupancy at the same two sites. That does not establish the selected actual MPN, effective capacitance under bias, assembled height, solder envelope, bypass-loop impedance or vibration clearance. Earlier MCU eight in-pad vias and the relocated drill's 23.8 µm nominal EP-edge margin remain unresolved DFM risks. JP301 stays OPEN; main analog supplies, remaining grounds/signals and external reference distribution remain unfinished.

## Reproduction contract

This review manifest contains new review code/results, fresh DRC, reproduced author verification, native counterfactual evidence and integrity records. It does not duplicate copied native boards or copied author scripts. For reproduction in a new `hardware/<review-dir>`, copy the hash-bound candidate's `native/`, `verify.py`, `finite_copper.py`, `native_polygon.py`, `materialization.json`, `plan_v2.json`, `drc.json`, `materialize.py`, `counterfactual.py`, `native_negative.py`, and `pose_envelope.py`. Keep all 53 declared dependencies at their original repository-relative paths. Run `independent.py` normally and optimized; reproduced author checks and three native deletion cases have separate recorded outputs. Never execute these output-writing scripts in the frozen original candidate directory.

No physical measurements, firmware changes, procurement, fabrication, energizing or publication were performed. **Do not fabricate or power this incomplete research board.**
