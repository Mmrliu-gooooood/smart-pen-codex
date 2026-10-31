from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
if (D/'review_manifest.json').exists():raise RuntimeError('already frozen')
files=set()
for dirname in ['native','final_candidate']:
 for f in (D/dirname).rglob('*'):
  if f.is_file()and(f.suffix in['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_dru','.kicad_sym','.kicad_mod']or f.name in['sym-lib-table','fp-lib-table']):files.add(f)
for n in ['finite_copper.py','native_polygon.py','source_netlist.xml']:files.add(D/'review_dependencies'/n)
for n in ['README.md','CONTRACT.md','RUN_CHECKS.md','verify_manifest.py','freeze_review.py','verify_final.py','finite_final.py','geometry_native.py','source_roles.py','anchor_policy.py','anchor_regression_final.py','native_contract_final.py','fill_one.py','negatives_final.py','saved_cut.py','native_blocks.py','reference_final.py','reference_check.py','plane_islands_final.py','newpaths_final.py','plane_delta_final.py','path_geometry.py','collinear_screen.py','aggregate_checks.py','restore_final_options.py','proposed_full104.json','proposed_obstacles.json','pose_overlay_authoritative.json','joint_prefilter.json','final_verification.json','final_verification_optimized.json','finite_final.json','finite_final_optimized.json','source_roles.json','source_roles_optimized.json','anchor_regression.json','anchor_regression_optimized.json','final_drc.json','final_fill_reload.json','final_native_contract.json','final_reference.json','plane_islands_final.json','newpaths_final.json','plane_delta_final.json','path_geometry.json','collinear_screen.json','aggregate_checks.json','restoration_comparison.json','final_restore_R219_drc.json','final_restore_C104_drc.json','source_margin_trial.json','source_margin_reference.json','reference_a771.json']:
 files.add(D/n)
for f in(D/'final_validation').iterdir():
 if f.is_file()and(f.suffix in['.json','.ndiff']):files.add(f)
rows=[]
for f in sorted(files):
 if not f.is_file():raise RuntimeError(str(f))
 rows.append({'path':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
r={'status':'FROZEN_SCOPED_STATIC_CANDIDATE_FOR_INDEPENDENT_REVIEW','native':'final_candidate/mainboard_revD.kicad_pcb','native_sha256':'d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b','parent_sha256':'c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855','actual_drc':[0,45,0],'scope':'PCLK+HREF four closures only; VSYNC unresolved. Real In2/AON/C104return/source-reference exceptions retained. NOFAB/NOPOWER/providerNULL/JP201JP202JP301OPEN. Not SI/PDN/assembly/operation acceptance.','files':rows,'excluded':'All rejected/planning/native-cut trial boards, failed materializer partials, UI prl, stale copied native reports, caches and unselected routing scripts. Labeled negative/comparison report evidence and regeneration scripts included; no rejected board silently bundled as candidate.','independent_advisory':{'path':'../independent_receive_pair_advisory_20261031_0303/manifest.json','sha256':'1d0e123f782d343a62fac865655a31a81dbede2ef9288198839b01d7a93f8071'},'mechanics_pending_binding':'../reconstruction_receive_margin_mechanics_20261031_0305'}
(D/'review_manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(len(rows),hashlib.sha256((D/'review_manifest.json').read_bytes()).hexdigest())
