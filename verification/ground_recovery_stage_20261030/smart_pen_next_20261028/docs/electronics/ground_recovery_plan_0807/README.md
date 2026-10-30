# 32 isolated grounds — bounded group planning, 2026-10-30

**NOFAB / NOPOWER.** Parent input: frozen0745 PCB `3276f04433c8ee3759f963fdc133200aee0b398ec6009e31a82fd595ab2f4328`. Its actual physical ground graph was recomputed:71-core pads +32 singleton pads=103. The earlier `camera_control_remaining_plan_20261030/inventory.json` describes0628 (70-core/102 total), so only its named targets/source inventory was reused; old counts were not blindly carried forward.

## Selection and scope

**Authoritative selected geometry: `selected20_final.json`**, SHA `0eff8ad9adbcb5ad77e16f09ebf352cf72d478f4f64df8eed1aacfd687159274`. Parent authorized it as a separate experimental native in `hardware/ground_recovery_native_0818`; that directory contains final native, real checks,20 cuts,backout,replay and manifests. This planning folder retains earlier scratch evidence, NOT multiple approved fabrication boards.

Twenty grounds are selected as one coherent reviewable group, with28 added copper objects /6 through vias. All old source, footprint positions, copper, AON/SENS connectivity and Schmitt region remain unchanged. Only ground is added; no resistor signal-side bias stubs, camera power/control source or NC outputs are connected.

- R216.2; R214.2
- R224.2,R228.2; R230.2,R231.2
- R225.2,R226.2,R227.2,R220.2,R206.2
- R233.2,R234.2,R232.2
- R221.2,R222.2,J104.3,R223.2
- R235.2,R237.2

**Remaining12 isolated grounds** are explicitly NOT part of this version:
1. R104.2 (GPIO45 strap ground): source need is important, but new ground copper in the RF end requires separate RF/installation review. First local via(4.926,1.099) and improved finite candidate(5.425,1.7) are historical planning only, neither applied. Actual nearby L101 RF_MATCH_TBD, C106/C107 DNP tuning and AE101 STUDY_NOFAB make rule-area clearance insufficient to declare RF impact closed. See existing `docs/research/rf_path_qualification` and actual later `hardware/rf_feed_conditional_candidate` evidence; do not confuse the old RF study geometry with current0745 placement. The20-group has no new copper in this end.
2. J202.1/.4/.7/.10/.13/.17: separate `docs/electronics/j202_ground_plan_0807`, manifest `783a519b0579166b75ea2ce88f9cc35d3829b8554985bc52aaed2461c3df51dd`. Its six tail-side traces/vias produce scratch0/90, GND77/103, but only20µm extra courtyard and35µm extra board-edge margin. It is not merged here or called robust fabrication layout.
3. R229.2,R218.2,R219.2,J105.2,J107.3: no clear route was found inside the declared bounded local candidate set. Model rows retain tested-candidate counts/rejection evidence. This is a local search blocker, not proof global routing impossible. J105/J107 also retain ADC/USB-interface/mechanical context; do not solve them by changing source or extending an arbitrary long ground branch.

## Bounded alternatives and refinement

1. Initial same-net reuse-first topology: nearest reachable core copper anchors within3mm, new via radial offsets≤1.7mm, F/B0.3mm ground traces,0.45/0.2mm through vias; no old removals/relocation.21 of26 non-J202 pads passed actual scratch0/75/0/GND92/103.10vias/13courtyard overlaps. Retained under `attempt1`.
2. Same exact bounded windows, prioritizing avoidance of courtyard intersections rather than merely shortest length: same21 pads,8vias/3courtyard overlaps, real scratch0/75/0 and no retained signal reference loss. `model.json`/`scratch_result.json` preserve this intermediate evidence.
3. ExcludeRF R104, then only local clearance refinements, not a third board-wide search: move R234 via(8.325,51.75)→(8.325,51.9), move shared J104 via(9.399,57.201)→(9.35,57.25), replace R225's proposed U202-body via by a B-side dogleg into the proposed R220 ground branch at(2.84,44.1). These eliminate the TSSOP-body and resistor-courtyard process assumptions, reduce to6vias, and keep only J104 probe-envelope overlap. All changes pass finite multilayer/pad checks before native fill.

The final native actually verifies0DRC/76unconnected/0parity, GND91/103, AON41/41,SENS12/12, no old signal additional reference projection loss. It does not complete the board. Historical clock/CAM_ON reference losses, all unqualified dynamic/thermal/charge/DFM gates remain.

## Reuse / negative design / mechanical budget

All old same-net copper is retained. Short paths reuse actual core vias/pads (not merely geometrically nearby presumed ground). R228 shares R224's core path, R206 shares R226's via, R223 shares J104's via, and R225 now shares R220's branch. These dependencies are declared before negative tests: cutting each shared trunk must expose the expected two-pad loss, not be silently treated as a one-pad test. Full actual20-cut results are in native0818.

No vias overlap actual pads on any copper layer, including same-net ground pads. New0.45/0.2mm vias use real through-layer and drill clearance checks. Final J104.3 circular1mm probe pad-to-via copper gap is0.194239mm; no copper obstruction/short. Its larger NoPaste footprint access rectangle is not a fitted connector body: fixture tip/positioning tolerance, enclosure access, soldermask expansion and tenting remain open.

Board native outline remains x0..14mm, y−6.5..95mm (14×101.5mm). No board/shaft dimensions, old footprints or3D assembly altered. No claimed hand-grip/diameter/enclosure qualification. New-copper operations stay outside the protected U205/C209 local area. Actual source/FP immutability and reference/negative results are in native0818, not inferred from a distance plot.

## Reproduction boundaries

`plan_ground.py` is a bounded search diagnostic, not an imported library; run only in an independent working copy. Its temporary-object diagnostic UUIDs can vary. Native reconstruction consumes the frozen explicit final geometry JSON and checks its hash; it does not rerun a historical planner in place. `refine_clearance.py` and `refine_r225.py` document the deterministic local geometric refinements. `test_scratch.py` and `test_selected20.py` preserve pre-final scratch evidence; do not mistake their intermediate boards for final0818.

Only the final native is proposed for independent review. No GitHub publication, power, purchase, bridging, eFuse change or firmware-provider change performed here.
