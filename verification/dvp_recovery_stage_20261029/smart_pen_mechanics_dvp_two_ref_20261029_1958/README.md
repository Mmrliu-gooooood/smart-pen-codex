# Bounded two-reference mechanical successor screen — NOFAB

This is an isolated finite comparison, not a redesign of frozen PCB/CAD. Predecessor native184dce and all mechanical inputs remain unchanged. Exact retained installation envelopes are carried over from `../smart_pen_mechanics_dvp_joint_audit_20261029_1950`:

- R206: full2.45×.95mm XY pad/body union,1.45mm below B.
- J107: each1.8×2.2mm terminal projection,2mm below B, all three pads move together. No height or termination-budget shrink.
- Other27 reference changes remain simultaneously at184dce poses. J103/J106 remain fixed in the source board. RevD fixture's pre-existing R222 conflict is not repaired by this two-ref study.

Nine candidate positions were supplied by the electrical worker after its bounded pad/courtyard/copper screen:
R206 B(8,47), (9,45.5), (8,45.5), (7,47), (9,46).
J107 B origin(3.2,84), (3.7,84), (2.7,83.5), (2.7,84.5), unchanged180° orientation.

`screen.py` tests each against four independent actual CAD contexts: RevC/B52 cassette, RevD external bench/B52 cassette, ACCESS19 and ACCESS20 research shells (the latter retain unimplemented B70.5 contact wiring). It computes common volumes plus nearest actual OCC distances. Intentional contact of the mounted component's base to the mainboard is excluded from free-clearance minima. No other obstacles are silently removed. Finite collision-volume threshold1e−7mm³ is numerical, not a fabrication allowance.

`results.json` gives every candidate, collisions and nearest non-board obstacles; `selection.json` gives the resulting bounded choice and simultaneous check, if completed. A no-collision result is nominal only: source component and solder budgets, actual material/tolerance/thermal margins and assembly routes remain unqualified. The current board and ACCESS are still not a single selected whole-pen assembly because native J103 remains B52.

No procurement, hardware operation, external upload or manufacture approval is performed.

## Bounded choice and actual native verification

Among the supplied finite candidates, the least-displacement no-collision combination is:

- **R206 B(9,46),0°**: 1mm move from(9,47).
- **J107 B origin(3.2,84),180°**: .5mm move from(2.7,84). All three actual pads become(2.0,81.5), (2.0,83.9), (2.0,86.3).

This is not a proof of the globally smallest possible continuous displacement. Other untested intermediate positions are not evaluated.

The electrical worker materialized this combination at `../smart_pen_next_20261028/hardware/dvp_mechanical_clearance_successor_1957/native/mainboard_revD.kicad_pcb`, SHA **f92c7517b40466208d907d30b076ccd80d40bb3c298c162b40891f86b5070f19**. `check_native.py` independently compares all102 reference poses, footprint identities, values and pad/net/size/angle records with184dce. Exactly the two intended translations differ; J103/J106 and all other references remain unchanged. Copper/electrical DRC is the electrical worker's separate responsibility, not claimed by this mechanical check.

## Exact nominal gaps after simultaneous two-ref change

Both changes are applied simultaneously before testing every changed installation envelope against all other modeled entities:

| Context | R206 minimum non-board distance | J107 minimum non-board distance |
|---|---:|---:|
| RevC/B52 | .60274936893mm to M1.6 cross screw | .93000000000mm to R501 envelope |
| RevD external bench/B52 | .60274936893mm to same screw | .85000000000mm to Common_base |
| ACCESS19 research | .60274936893mm to same screw | .45000000000mm to lower shell |
| ACCESS20 research | .60274936893mm to same screw | .45000000000mm to lower shell |

R206 also has .60466933112mm to the independent power budget and .87941674360mm to the right cassette housing. These are geometric separations of retained budgets, not electrical isolation, thermal, printer or assembly tolerances. Real wire routing and solder/tool access have not been added or certified.

Normal and optimized combined results are identical. Six predecessor-restoration negative controls reproduce the R206 collision in all four contexts and the J107.2 collision in both ACCESS shells. All29 changed refs were checked again after applying the pair: **the RevD bench R222/top-collar overlap remains .55522627318mm³**; it is the only remaining changed-ref overlap in these contexts and is not removed or labelled acceptable.

The finite rejected directions remain in `results.json`: R206 x8 or x7 at y47 still collides; J107 y83.5 or84.5 at x2.7 still collides. R206(9,45.5)/(8,45.5) pass but move further and have smaller .30103986447mm minimum spacing; J107(3.7,84) passes with .93mm minimum spacing but moves further.

## Verification notes

An initial native identity diagnostic incorrectly compared Python SWIG proxy representations of LIB_ID, including transient memory addresses, and therefore falsely reported many changes. This audit checker was corrected to compare explicit library nickname and footprint item strings; `native_check_debug.log` retains that rejected diagnostic, while `native_identity.json`/`native_check.log` are the corrected result. No design change was made in response to the checker mistake.

Overall status: **bounded two-ref static envelope gate passed, whole pen NOFAB**. External bench R222, native B52 versus ACCESS B70.5 contact-harness inconsistency, all unknown real part/process/material envelopes and physical tests remain open.
