from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for stem in ['verify','physical','negative','replay_rollback','raw_delta']:
 if (D/(stem+'.json')).read_bytes()!=(D/(stem+'_optimized.json')).read_bytes():raise RuntimeError('normal/-O '+stem)
if sha(D/'native/mainboard_revD.kicad_pcb')!='ff70d9171b364e2d89ce13d109f22a2362afe76c340d384e194fb541bed6af8a':raise RuntimeError('candidate SHA')
if sha(D.parent/'ground_recovery_native_0818/native/mainboard_revD.kicad_pcb')!='abd8a388a606582e80ebe5f59da7579f7020cd44be6af494e032b8f69fde8ca0':raise RuntimeError('parent changed')
deps=[R/'hardware/translator_domain_candidate_0130/finite_copper.py',R/'hardware/translator_domain_candidate_0130/native_polygon.py',R/'hardware/camera_schmitt_source_0744/handoff.json',R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c',D.parent/'ground_recovery_native_0818/manifest.json']
(D/'dependencies.json').write_text(json.dumps({str(f.relative_to(R.parent)):sha(f)for f in deps},indent=2)+'\n')
files=['README.md','selected_final.json','materialize.py','materialization.json','run_checks.py','cli_results.json','verify.py','geometry_native.py','physical.py','negative.py','replay_rollback.py','raw_delta.py','render.py','freeze.py','dependencies.json','native_forward.patch','rollback_drc.json','negative_drc.json','group_views.png','group_views.svg']
for stem in ['verify','physical','negative','replay_rollback','raw_delta']:
 files.extend([stem+'.json',stem+'_optimized.json'])
files.extend(str(f.relative_to(D))for folder in ['native','checks']for f in (D/folder).rglob('*')if f.is_file())
(D/'manifest.json').write_text(json.dumps({'status':'LOCAL_VALIDATED_STATIC_CANDIDATE_PENDING_INDEPENDENT_REVIEW_NOFAB_NOPOWER','upload_policy':'Explicit allowlist only; rejected_wrong_pad_layer, search/alternate/negative specimens excluded. No automatic remote upload authorization.','files':{f:sha(D/f)for f in sorted(files)}},indent=2)+'\n');print(sha(D/'manifest.json'),len(files))
