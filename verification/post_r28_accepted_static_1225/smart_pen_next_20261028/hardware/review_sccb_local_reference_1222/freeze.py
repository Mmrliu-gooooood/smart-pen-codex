from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name in ['verify','physical','replay','negative']:
 if (D/(name+'_result.json')).read_bytes()!=(D/(name+'_optimized.json')).read_bytes():raise RuntimeError('normal/O '+name)
if (D/'local_repair_delta.json').read_bytes()!=(D/'local_repair_delta_optimized.json').read_bytes():raise RuntimeError('normal/O local delta')
if (D/'reference_classification.json').read_bytes()!=(D/'reference_classification_optimized.json').read_bytes():raise RuntimeError('normal/O reference')
if sha(D/'native/mainboard_revD.kicad_pcb')!='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697':raise RuntimeError('candidate hash')
if sha(D.parent/'control_envelope_native_1051/native/mainboard_revD.kicad_pcb')!='8312b1d5ec56f0ab4c396cba2b78449e191f06225bf9aa64ea6522fd1c3c68bb':raise RuntimeError('parent hash')
files=['render.py','group_views.png','group_views.svg','local_repair_delta.py','local_repair_delta.json','local_repair_delta_optimized.json','README.md','selected_final.json','materialization.json','materialize.py','run_checks.py','cli_results.json','verify.py','physical.py','geometry_native.py','installation_obstacles.json','reference_classification.py','reference_classification.json','reference_classification_optimized.json','reference_diagnostic.json','negative.py','cut_one.py','replay_rollback.py','native_forward.patch','rollback_drc.json','freeze.py']
for name in ['verify','physical','replay','negative']:files.extend([name+'_result.json',name+'_optimized.json'])
files.extend(str(f.relative_to(D))for folder in ['native','checks']for f in (D/folder).rglob('*')if f.is_file())
for f in files:
 if not(D/f).is_file():raise RuntimeError('missing '+f)
(D/'manifest.json').write_text(json.dumps({'status':'FROZEN_LOCAL_SCCB_REPAIR_PENDING_JOINT_REVIEW_NOFAB_NOPOWER','upload_policy':'Candidate NOT validated release. No automatic remote upload authority. Explicit diagnostic allowlist; failed exploratory native boards and negative cut native boards excluded.','files':{f:sha(D/f)for f in sorted(files)}},indent=2)+'\n');print(sha(D/'manifest.json'),len(files))
