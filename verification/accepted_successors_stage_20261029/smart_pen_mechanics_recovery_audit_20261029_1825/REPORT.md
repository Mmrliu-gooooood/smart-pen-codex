# Mechanical recovery integration audit — NOFAB

Date: 2026-10-29. Independent read-only source/CAD audit after execution environment recovery. No frozen native, manifest, design, or source was modified. No upload or hardware operation.

## Result

The retained files are intact, but there is **no single current electrically implemented and mechanically assembly-qualified pen configuration**. Do not fabricate the ACCESS mechanical study by combining it with accepted electrical board 9a03.

Four manifests / **108 file members** independently matched their stored SHA-256 and byte counts. This is file-integrity evidence, not a new repetition of the author's 108 wire-tolerance geometry scenarios. Latest retained mechanical study is the J301 y92.3 placement prescreen; no later complete assembly was found in the mechanical workspace.

## Newly executed checks

The independent `audit.py` reads actual FreeCAD/OCC shapes and KiCad board data, not just historical report claims. `results.json` pins inputs and outputs.

1. Accepted board `../smart_pen_next_20261028/hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb` has exact SHA-256 9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038.
2. **Actual J103** is B.Cu, pad coordinates (3,52) and (5.4,52). Under the mechanical X = PCB x − 7 / Z = 127 − PCB y mapping these are (−4,75) and (−1.6,75). ACCESS's curved-wire bare main tails instead occupy Z roughly56.43–57.98, leading to proposed B70.5 endpoints. They are not actual 9a03 pads. The proposal also changes X, not only longitudinal position.
3. **Actual J301** pads remain y88.7, body Z38.3. The y92.3/Z34.7 local placement preview is not the accepted board. A valid placement prescreen does not reconnect its old supply/ground copper.
4. Both OD19/20 ACCESS native documents reopen with valid shapes and positive constituent solid volumes. The exact stored D1 shape equals an R1.175 ×67 cylinder in both Boolean-difference directions. Its continuous axial translation union (Z−68..67) has no positive-volume intersection above1e−7mm³ with remaining native objects. This applies only to the source's simplified cylinder, not a real refill shoulder/tip, elastic insertion, or optical nose.
5. Direct recomputation finds D1-to-slider distance0 and D1-to-compressed-grip distance approximately4.44e−16mm, while housing distance is .925mm. Zero common volume is **not positive fit clearance** or verified insertion force.
6. For both shells and both head-power termination X positions, recomputed straight corridor/frame common volume is **2.016mm³** for old Z37.2→28 and proposed Z33.6→28 corridor endpoints alike. The J301 move does not create this blocker, but does not solve it. These budget corridors are not actual selected wires.

## Version ledger and evidence

All paths below are relative to the shared workspace; read linked source descriptions together with their boundary conditions.

- [Selected ACCESS study](../smart_pen_mechanics_next_20261028/mechanical/compliant_retainer_longarc_0415/README.md), manifest145b0d14e94d4f9d9cefeb4cabedbf5521c383ecb5926625ecc60574942fddfc: 62 members. Nine additional parts, OD19/20 comparison, .83/.93board variants; not a complete pen or approved replacement of15–18mm target.
- [Independent prior ACCESS audit](../smart_pen_mechanics_next_20261028/mechanical/compliant_retainer_independent_audit_0500/), manifestcb42574ef87dbc2c015473169c5f633cae5b7e4e96a585f15d32de6b6eab6888: 17 members.
- [Refill-last study](../smart_pen_mechanics_next_20261028/mechanical/prewired_transfer_refill_last_0532/README.md), manifest40f25040bfb7d40d9885ae4776846f13f32dfe1b4e1e69b44e37b9e6c6b3feb6: 14 members. It supersedes the statement that no prewired transfer geometry has been tested, **not** the need for a real transfer fixture. Seven Y samples are not a continuous swept-volume proof. After that hypothetical transfer, source non-D1 objects are mathematically restored, not physically fastened by a demonstrated procedure.
- [J301 local preview](../smart_pen_mechanics_next_20261028/mechanical/j301_y92p3_prescreen_0728/README.md), manifestcd6cdd527446d3f7bbe61e16e134e1413481a29ab3b451a91a20c4e3db249e9c: 15 members. Preview board04980dd3… was not accepted electrical layout.

## Ordered next steps

1. **Freeze one electrical/mechanical interface contract first.** Either retain actual J103 B52 and design its actual short harness/assembly, or review a new native B70.5 land/filter/routing change. Do not silently choose the proposal. Record both pad positions, normals, allowed movement, mounting datums, selected wire, and filtration placement. The ongoing translator/DVP rearrangement requires a fresh full footprint-to-mechanics check before carrying over clearance claims.
2. **Resolve head-power routing as an actual wire assembly.** Select a bounded wire/current/insulation/termination model, then check bend/exit/tool paths around the front frame using the unchanged termination budget. Do not remove the frame or shrink envelopes merely to make a test pass. Camera head/optics remain missing actual constraints.
3. **Define and model the pre-solder/transfer process before claiming assembly readiness.** Support board, cassette and wire ends at their true common datums; protect bare tails and avoid using wires as positioning springs. Specify holding/release access, solder/inspection access, real strain relief, and all fastening order. Validate continuous or sufficiently bounded motion rather than only seven nominal positions. Include board-to-power and other harnesses currently absent.
4. **Close refill/contact mechanics with physical part data.** Actual refill dimensional envelope, interference/friction, material/compliance, insertion force, switch travel/overtravel, unloaded release and recalibration after insertion require measurement. Current zero contact gap cannot set printer tolerance or safe insertion force.
5. **Only then close full product gates:** camera/nose/FPC and nib datum; selected battery protection/fixing/isolation; USB fixing; retainer material/preload/creep and fastener strength; complete closure/sweat ingress; RF near-material effects; dimensional target and ≤380CNY per-unit all-in build cost. None is qualified by current native validity checks.

## Reproduction and limitations

Run `/usr/bin/python3 audit.py` in this separate audit folder. It writes only this audit's results. Requires installed pcbnew and FreeCAD Python modules. Source hash guards reject a changed accepted board; every manifest-listed member is checked before CAD operations. No ERC/DRC was rerun here, nor were all author's geometry regression suites rerun. This audit confirms retained identities, specific raw geometry/port facts, and integration gaps; it does not certify electrical safety, fit, physical manufacture, accuracy, fatigue or runtime.
