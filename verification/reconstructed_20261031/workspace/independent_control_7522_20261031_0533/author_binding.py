from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;W=O.parent;H=W/'reconstruction_control_service_20261031_0510';q=H/'review_manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(q)!='bec167d27945b9d4af03171fd7f0c457315ffc82333d178ececc6063f2f86614':raise RuntimeError('author manifest')
j=json.load(open(q));files=j['files']
if len(files)!=192:raise RuntimeError('192 allowlisted files')
for item in files:
 rel=item['path']
 p=H/rel
 if sha(p)!=item['sha256']or p.stat().st_size!=item['bytes']:raise RuntimeError('author artifact '+rel)
expected='7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1'
if sha(H/j['native'])!=expected or sha(O/'selected_native.kicad_pcb')!=expected:raise RuntimeError('selected local/author PCB')
(O/'author_binding.json').write_text(json.dumps({'author_manifest_sha256':sha(q),'author_files_verified':192,'exact_selected_native_sha256':expected,'local_snapshot_matches_author':True,'functional_scope':'NEW 688-based four RESET/PWDN MCU and service joins; no pose/old copper changes; J104 probe/tool/camera-off and electrical gates remain','independent_electrical_review_pending':True,'NOFAB':True,'NO_POWER':True,'no_remote_action_authorized_or_performed':True},indent=2)+'\n')
