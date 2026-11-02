# Actual distributed J107 native — conditional mechanical review

Native `617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5`, exact parent current24 `dcaaafa93bde51e58a96d9443cb77031773fc42a16ad3db20210b53f0394b052`. Earlier978/7d22 reviews remain immutable and do not establish this design's acceptance. Electrical/plane reviews remain separate.

## Exact changes and bindings
102 other raw footprint blocks are byte-identical. J107 is now `GateStudy:J107_DistributedWireLands3_NOFAB`, B.Cu, origin (6.4,31.66), angle0. Actual pads: EN1 (5.22,34.31)270°, EN2 (7.2,25.38)270°, GND (6.4,31.66)180°. Each retains native unrotated1.5×2 mm copper, original rounded-corner geometry and +.04 mask expansion; EN1 radius .375, EN2/GND radius .05. No EN1 terminal escape is authorized by this review.

The 104-object contract intentionally replaces only three J107 per-pad packing prisms. Each remains7.92mm³, 2mm height, 2.2×1.8 or1.8×2.2 matching actual pad rotation. Native footprint pose and each pad-specific pose are separately recorded, not misrepresented as one rigid three-terminal connector.

18 added tracks+2 vias,23 removed tracks versus24. All retained copper signatures unchanged. New finite copper/via outer envelopes screen against full104; **every retained exterior track/via is also screened against relocated J107 budgets**, with no old-copper exemption there. All other native pads clear new joint budgets. 50 applicable F/B/inner-layer track/via keepout checks pass; other rule geometry/flags unchanged. U101 source lead/body overlap entirely in actual rotated source pad. No prior-copper projection allowance is needed for added copper in this candidate.

## Two NEW narrow terminal contracts
- EN2 .15 B north: exact lead (7.2,25.38)→(7.2,24.33), ring X7.125..7.275/Y24.48..24.63. Outside pad .0225mm², existing mask exposes .006 and nominally covers .0165.
- GND .30 B west: exact lead (6.4,31.66)→(5.33,31.66), ring X5.50..5.65/Y31.51..31.81. Outside pad .045mm², exposed .012 and nominal covered .033.

These are owning-pad, owning-net, fixed-width, direction/position/layer-bound conductive-joint routing semantics ONLY. Wrong net/width/side/position/terminal mutations reject; via ownership forbidden. Neither old tail-J107 coordinates nor a whole-envelope waiver is reused. Normal and Python-O results agree. Physical prisms are not cut or shrunk; solder volume, mask registration, wire insulation/strain relief, approach and tool space remain unqualified. No “fully masked neck” claim.

## Whole known214 saved scene
Saved `DISTRIBUTED_J107_DEFAULT_STACK_NOFAB.FCStd` has234 objects/214 shapes. Only3 J107 packing shapes changed;211 shapes unchanged. Each new prism was independently checked against all213 other known shapes, including power-board bodies, refill/shell/neighbors. No solid intersection. Nearest positive gap: EN2 to POWER_SCREEN_C6 **.163395702816mm**; EN1↔GND .65mm. These are nominal model gaps, not tolerance-certified fit. Negative forced overlap with Power_L1 rejects.

All104 new saved bounds checked after reopening; current native binding independently found in saved Document.xml;211 unchanged shapes independently reread and compared by bounds, volume, area, face/edge counts. Source remains historical1534 default known-only scene carried through current24, NOT a complete1624 qualified assembly.

Historical locked-cap-vs-pack conflict44.244881mm³ remains unchanged. All unknown operation/probe/harness/bend/contact/tool/power-service objects remain. No wire harness or solder/tool shape has been invented. EN1 still open. ADC battery frontend is not qualified by this work. No whole-pen, safe-power, SI/PDN or fabrication release.

## Replay dependencies
Relative to workspace:
- `sensor_d5_candidate_20261102_0445/release/candidate/mainboard_revD.kicad_pcb`
- `pcb_interface_codesign_20261102_0612/candidate/mainboard_revD.kicad_pcb`
- `independent_d5_final_mechanics_20261102_0451/full104_d5_24.json`
- `independent_d5_final_mechanics_20261102_0451/D5_24_DEFAULT_STACK_NOFAB.FCStd`
- `control_interface_nonlinear_20261102_0609/proposed_pad_budgets.json`

Run `/usr/bin/python3 review.py` (also -O), then `scene.py`, then `readback.py`. FreeCAD library path is in scripts. Native/full104 are hash-bound; scene serialization hashes may vary on replay but geometry/binding checks must pass. Only manifest-listed deliverables, no automatic scene backups.
