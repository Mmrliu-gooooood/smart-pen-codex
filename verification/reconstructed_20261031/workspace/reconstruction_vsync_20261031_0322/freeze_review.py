from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
if (D/'review_manifest.json').exists():raise RuntimeError('already frozen')
files=set()
for dirname in ['native','final_candidate']:
 for f in(D/dirname).rglob('*'):
  if f.is_file()and(f.suffix in['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_dru','.kicad_sym','.kicad_mod']or f.name in['sym-lib-table','fp-lib-table']):files.add(f)
for f in(D/'review_dependencies/branch_supplement').iterdir():
 if f.is_file():files.add(f)
for n in ['finite_copper.py','native_polygon.py','source_netlist.xml']:files.add(D/'review_dependencies'/n)
for n in ['README.md','CONTRACT.md','RUN_CHECKS.md','verify_manifest.py','freeze_review.py','verify_final.py','finite_final.py','geometry_native.py','source_roles.py','anchor_policy.py','anchor_regression_final.py','native_contract_final.py','fill_one.py','negatives_final.py','saved_cut.py','native_blocks.py','reference_final.py','reference_check.py','retained_reference_unions.py','plane_islands_final.py','newpaths_final.py','plane_delta_final.py','path_geometry.py','collinear_screen.py','aggregate_checks.py','proposed_full104.json','proposed_obstacles.json','joint_prefilter.json','final_verification.json','final_verification_optimized.json','finite_final.json','finite_final_optimized.json','source_roles.json','source_roles_optimized.json','anchor_regression.json','anchor_regression_optimized.json','final_drc.json','final_fill_reload.json','final_native_contract.json','final_reference.json','retained_reference_unions.json','plane_islands_final.json','newpaths_final.json','plane_delta_final.json','path_geometry.json','collinear_screen.json','aggregate_checks.json','routing_comparison.json','source_refinement.json','source_refinement_east_rejected.json','mcu_first_unused_sink_via.json','local_junction_prefilter/preflight.py','local_junction_prefilter/results.json','advisory_dependencies.json']:
 files.add(D/n)
for f in(D/'final_validation').iterdir():
 if f.is_file()and f.suffix in['.json','.ndiff']:files.add(f)
rows=[]
for f in sorted(files):
 if not f.is_file():raise RuntimeError(str(f))
 rows.append({'path':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
r={'status':'FROZEN_BOUNDED_STATIC_RESEARCH_CANDIDATE_FOR_INDEPENDENT_REVIEW','native':'final_candidate/mainboard_revD.kicad_pcb','native_sha256':'5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433','parent_sha256':'d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b','actual_drc':[0,43,0],'scope':'Two VSYNC closures; one same-net SENS_D6 F fanout replacement. Explicit long bias arm/shared topology and real foreign-reference/nonlocal plane-fill penalties remain. No poses/PDN/USB modifications; unchanged power copper is not PDN equivalence. NOFAB/NOPOWER/providerNULL/JP201JP202JP301OPEN. Not SI/PDN/assembly/capture acceptance.','files':rows,'excluded':'All unselected/rejected/planning/cut native boards, failed partials, UI prl, stale reports/caches. Labeled negative/comparison/preflight reports and regeneration scripts included, not silently bundled as candidate PCB.','advisory_dependencies':json.loads((D/'advisory_dependencies.json').read_text()),'mechanics_pending_author_binding':'../reconstruction_vsync_refined_mechanics_20261031_0358'}
(D/'review_manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(len(rows),hashlib.sha256((D/'review_manifest.json').read_bytes()).hexdigest())
