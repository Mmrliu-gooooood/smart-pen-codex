from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for s in ['verify','physical','negative','raw_delta','replay_rollback']:
 if (D/(s+'.json')).read_bytes()!=(D/(s+'_optimized.json')).read_bytes():raise RuntimeError('normal/O '+s)
if sha(D/'native/mainboard_revD.kicad_pcb')!='a14b30138f9f74ddbfb28bd20872160a1e83b96c1ed4da91d2805589050f97f4':raise RuntimeError('candidate')
if sha(D.parent/'ground_local_native_0920/native/mainboard_revD.kicad_pcb')!='ff70d9171b364e2d89ce13d109f22a2362afe76c340d384e194fb541bed6af8a':raise RuntimeError('accepted parent unchanged')
deps=[R/'hardware/translator_domain_candidate_0130/finite_copper.py',R/'hardware/translator_domain_candidate_0130/native_polygon.py',R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c',D.parent/'ground_local_native_0920/manifest.json',R.parent/'assembly_clearance_candidate_20261030_0921/tail100/manifest.json']
(D/'dependencies.json').write_text(json.dumps({str(f.relative_to(R.parent)):sha(f)for f in deps},indent=2)+'\n')
files=['README.md','selected_final.json','materialize.py','materialization.json','run_checks.py','cli_results.json','verify.py','geometry_native.py','physical.py','negative.py','replay_rollback.py','raw_delta.py','render.py','freeze.py','dependencies.json','native_forward.patch','rollback_drc.json','reference_diagnostic.json','group_views.png','group_views.svg']
for s in ['verify','physical','negative','raw_delta','replay_rollback']:files.extend([s+'.json',s+'_optimized.json'])
files.extend(str(f.relative_to(D))for folder in ['native','checks']for f in (D/folder).rglob('*')if f.is_file())
files.extend(str(f.relative_to(D))for f in (D/'negative_cuts').glob('*/drc.json'))
(D/'manifest.json').write_text(json.dumps({'status':'FROZEN_LIMITED_STATIC_CANDIDATE_NOT_ACCEPTED_REPLACEMENT_NOFAB_NOPOWER','open_reference_gate':'Explicit unchanged-track sliver and modified-route absolute/union reference deltas require independent classification; no zero loss claim','upload_policy':'Explicit allowlist only. Exploratory/rejected intermediates and broken negative native boards excluded; no automatic remote upload authority.','files':{f:sha(D/f)for f in sorted(files)}},indent=2)+'\n');print(sha(D/'manifest.json'),len(files))
