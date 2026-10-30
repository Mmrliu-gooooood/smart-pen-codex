# Exact-visibility simplification of complete IMU model

**READ ONLY / NOT NATIVE / NO FAB / NO POWER.** Parent PCB unchanged: `69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`, actual0/113/0. This is a separately authorized simplification of frozen complete grid model `imu_full_joint_plan_0505` (manifest `416a3ac65e88e3815ff821a3b20ff22efc9c95d3d3d4e083d7c5e6504f06ae05`), **not a fabricated106-airwire native result**.

## One bounded deterministic pass

`simplify.py` performs1523candidate visibility checks across the five grid-generated long/pullup paths. It does not run another full-length router. Only same-layer continuous runs can be replaced by fewer straight segments, with the original width. All actual contact-bearing segments at pads/external same-net branches, all vias, all analytic local MCU/MEMS fanouts and both AON supply reconnections are fixed. Candidate segments must:

- Pass exact finite-copper clearance against all actual old copper, all other new nets, all pads, native board edge and MEMS rule areas.
- Avoid creating additional external same-net branch contacts or crossing other path segments.
- Retain protected physical branch segments rather than merely preserving an endpoint list.

No pixel acceptance, clearance relaxation, arbitrary smoothing or moved footprint is used. This is not a claim that new copper equals old copper: `comparison.json` reports removed/added copper area per net/layer and independently proves exact retained vias, widths, local parts and protected contact segments. Same-net contact protection is intentionally conservative; some tiny segments remain.

## Before / after

| Net | Original→new length mm | Original→new segments | Vias unchanged | <.1mm segments original→new |
|---|---|---|---:|---|
| SCL |81.476399→81.004717|184→35|4|167→21|
| SDA |84.507706→83.185206|199→50|3|168→29|
| IRQ |78.568291→77.440401|69→30|4|31→3|

Signal segments452→115; short segments366→53. Total new objects, including AON,474→137. There are no remaining adjacent same-direction collinear pairs. The remaining53short segments are retained, not silently rounded away. This is more maintainable than the grid variant but **not a claim of final product/DFM elegance**.

## Complete physical model evidence

Reconstructed from serialized `strategy1.json`, not trusted in-memory router objects:

- All physical pads of each complete SCL/SDA/IRQ net form one component, including actual R501/R502 signal pads and MCU/IMU pins.
- Both10k pullup AON supplies connect to actual core copper. No imaginary via at(4.35,85.6): R502 returns to C503.1(4.35,84.5).
- All old physical pad components remain, including pressure/STRAP and existing DVP/clock. Footprints, source, straps and13new-via coordinates/sizes/drills are unchanged from the frozen complete model.
- Conservative new-via antipad screen: AON38/GND70/SENS12core pads; all IMU14 power/ground remain. Same vias mean this plane-hole model is unchanged by visibility simplification.
- Additional projection loss onto old signal copper, including EXTCLK, remains zero under that screen. **Native fill, actual reference continuity, timing, EMI and bus capacitance still need verification.**
- Removing each long-route/local-source/pullup group yields expected disconnection. CS/SA0 direct B feed preserves its four negative controls with all planes excluded.
- Verification, metrics, geometry difference and the simplification replay agree under normal and optimized Python. No safety assertion depends on Python `assert`.

`layers.svg` and `layers.png` show current F/In3/B geometry; gray is old retained source and colored is this variant. The PNG was rendered and visually inspected. Planes are omitted for legibility, not removed from the electrical model.

## Unchanged hard gates

Do not native-materialize or fabricate merely because this model connects. Parent decides the next stage. Required later: real freshfill, full `--all-track-errors --schematic-parity` DRC, ERC, source/resource equality, complete pad/core checks, actual via/reference contours, native cuts/replay and independent review.

All courtyard intersections listed in `verification.json` remain open DFM/assembly gates: U501 outer-fanout vias, U101 underbody/courtyard, back C504, R501, J301, JP201 and back J105. They avoid real pad copper but are **not** proven safe for stencil/tenting/assembly/stress. The narrow MCU SDA U101.14 corner and SDA MEMS escape need actual manufacturing-margin review. No via-in-pad or keepout waiver is implied.

Preserve prior pressure BOOT/NIB merged reference-hole, underbody-via, clock/J107 harness, mechanical, camera, charging and cell gates. JP301 OPEN. Unknown camera remains disconnected. 10k/100kHz is only a future controlled-test starting point; IRQ `_N` naming does not configure polarity, the firmware provider remains absent, and no functioning prewake/first-stroke performance is claimed.
