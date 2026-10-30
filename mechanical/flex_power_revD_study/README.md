# 18 mm head-flex and current-board integration study — NOFAB

2026-10-28. This is a **separate conditional geometry study**, not a print, manufacturing release, selected camera, qualified flex, or closed tolerance stack. Prior `whole_pen_revC` files are unchanged.

## Results that change the previous assembly assumptions

1. The new power board is **14 × 45 mm**, not the old 10 × 5 × 18/22 mm aggregate tail placeholder. The previous 180/210 mm assembly cannot simply inherit it.
2. Strict axial succession of the latest 95 mm mainboard, RF reserve, complete battery budget, actual-length power board and USB board produces a **260 mm** reference body, 50 mm longer than the previous 210 mm axial study. This is a comparison, not a recommended pen.
3. Placing the power board behind the mainboard over Z82..127 produces an **18 × 213 mm** conditional alternative. The actual XCLK5 / recovered BIAS4 / sampled HREF3 component placements were each checked separately. Nominal represented solids have no positive-volume collision and remain within ID15.6. Native CAD reopen and STEP reread pass. **The smallest radial margin is only 0.296792 mm**, below this study's 0.30 mm screening budget and before a real tolerance chain. It is not ready to manufacture.
4. A head flex departing **inward from rear-face pads** rather than outward from the board edge removes the previous nominal quarter-bend collision in all 16 tested parameter combinations. This requires a different, presently unconfirmed departure direction. It does **not** prove the existing camera flex can be folded that way. The proposed bend ends before a host connector and is not a complete interconnect.

## Which hardware was actually represented

`inputs/current_board_extract.json`: actual XCLK5 12 × 95 × 0.8 mm board, 74 footprint positions, side, DNP, F.Fab/B.Fab/pad bounds. `inputs/bias4_board_extract.json`: recovered BIAS4, SHA256 `0796d092b4775e314f9b5f43b62b0a7ba153c9b4e8804fb02c6f0ea8cdeae5cc`. **R217 is F.Cu 0402**, not a newly added backside component. `inputs/href3_board_extract.json`: HREF3 sampled while still under review, SHA256 `f00d85c7eea8e8abdbf89eb83720fa7aeca564e939f0b6b5f89d548881cb7815`; R220 is moved to B.Cu. This mechanical check does not adopt or freeze that electrical candidate.

Actual mainboard prisms use source fabrication/pad bounds, known package maxima where already documented, and explicit unknown-passive height 1.0 mm plus assumed 0.15 mm solder allowance. They are not manufacturer STEP models. **16 schematic footprints are still absent from the PCB**, so zero collision cannot cover those missing physical items.

The power board has a real 14 × 45 outline; its **4.15 mm total populated thickness remains a conditional envelope**, not extracted individual bodies. USB has a real 12 × 20 outline, but 5 mm overall height is an assumed budget. Full USB receptacle mating/access, load transfer, wiring and connectors remain absent. Full battery Ø12.2 × 49 is a budget including NTC/sleeve/contacts, not a qualified assembled battery product. RF is only a reserved volume, not a certified antenna keepout.

## 213 mm stacking coordinates and actual checks

- Pen axis +Z; nominal refill axis Y=-3.8, Z0..67.
- Mainboard base Y2.9..3.7, Z32..127. Actual front/back package prisms retained.
- Power total-thickness budget X±7, Y-2.7..1.45, Z82..127.
- Required compact contact cassette Ø6 × 12, Y=-3.8, Z68..80. **Still a required envelope, not a completed mechanism.** Power-to-contact gap 2.0 mm nominal.
- Battery budget Z141..190; power-to-battery axial separation 14.0 mm. This is not a thermal safety result.
- RF reserve Z128..139; USB board budget Z192..212; reference barrel end Z213. No hidden reduction of actual board lengths.
- Back R105 and R214 to power: 0.30 mm. Sampled HREF3 back R220 to power: also 0.30 mm.
- Closest main component-corner margin: 0.296792 mm; power rectangle margin 0.297334 mm. Depending on equal-value corner ordering, R210/R221 are reported as the limiting passive prism. Mainboard is not silently reduced to an empty rectangle.

**Tolerance sensitivity fails before production qualification.** With only hypothetical +0.1 mm radial wall error and 0.2 mm outward assembly/bow allowance, the conservative remaining radial budget is -0.003208 mm. These are diagnostic inputs, not supplier tolerance specifications. Increasing unknown passive height from 1.0 to 1.3 mm gives only 0.099472 mm radial margin and zero nominal backside gap; 1.6 mm gives radial interference -0.104311 mm and backside overlap 0.30 mm. Actual MPN heights, solder, warp, mold/print tolerances, insulation thickness, supports and serviceability must be frozen and rerun. A small mathematical undershoot is not a waiver.

A 19 mm outer diameter with the same wall/coordinates would add 0.5 mm nominal radial room; it would **not** improve the 0.30 mm inter-board gap or solve missing components. This is a tradeoff, not a decision to abandon the user's 18 mm target. Lower-profile qualified parts, local component relocation, revised supports and separated boards should be compared before changing the target.

## FPC inward bend: what changed and what did not

The earlier diagnostic bend leaves a board edge outward, causing shell/refill interference. The new bend starts at the **back face**, at Y=-2.2 or Y=5.8 for an 8 × 8 head centered Y1.8, and travels inward while turning toward +Z. Parameter sweep: width5/8, neutral-axis radius3/5, rear offset0.2/0.5 mm, thickness0.15 mm. All are assumptions. No claim is made that R3 is safe for any real FPC stack or repeated bending.

For W8/R3/offset0.2 from the -Y side: minimum represented camera distance0.125 mm, refill distance0.425 mm; endpoint Y0.8/Z27.2. No shell overflow or camera/refill intersection. This tiny rear clearance still lacks tolerance, insulation and strain relief. Need actual pad or connector departure tangent, coverlay/copper stack, stiffener, bend exclusion zone, neutral axis/minimum static bend radius and endpoint connector before this can become an assembly.

The future head uses 8 × 8 PCB, a **hypothetical H6.5 mm stack**, and unconfirmed lens/holder interface. It is NOT the purchased 13 mm SC035HGS custom module.

## Purchased camera versus future compact pen

Previously reviewed custom-module PDF dimensions are 13±0.2 mm square board, nominal21.82 mm ear span, lensØ10 and 9.44 mm axial dimension. For its board transverse to the barrel (sensor axis parallel to barrel), the square alone requires at least:

- Nominal 13 mm: sqrt(2)×13 + 2×1.2 = **20.785 mm outer diameter**, with zero clearance.
- 13.2 mm maximum square: **21.068 mm outer diameter**, with zero clearance.
- Retained nominal21.82 ear span alone gives necessary outer diameter **≥24.22 mm**, before ear-span tolerance/clearance; the full ear shape may require more.

These are necessary aligned-section bounds, not proof that all tilted arrangements are impossible. Tilting changes optics, depth, flex and paper clearance and needs its own complete model. Ear outlines and connector geometry are not fabricated from their bounding span; no instruction to cut ears/flex is implied.

**First two functional prototypes and final slim product are different gates.** The purchased camera can remain on the already planned optical test fixture or an oversized, dimension-confirmed head while electrical compatibility, near focus, illumination and real decoding are verified. An 8 mm compact replacement requires a real drawing/price/availability/driver/near-focus qualification before integrating it into the two-prototype budget. This study authorizes neither purchase nor changing the budget and does not promise the two first prototypes will already be 18 mm pens.

## Other arrangement screens

- Complete Ø12.2 pack beside a 14 × 4.15 power rectangle with 0.3 gap, under the tested simple parallel cross-section arrangement, needs approximately **22 mm outer diameter** with1.2 wall. This is not a global bound over all rotations or axial staggering.
- An ideal 12 × 2.15 main rectangle stacked with14 × 4.15 power and0.3 gap looks easier, but ignores actual backside parts. It is explicitly not used for the CAD pass. The actual-component models above supersede that optimistic screen.

## Files and reproducibility

- `extract_current.py`, `extract_bias4.py`, `extract_href3.py` preserve independent source identities in JSON. The scripts refer to the cloud sibling electronics tree; inputs permit offline inspection without pretending current source revisions match automatically.
- `build_study.py`: inward-flex sweep, 260 mm reference, aligned-camera bounds.
- `build_stacked.py`: XCLK5 213 mm candidate.
- `compare_updated_boards.py`: BIAS4 and sampled HREF3 213 mm alternatives.
- `*_validation.json`, `updated_board_comparison.json`, `tolerance_sensitivity.json`: checks and limitations.
- Four native FCStd and four STEP files are **mutually exclusive studies**. No STL, manufacturing drawing, fastener system or printable enclosure is released.

FreeCAD1.0.0 / OCCT validations were run. CAD success establishes only nominal geometry of represented shapes, not lens quality, charging safety, flex lifetime, EMC/RF, thermals, drop resistance, manufacturing accuracy or handwriting accuracy.
