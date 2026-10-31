from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;W=O.parent;H=W/'reconstruction_u101_joint_20261031_0051';q=H/'review_manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(q)!='6ce9c2ccaadcf72af7f66c0440df2fbc48fda11af76a80334cf4b55d938b2df4':raise RuntimeError('author manifest')
j=json.load(open(q));files=j['files']
if len(files)!=169:raise RuntimeError('169 allowlisted files')
for rel,item in files.items():
 p=H/rel
 if sha(p)!=item['sha256']or p.stat().st_size!=item['bytes']:raise RuntimeError('author artifact '+rel)
expected='f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71'
if sha(H/j['native_path'])!=expected or sha(O/'selected_native.kicad_pcb')!=expected:raise RuntimeError('selected local/author PCB')
(O/'author_binding.json').write_text(json.dumps({'author_manifest_sha256':sha(q),'author_files_verified':169,'exact_selected_native_sha256':expected,'local_snapshot_matches_author':True,'functional_scope':'NEW 4d7d-based eight MCU data closures; receive/SCCB remain open; not lost historical51','independent_electrical_review_pending':True,'NOFAB':True,'NO_POWER':True,'no_remote_action_authorized_or_performed':True},indent=2)+'\n')
