# DVP joint-placement mechanical screen — conditional incompatibilities, NOFAB

## Scope and identity

This isolated review does not modify any frozen mechanical/native design and does not upload anything. It reviews actual candidate PCB `../smart_pen_next_20261028/hardware/dvp_joint_native_candidate_1950/native/mainboard_revD.kicad_pcb`, SHA256 **184dce12e82219e5d4bb3e1f20f84cf2bc6e06c1494f5b23862f5e1978024f81**, not a selected finished board.

The parent analytic package `dvp_joint_feasibility_1942` manifest **5042728ce459c68277eade07a70fb5cecaa038937d01c6a0f9d7327ee4ec9d22** and all14 listed file hashes/sizes were checked. The actual native candidate matches the six-pose derivative of input7d197; its author retains source/parity/electrical checks separately.

Against accepted9a03, **29 references**, not33, change position/orientation/side. Four of the final six refs had already changed in the27-ref input. These29 refs map to32 existing mechanical envelope entities because J105 has2 terminals and J107 has3. J103/J106 remain unchanged in native board data. Eleven changed references are on B: R218/R219/R221/R222/R223/R225/R226/R227/R206/J105/J107. This screen does not omit the earlier B-side changes.

Exact old/new poses and original ACCESS envelopes are in `delta.json`; actual candidate-based transforms, dimensions, source hashes, and all collisions are in `screen_results_normal.json`.

## Main finding

**Do not pass the candidate against the current full installation-envelope contract.** There are real positive-volume intersections between retained modeled installation budgets and existing mechanical solids. However, the evidence does **not** establish unavoidable collision of the unknown real component bodies. Reducing a budget without selected part, solder, wire and assembly evidence is not an acceptable fix.

| Changed entity | Existing context / obstacle | Retained installation budget | Recomputed intersection |
|---|---|---|---|
| R206, B(9,47) | RevC, RevD bench, ACCESS19, ACCESS20 / right cassette housing | 2.45×.95mm pad/body XY union,1.45mm depth from B | .18103175385mm³ in every context |
| J107 pin2, B(1.5,83.9) | ACCESS19/20 / lower common-datum shell | 1.8×2.2mm XY solder/wire rectangle,2mm depth | .01981508530mm³ in each shell |
| R222, B(6,56) | RevD external bench only / cassette top collar | inherited2.45×.95×1.45mm budget | .55522627318mm³ |

The RevD collar is an external assembly/test fixture, **not** a product-shell obstruction. It still cannot silently inherit compatibility after this board change.

For the same retained XY budgets, first obstacle depths from B are .46479317633mm for R206, .41479317633mm for J107.2, and1.06479317633mm for the bench's R222. These are nominal geometry thresholds for this footprint projection, **not** approved component-height limits: they contain no solder/process/tolerance or electrical/thermal margin.

### Important body-versus-installation distinction

Independent smaller-shape sensitivities in `conflict_sensitivity.json` show:

- R206 as a hypothetical1.6×.8×.55mm box has no positive-volume housing intersection, while the retained2.45×.95mm XY budget at .55mm depth intersects .01565675385mm³. The conflict is not proof that the actual resistor body must hit; unknown solder fillet/stand-off and conservative pad/body union matter.
- J107.2 reduced to the copper-land1.4×1.8mm projection at2mm depth has no positive-volume intersection, while the retained1.8×2.2mm terminal budget does. **A copper footprint is not a complete solder joint, insulated wire, bend or strain-relief envelope.** No reduced terminal shape is selected here.
- Height sweeps reproduce collision onset at .465mm and .415mm respectively, consistent with the obstacle bounds. A deliberately separated R206 control yields0 collision. None of these scenarios changes an original design.

## What passed at this limited scope

- All29 changed refs are represented, including three IC rotations, six decoupling capacitor relocations, and all B-side changes. Exact pad-derived positions are used for J105/J107; J107 is not simply shifted from old x8.2 to an erroneous x3.9.
- Apart from the listed intersections, no changed retained envelope has another positive-volume overlap with the other modeled solids in these four static contexts. Peers are moved simultaneously before checking, so stale old positions are not treated as obstacles.
- J105 new B77.5 lands retain their2mm budget and have no static positive-volume collision in these contexts. This is not soldering-tool, wire routing, or safe ADC-front-end implementation approval.
- R225/226/227 and other changed resistors above the independent power budget have1.75mm nominal first-obstacle depth in the existing stack. The old1.45mm assumption leaves.30mm nominal geometric separation; previously reserved relative-stack uncertainty consumes part of this. Actual power parts, insulation thickness, thermal clearance, cell geometry and assembly variation are not qualified.
- Moved envelope radial maximum in ACCESS is7.77142451mm at R224/R228/R233. This is only those moved envelopes, not whole-product compliance. It does not approve OD19/20 against the user's15–18mm target or remove prior global stack/material margins.

## Height evidence and limits

`interfaces84_screen/extract.py` documents the inherited default passive body1.3mm + .15mm solder assumption, giving1.45mm. This is not a manufacturer maximum for R206/R225/R226/R227 or all other passives. The separate resistor-height contract includes R218/R221 and selected other refs at body maximum.55 + assumed .15mm solder = .70mm; it does not automatically qualify R206 or all100k resistors. Native generic KiCad STEP references are not supplier height evidence.

U201/U202/U203 inherited TSSOP envelope is package-bound1.2mm plus an assumed.15mm mounting allowance. Source mechanical envelope identities are retained and rotated; this review does not requalify package vendor tolerances or solder stand-off. Wirebank J105/J107 has no zero-height exception: its existing2mm terminal budget remains until an actual process envelope is justified.

The diagnostic `first_height_obstacles` list is a broad vertical projection query. At near-tangent freeform wire boundaries it may report zero-depth numerical contact despite no finite retained-budget collision; **do not use that list wholesale as a clearance certificate**. Reported limiting depths above are independently checked with finite positive-volume height sweeps. Full collision conclusions use finite native common volumes, with1e−7mm³ numerical reporting threshold, not a physical manufacturing tolerance.

## Recommended bounded response

1. Keep this candidate unselected and NOFAB. Resolve R206 and J107.2 installation conflicts before claiming mechanical compatibility. Either preserve established budgets and adjust the native placement under electrical constraints, or produce an explicit actual part/fillet/wire/assembly/tolerance envelope that supports a smaller model. Do not shave housing or zero the component height solely to pass.
2. If this board is used with the existing RevD bench, also update/recheck its top collar for R222. Do not confuse that bench-only change with the pen enclosure.
3. Re-run the complete final native-to-CAD mapping after any electrical relocation, along with support/copper contact and fastening/access checks. Current ACCESS uses unimplemented B70.5 contact-wire geometry, while this board correctly retains actual J103 B52; therefore this remains a research-context screen, not an assembled electrical/mechanical product variant.
4. Actual battery, camera/nose/FPC, wire routing and strain relief, solder tools, heat exposure, assembly motion, preload/creep, sweat/insulation and total cost remain outside this static envelope test. No passes here close these gates.

## Reproduce

`screen.py` reads exact accepted/candidate hashes and the four frozen native CAD contexts, transforms retained budgets into actual new poses in memory, and writes only this isolated review folder. It uses /usr/bin/python3, pcbnew, FreeCAD/OCC. `verify_conflicts.py` independently constructs the finite sensitivity shapes and checks collision/separation controls. No source CAD is saved or modified. `inspect.py` is the preliminary read-only six-delta reconstruction; the actual-candidate screen is authoritative. Source hashes are recorded; `verification.json` records normal/optimized comparison and post-run unchanged inputs.
