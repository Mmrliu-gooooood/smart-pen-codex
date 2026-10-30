from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for n in ['verify','physical','raw_delta','replay','negative']:
 a=D/(n+'_result.json');b=D/(n+'_optimized.json');json.loads(a.read_text());json.loads(b.read_text())
 if a.read_bytes()!=b.read_bytes():raise RuntimeError('normal/O '+n)
for n in ['reference_classification','reference_interaction','pre_via_reference','source_check']:
 a=D/(n+'.json');b=D/(n+'_optimized.json');json.loads(a.read_text());json.loads(b.read_text())
 if a.read_bytes()!=b.read_bytes():raise RuntimeError('normal/O '+n)
if sha(D/'native/mainboard_revD.kicad_pcb')!='4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad':raise RuntimeError('exact candidate')
if sha(D.parent/'sccb_local_reference_1216/native/mainboard_revD.kicad_pcb')!='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697':raise RuntimeError('accepted parent unchanged')
deps=[D.parent/'sccb_local_reference_1216/manifest.json',D.parent/'translator_domain_candidate_0130/finite_copper.py',D.parent/'translator_domain_candidate_0130/native_polygon.py',R/'docs/electronics/camera_safeoff_addendum_0719/sources/axc8.pdf',R.parent/'assembly_dvp_route_masks_20261030_1228/route_masks_y20_38.json',R.parent/'assembly_bias_pose_screen_20261030_1241/geometry_results.json',R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c']
(D/'dependencies.json').write_text(json.dumps({str(f.relative_to(R.parent)):sha(f)for f in deps},indent=2)+'\n')
files=['README.md','selected_final.json','materialization.json','materialize.py','run_checks.py','cli_results.json','verify.py','physical.py','geometry_native.py','installation_obstacles.json','raw_delta.py','replay_rollback.py','negative.py','cut_one.py','source_roles.json','source_check.py','source_check.json','source_check_optimized.json','reference_diagnostic.json','reference_classification.py','reference_classification.json','reference_classification_optimized.json','reference_interaction.py','reference_interaction.json','reference_interaction_optimized.json','pre_via_reference.py','pre_via_reference.json','pre_via_reference_optimized.json','native_forward.patch','rollback_drc.json','render.py','group_views.png','group_views.svg','dependencies.json','freeze.py']
for n in ['verify','physical','raw_delta','replay','negative']:files +=[n+'_result.json',n+'_optimized.json']
files +=[str(f.relative_to(D))for folder in ['native','checks']for f in(D/folder).rglob('*')if f.is_file()]
if len(files)!=len(set(files)):raise RuntimeError('duplicate allowlist')
for f in files:
 if not(D/f).is_file():raise RuntimeError('missing '+f)
(D/'manifest.json').write_text(json.dumps({'status':'FROZEN_DATA8_BIAS_RELOCATION_STATIC_CANDIDATE_PENDING_JOINT_REVIEW_NOFAB_NOPOWER','scope':'Eight existing U201 A-port100k bias branches; two passive moves and GND rebuild; actual new mutual-via reference/load/timing and intended-own-courtyard escape exceptions explicitly disclosed, not product qualification.','upload_policy':'Explicit candidate allowlist only, no automatic remote authority. Excludes incomplete planners, trial-native boards, negative-cut natives and counterfactual natives. Frozen publications unchanged.','files':{f:sha(D/f)for f in sorted(files)}},indent=2)+'\n');print(sha(D/'manifest.json'),len(files))
