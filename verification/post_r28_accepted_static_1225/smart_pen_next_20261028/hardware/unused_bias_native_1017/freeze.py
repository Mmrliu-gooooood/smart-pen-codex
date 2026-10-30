from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for s in ['verify','physical','negative','raw_delta','replay_rollback','new_reference_hole','source_roles']:
 if (D/(s+'.json')).read_bytes()!=(D/(s+'_optimized.json')).read_bytes():raise RuntimeError('normal/O '+s)
if sha(D/'native/mainboard_revD.kicad_pcb')!='2a5400724239f11fe6f589c4f954441deea3c89b0659d1a6292062c99e3e0866':raise RuntimeError('candidate')
if sha(D.parent/'ground_pair_native_1007/native/mainboard_revD.kicad_pcb')!='6d05642f7d15ba10c22266e551d72b8457d703bd7328dca79ff5c1c50812b4d9':raise RuntimeError('accepted parent unchanged')
deps=[R/'hardware/translator_domain_candidate_0130/finite_copper.py',R/'hardware/translator_domain_candidate_0130/native_polygon.py',R/'docs/electronics/camera_safeoff_addendum_0719/sources/axc4.pdf',R/'docs/electronics/camera_safeoff_addendum_0719/sources_index.json',R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c',D.parent/'ground_pair_native_1007/manifest.json']
(D/'dependencies.json').write_text(json.dumps({str(f.relative_to(R.parent)):sha(f)for f in deps},indent=2)+'\n')
files=['README.md','selected_final.json','materialize.py','materialization.json','run_checks.py','cli_results.json','verify.py','geometry_native.py','physical.py','negative.py','cut_one.py','replay_rollback.py','raw_delta.py','new_reference_hole.py','source_roles.py','render.py','freeze.py','dependencies.json','native_forward.patch','rollback_drc.json','group_views.png','group_views.svg']
for s in ['verify','physical','negative','raw_delta','replay_rollback','new_reference_hole','source_roles']:files.extend([s+'.json',s+'_optimized.json'])
files.extend(str(f.relative_to(D))for folder in ['native','checks']for f in (D/folder).rglob('*')if f.is_file())
files.extend(str(f.relative_to(D))for f in (D/'negative_cuts').glob('*/drc.json'))
(D/'manifest.json').write_text(json.dumps({'status':'FROZEN_UNUSED_INPUT_BIAS_STATIC_CANDIDATE_PENDING_INDEPENDENT_REVIEW_NOFAB_NOPOWER','scope':'Fourteen tracks and one via connect existing R206/U202 and R207/U203 unused-input bias; old copper/FP/outline unchanged; own new-via reference hole disclosed','upload_policy':'Explicit allowlist only. Local exploratory/failed-runner diagnostics and broken native boards excluded; no automatic remote upload authority.','files':{f:sha(D/f)for f in sorted(files)}},indent=2)+'\n');print(sha(D/'manifest.json'),len(files))
