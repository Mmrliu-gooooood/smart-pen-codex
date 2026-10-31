# Reproduce in a NEW writable review mirror

Do not execute output-writing scripts inside this frozen directory. Verify `review_manifest.json`, copy its allowlisted files to an independent directory, and run there with KiCad9.0.2 `/usr/bin/python3` and `kicad-cli`.

1. `verify_manifest.py` checks every hash/size. `verify_final.py` and `python -O verify_final.py` check312 native/physical contracts; `finite_final.py` in both modes checks whole finite copper/body geometry.
2. Run `source_roles.py`, `anchor_regression_final.py` in both modes; `native_contract_final.py`, `path_geometry.py`, `collinear_screen.py`.
3. `kicad-cli pcb drc --all-track-errors --schematic-parity --format json -o final_drc.json final_candidate/mainboard_revD.kicad_pcb` must produce0/45/0. Keep project/rules/schematic/footprints beside PCB.
4. Copy final_candidate to a fresh mirror, run `fill_one.py <mirror>/mainboard_revD.kicad_pcb` in separate normal and -O processes; compare exact bytes/hash to frozen native. Do not replace filled board with an unfilled template.
5. `reference_check.py`, `plane_islands_final.py`, `newpaths_final.py`, `plane_delta_final.py` reproduce the explicit nonzero reference/PDN measurements, not a zero-regression predicate.
6. `negatives_final.py 0..3` in normal/-O performs actual four terminal cuts against finite physical connectivity and checks exact reversible raw replay. `saved_cut.py 0..3` in both modes creates clearly diagnostic mirrors; refill each using `fill_one.py`, then native all-track/parity DRC. Each must be1/46/0 (cut0 via_dangling, cuts1..3 track_dangling). These rejected cut boards are test fixtures, not the candidate.
7. `restore_final_options.py` generates separately labeled diagnostic restoration variants, not candidates; after refill, R219 and C104 restoration DRC conflicts reproduce the selected-topology constraint. `restoration_comparison.json` records exact generated specimen hashes/reports.
8. `aggregate_checks.py` checks all author results. Separate independent mechanical and PDN advisory packages remain necessary; this script is not self-acceptance.

Some script outputs overwrite report files in the review mirror; preserve the frozen original hashes before running. Set XDG_CONFIG_HOME/CACHE_HOME/DATA_HOME to writable temporary directories; inherited read-only default KiCad directory warnings are not design evidence. Normal/-O tests do not rely on assert statements.

NOFAB / NO POWER. Static connectivity and nominal envelopes do not establish timing, real power sequence, loaded VOH, actual package process, installation/tool access or capture functionality.
