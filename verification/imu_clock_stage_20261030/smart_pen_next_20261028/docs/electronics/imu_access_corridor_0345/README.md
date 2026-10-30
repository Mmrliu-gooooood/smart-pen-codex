# IMU access corridor: two local J107 placements, both electrically rejected

Status: **PLAN ONLY — NO NATIVE SAVE — NO FAB / NO POWER.**

Source: pressure-corrected mainboard SHA256 `6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c`. R503=47k remains unchanged. No source edits, native refill, native DRC, upload or physical work. Source DRC 0/134/0 is inherited, not a result for this proposal.

## Scope and outcome
Exactly two coherent J107-only placement hypotheses; U501 and C501–503 unchanged. J107 is a backside external USB_EN1/USB_EN2/GND harness termination, NOT an IMU interface or permission to omit low-power IMU operation. All three source J107 pad components were isolated; moving the port cannot break an already connected pad component, but its future wiring and mechanical access must be qualified anew.

1. **J107 (3.2,88),180°,B:** axial +4 mm. Pad3 crosses J202.21/.22/.23 and two existing SENS_VIO_1V8 copper objects. J107/J202 courtyard collision 3.2636 mm². Four nominal mechanical collisions across the four CAD contexts. REJECT.
2. **J107 (5.2,84),180°,B:** transverse +2 mm. All three pads cross ONE existing SENS_EXTCLK B.Cu segment UUID `2010858e-8edf-52c4-a3a5-f423a79bbfc8`. No other foreign old-copper collision or same-side courtyard collision found. Four nominal CAD contexts have zero collisions; minimum non-board clearance 0.93 mm. Electrically REJECT until that old net is restored on a new verified route. This is a concrete structural direction, not a feasibility claim.

`check_poses.json` and byte-identical optimized-Python replay independently test moved native pads against ALL old tracks/vias and other native pads on actual copper layers. Checks use 0.15 mm foreign copper clearance and actual native transformed pad geometry. Same-net restoration evidence comes from the complete pad-component model, not net names alone. No third position searched.

## Complete IMU supply/return geometry hypothesis
`explore.py` constructs 28 objects in memory: 0.25 mm tracks and two standard 0.60/0.30 mm through vias at AON (2.65,79.9), GND (2.65,83.3). `check_model.json` records exact endpoints and all 14 target pads. New objects pass finite copper, all-layer pad, drill, board-edge and existing native no-via/no-track rule checks for the FIRST placement. The first preliminary C503 diagonal crossed the GND bus and was replaced by the left x=1.8 mm route; that rejected code is retained.

Seven AON pads: U501.2/.3/.9/.10, C501.1/C502.1/C503.1. Seven GND pads: U501.5/.6/.7/.8, C501.2/C502.2/C503.2. ST LIS2DW12 pin contract remains unchanged: CS/SA0 tied AON; RES7 GND; NC5 may be GND. U501 body/decoupling placement and MEMS central fanout restrictions are unchanged. GND via overlaps U501 courtyard by 0.0292143 mm² but not the project body/no-via rectangle; this is NOT assembly/stress clearance approval. TN0018 stress/assembly qualification and actual part heights remain open.

The isolated-domain finite model shows AON35/39, GND69/102, SENS12/12 and retains every old pad component. **Those counts must NOT be reported as a valid board improvement:** first-placement J107.3 also touches existing GND/J202 and simultaneously violates other domains. The model does not turn an inter-net short into a valid connection. Removing either new domain access via disconnects all seven target pads for that domain, retained as a causal negative. Old signal reference-plane projection loss is zero in the nominal plane model; 0.25 mm eroded planes remain single components. These are nominal polygons, not native refill sign-off.

## Mechanical evidence and limits
`mechanical_screen.py/json/log` reuse exact retained full wire termination budget boxes (each 1.8×2.2×2 mm); no height reduction. R206 is adjusted to its accepted (9,46) pose in those contexts. Original context hash is verified. RevC, RevD_BENCH, ACCESS19 and ACCESS20 are nominal contextual CAD, not a regenerated current-board full assembly. Main-board face contact is intentionally excluded; Context_ONLY summary shapes excluded. Later unrelated board changes are not represented by these older contexts. Actual wire, solder fillet, bend radius, strain relief, tool access, insulation and thermal envelope remain unqualified. This screen establishes a direction for J107 only, not complete production fit.

## Next bounded proposal requiring review
Prefer second transverse J107 placement; retain U501 and all three caps. Permit a LOCAL restoration/reroute of the single conflicting SENS_EXTCLK segment, preserving its entire original connected pad component, width, voltage domain, reference return path and camera connector. Do not move J202/MCU/RF, and do not remove EXTCLK by declaring it unnecessary. Only after all moved-pad, new-copper, connectivity, mechanical and causal-negative checks pass should a native candidate be saved/refilled/DRC-tested. If no legal local path exists, separately review splitting/reorienting the three external harness termination pads with the full wiring budget.
