# Reproduce in a NEW independent writable mirror

Verify `review_manifest.json` with `verify_manifest.py` before running output-writing scripts. Never rerun inside frozen originals. Use KiCad9.0.2 `/usr/bin/python3`; configure XDG config/cache/data to writable temp directories.

- `verify_final.py` normal/-O:312 explicit native/physical gates, one declared old replacement, only VSYNC three-pad merge, unchanged power/poses/data/control and cores94/41/12.
- `finite_final.py` normal/-O: actual finite all-layer foreign copper/pad/drill/full104/keepout checks. `native_contract_final.py`: outlines/zone flags/stackup/project source exact.
- `source_roles.py`, `anchor_regression_final.py` normal/-O: source/native pin/domain/side roles and six actual PCB_TRACK-wrapped via fixtures.
- Native `kicad-cli pcb drc --all-track-errors --schematic-parity --format json -o final_drc.json final_candidate/mainboard_revD.kicad_pcb`:0/43/0.
- Copy final native+project to a separate directory, run `fill_one.py <copy>/mainboard_revD.kicad_pcb` normal then-O in fresh processes and compare exact bytes/hash.
- `negatives_final.py 0..2` normal/-O: MCU VSYNC, bias VSYNC and SENS_D6 terminal cuts; exact reversible raw native replay. `saved_cut.py 0..2` normal/-O produces clearly diagnostic copies; refill and run native DRC. Each1/44/0 with track_dangling. These intentionally rejected boards are not release candidate files.
- `reference_check.py`, `retained_reference_unions.py`, `plane_islands_final.py`, `newpaths_final.py`, `plane_delta_final.py`: reproduce explicit nonzero effects. Preserve Boolean operation order and overlap/precision disclosures rather than forcing zero.
- `path_geometry.py`, `collinear_screen.py`: planar centerline model/layer changes and exact collinearity screen, not time-domain qualification.
- `local_junction_prefilter/preflight.py`: one rejected in-memory local PCLK/VSYNC shortening proposal. Random new UUIDs can differ; compare actual geometry/conflict classes, not their generated UUID strings. It writes no candidate board and does not prove global impossibility.
- `aggregate_checks.py`:23 author result gates. Separate exact-bound mechanical and PDN/branch advisory packages still required. No manufacturing, PDN, capture or SI approval follows from this suite.

Output reports are overwritten only in the independent mirror. The original allowlisted native/reports are immutable. Rejected trial native boards, UI prl, stale reports and caches are excluded from backup allowlist; diagnostic reports and reproduction scripts are labeled explicitly.
