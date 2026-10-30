from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for s in ['verify','physical','negative','raw_delta','replay_rollback','reference_closure']:
 if (D/(s+'.json')).read_bytes()!=(D/(s+'_optimized.json')).read_bytes():raise RuntimeError('normal/O '+s)
if sha(D/'native/mainboard_revD.kicad_pcb')!='8684d20fa449402ab1309b9af17d1cb64e0e6c4935532a36febaf362b0060f09':raise RuntimeError('candidate')
if sha(D.parent/'tail100_routing_native_0927/native/mainboard_revD.kicad_pcb')!='a14b30138f9f74ddbfb28bd20872160a1e83b96c1ed4da91d2805589050f97f4':raise RuntimeError('frozen parent unchanged')
deps=[R/'hardware/translator_domain_candidate_0130/finite_copper.py',R/'hardware/translator_domain_candidate_0130/native_polygon.py',R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c',D.parent/'tail100_routing_native_0927/manifest.json',D.parent/'review_tail100_independent_0947/clock_reference_localization.json',D.parent/'review_tail100_independent_0947/reference_counterfactual_AON_I2C_SDA.json',R.parent/'assembly_tail_courtyard_review_20261030_1000/manifest.json']
(D/'dependencies.json').write_text(json.dumps({str(f.relative_to(R.parent)):sha(f)for f in deps},indent=2)+'\n')
files=['README.md','selected_final.json','materialize.py','materialization.json','run_checks.py','cli_results.json','verify.py','geometry_native.py','physical.py','negative.py','replay_rollback.py','raw_delta.py','reference_closure.py','render.py','freeze.py','dependencies.json','native_forward.patch','rollback_drc.json','reference_diagnostic.json','group_views.png','group_views.svg']
for s in ['verify','physical','negative','raw_delta','replay_rollback','reference_closure']:files.extend([s+'.json',s+'_optimized.json'])
files.extend(str(f.relative_to(D))for folder in ['native','checks']for f in (D/folder).rglob('*')if f.is_file())
files.extend(str(f.relative_to(D))for f in (D/'negative_cuts').glob('*/drc.json'))
(D/'manifest.json').write_text(json.dumps({'status':'FROZEN_COURTYARD_ESCAPE_CANDIDATE_PENDING_INDEPENDENT_REVIEW_NOFAB_NOPOWER','scope':'All physical net partitions preserved; moved vias clear all native courtyards/full J202 projection; exact reviewed clock gap avoided; no global manufacturing/dynamic/SI approval','upload_policy':'Explicit allowlist only. Exploratory/rejected intermediates and broken negative native boards excluded; no automatic remote upload authority.','files':{f:sha(D/f)for f in sorted(files)}},indent=2)+'\n');print(sha(D/'manifest.json'),len(files))
