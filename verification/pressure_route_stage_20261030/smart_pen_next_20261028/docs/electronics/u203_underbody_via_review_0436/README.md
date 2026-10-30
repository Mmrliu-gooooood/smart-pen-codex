# U203 underbody pressure-GND via: bounded independent DFM review

2026-10-30 UTC. **Research candidate may be retained with an explicit manufacturing gate; NOT fabrication/power approval.** No native source changes, no fabrication files, no hardware action and no publishing performed by this review.

## Exact scope and identity

Inspected current parent `hardware/imu_j107_clock_native_0405/native/mainboard_revD.kicad_pcb` SHA256 `d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22` and materialized candidate `hardware/pressure_joint_native_0433/native/mainboard_revD.kicad_pcb` SHA256 `69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc`. Proposal manifest: `ab0e1c38c3319afe962bed6a646323ca3949368b58c2d72dad022eb5829561d6`.

Embedded `schematic/controls_sccb.kicad_sch` and PCB both specify **SN74AXC4T245PWR**, not merely generic AXC4. Footprint `Package_SO:TSSOP-16_4.4x5mm_P0.65mm`; F.Cu pose (6,56), -90 degrees. Sixteen perimeter pads only, no central exposed-pad land. Exact source excerpt and pad geometry are in evidence.json.

## Primary TI evidence (official, accessed 2026-10-30)

[SN74AXC4T245 Rev B datasheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), physical PDF pages 4, 26, 38–40 (zero-based 3,25,37–39): PWR maps to PW TSSOP16. PW0016A drawing 4220204/B, 12/2023, shows peripheral gull-wing leads, molded body and no exposed central thermal pad. The BQB version instead explicitly has a thermal pad; its pad rules must not be transferred to PW. Body dimensions are 4.3–4.5 × 4.9–5.1 mm; pitch 0.65 mm; overall lead span 6.2–6.6 mm; height maximum 1.2 mm; body stand-off 0.05–0.15 mm. Lead width is 0.17–0.30 mm. The land/stencil examples contain only 16 peripheral lands; mask tolerances and stencil recommendations depend on fabrication/assembly site. These drawings do not authorize arbitrary underbody holes or guarantee an insulating coating process. This is a package-geometry conclusion, not a claim that internal leadframe metal does not exist.

The official PDF was downloaded to /tmp only and page38 visually inspected; it is not republished in this review.

## Native geometry and mask findings

Target via UUID `0fc7939c-7219-5bda-a92f-ff54d751526f`: GND, (5.4,55), copper diameter0.60mm, drill0.30mm, F–B through. U203 nominal molded-body projection is x3.5–8.5, y53.8–58.2; entire via disk lies inside that projection, not just within courtyard. It does **not** intersect the specified exposed lead/pad region. Even using the minimum body rectangle4.3×4.9, the disk is0.85mm inside its nearest edge; this is an XY placement observation, not a vertical stand-off safety guarantee.

Independent native polygon check uses 50nm ERROR_OUTSIDE pad conversion and tests every pad on each actual copper layer, including same-net/opposite-face pads. Zero copper-disk or drill-to-pad intersections. Closest U203 pad5: copper-disk edge gap **0.8374158mm**, drill edge gap0.9874158mm. A conservative bounding-box clearance to the upper pad row is0.825mm. There is no known central exposed-metal-base collision requiring hard rejection for this exact PW package.

**Opposite face matters:** closest pad of the entire board is R222.1 on B.Cu, copper gap **0.2254005mm**, drill gap0.3754005mm. R222 is at(6,56),0degrees. Its B.Courtyard begins y55.27; via disk reaches55.30, penetrating courtyard by0.03mm. Author physical.json reports overlap area0.004035077103mm². Independent nominal B.Fab lower body edge is55.5875, so disk-to-nominal-body separation0.2875mm. This is a real assembly-clearance gate despite no pad/body intersection; courtyard overlap is neither silently waived nor automatically treated as metal short. Purchased resistor body/termination tolerances, solder fillet and placement tolerance remain unqualified.

Actual target via front/back tenting modes are both0 = FROM_RULES, no local soldermask margin override. Native board setup explicitly `(tenting front back)` and both board settings are true. KiCad9.0.2 reports `IsTented(F.Mask)=true`, `IsTented(B.Mask)=true`, `HasSolderMask()=false`. These are actual design/effective settings—not an inference that all vias everywhere are tented. U203's16pads explicitly have F.Cu/F.Mask/F.Paste; no central paste land exists. Final manufacturing Gerber interpretation and fabrication reality were not verified here. No resin-fill/capping process is specified by these flags; tenting is not filling.

## Open manufacturing gates / decision limits

1. Fabricator must accept this exact0.30mm drilled through-via under a low-stand-off TSSOP and adjacent opposite-face resistor courtyard, with defined mask registration, tent durability, hole finishing and inspection. Obtain a controlled process requirement, not a verbal generic 'vias tented'.
2. With no qualified resin fill, an underbody hole can retain residues/contaminants; broken or unreliable tenting can leave exposed annulus/hole and create solder/cleaning risks. These are process risks to evaluate, **not evidence of a currently proven short or automatic need for resin fill in every case**. Stand-off is small; mask buildup, uneven topography, reflow and placement tolerances need assembly review.
3. Maintain no paste aperture over this via; verify final masks/paste/drill registration and opposite-side solder fillets. No exemption or enlarged mask opening has been introduced. Resolve R222 courtyard overlap or explicitly qualify it with the assembler before manufacturing.
4. Package substitution, pose change, different via size/location, different mask policy or native revision invalidates this conclusion. All unrelated whole-pen gates, including JP301 OPEN and unknown-camera NOPOWER, remain unchanged.

This check therefore removes an unsupported **blanket hard-reject solely because U203 body overlaps**. It does not remove the underbody-via/R222 assembly gate and does not qualify the design for production. Electrical native DRC/route completeness are owned by the candidate author; this read-only check is not a substitute for those tests.

## Replay

`XDG_CONFIG_HOME=/tmp/u203-kicad /usr/bin/python3 docs/electronics/u203_underbody_via_review_0436/inspect.py`

Script only loads native source and writes evidence/log in this isolated review directory. Candidate SHA is guarded. Distances are nominal polygon geometry, not fabrication tolerances. Keep this report linked to the candidate manifest; do not treat it as a source patch.
