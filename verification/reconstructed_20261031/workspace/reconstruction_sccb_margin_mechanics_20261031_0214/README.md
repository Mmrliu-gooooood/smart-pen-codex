# NEW Oct31 SCCB mechanical screen — research only

Candidate PCB `c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855`, from actual NEW f27 parent `f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71`. This is not recovery of missing Oct30 files. Author manifest `dda378e90fc7819c452eeedb115e77baaaa8ce35685b3d2b5e2839969fea0e66` is frozen; all 153 allowlisted files independently hash/size verified. No electrical or production release implied.

## Reproducible scope
Run `/usr/bin/python3 screen.py`, `keepouts.py`, `checks.py`, `author_binding.py` from this directory or by absolute path; repeat with `-O`. Normal and optimized JSON outputs are byte-identical. Source inputs remain read-only. Full-envelope masks are byte-identical to frozen f27 full104 masks, retaining U101 7.5×7.5, heights, sides and uncertainties.

Native diff: 148 added tracks (97 exterior, 51 inner), 5 added through-vias; no old copper removed or changed. All 103 footprint/pad/net/pose contracts unchanged; 104 full installation entities and exact 14×99.8 outline/native thickness unchanged. All exterior finite widths and both faces of each via screened against full envelopes, conservative native Fab bounds and complete native courtyard polygons. Inner copper screened against board outline and applicable native prohibitions, not treated as exterior assembly obstruction.

No new nonterminal full-body/Fab projection. The only full/Fab intersections are .15 mm straight north terminal escapes from actual U101.44 (8.2,6.575) to (8.2,6.15), and U101.45 (7.8,6.575) to (7.8,6.0). Each full overlap is .057589514346 mm², Fab .027589514346 mm²; not a blanket target-body waiver. Three deliberate center-via body negatives detect intrusion.

Eight native rule areas remain unchanged from f27; all new applicable track/via prohibitions pass on actual six-layer stack. U101 embedded rule areas prohibit pours only, not tracks/vias. Deliberate native LIS2DW12 prohibition-center via is detected.

## Finite margins and ordinary courtyard projections
All five vias clear retained full envelopes and Fab. Four via/courtyard projections are explicitly retained:

| Via center (native mm) | Court | Area mm² | Full-envelope nominal gap mm |
|---|---|---:|---:|
| SCL (10.6,41.8) | R231 F | .009664624028 | .200000 |
| SDA (12,41.75) | R231 F | .0106729781265 | .240026880943 |
| SCL (11.425,68.625) | U301 B | .136847215938 | .200000 |
| SCL (11.275,13.15) | R112 F | .026323625338 | .150000 |

SDA via (11.35,12.55) has no courtyard projection. Twelve total courtyard intersections include eight U101 north-source track pieces. Exact rows preserve actual pad-end provenance. Ordinary courtyard-only copper is classified separately from full-body/Fab intrusion; it is not automatic manufacturer tenting, reflow, tool or service qualification. No arbitrary universal .2 mm courtyard keepout is introduced. Finite outside-outline checks pass; minimum new copper-to-outline gap 1.275 mm.

The earlier 58853 diagnostic had .025 mm full-envelope gaps at R231/U301; this candidate improves both to .2 mm. The earlier snapshot is retained separately, not rewritten as final.

## CAD applicability and open gates
No pose/outline changes relative to f27: exact saved four-context CAD derivative `reconstruction_saved_cad_f27_20261031_0156` retains valid nominal geometry/contacts. Its metadata binds f27, NOT this electrical successor. This package does not claim new CAD files or changed saved metadata. Saved source geometry retains .93 mm board thickness budget, support contacts, print tolerance caveats and all six unresolved operation/DNP gates: J104, J108, JP201, JP202, C106, C107. External RevD bench fixture is not the pen enclosure.

NOFAB / NO POWER. No unqualified cell. Two pens budget CNY760 unchanged. Static research only: assembly accessibility, mask/tenting process, tolerances, electrical loading/reference/timing and physical verification remain separate gates.
