from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;W=O.parent;H=W/'reconstruction_receive6_20261031_0228';q=H/'review_manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(q)!='527e3d5cd76540a2d050843566cbb8d7d834c262b50f717a87653ccb6c7b44fb':raise RuntimeError('author manifest')
j=json.load(open(q));files=j['files']
if len(files)!=179:raise RuntimeError('179 allowlisted files')
for item in files:
 rel=item['path']
 p=H/rel
 if sha(p)!=item['sha256']or p.stat().st_size!=item['bytes']:raise RuntimeError('author artifact '+rel)
expected='d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b'
if sha(H/j['native'])!=expected or sha(O/'selected_native.kicad_pcb')!=expected:raise RuntimeError('selected local/author PCB')
(O/'author_binding.json').write_text(json.dumps({'author_manifest_sha256':sha(q),'author_files_verified':179,'exact_selected_native_sha256':expected,'local_snapshot_matches_author':True,'functional_scope':'NEW c698-based four PCLK/HREF closures; VSYNC stays open; two rigid passive moves; no missing historical recovery claim','independent_electrical_review_pending':True,'NOFAB':True,'NO_POWER':True,'no_remote_action_authorized_or_performed':True},indent=2)+'\n')
