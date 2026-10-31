from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;W=O.parent;H=W/'reconstruction_xclk_20261031_0420';q=H/'review_manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(q)!='0ba3a0539862daf77518f67fa338da8d697c0ff2f21a9dfc1f90145ee277bc54':raise RuntimeError('author manifest')
j=json.load(open(q));files=j['files']
if len(files)!=200:raise RuntimeError('200 allowlisted files')
for item in files:
 rel=item['path']
 p=H/rel
 if sha(p)!=item['sha256']or p.stat().st_size!=item['bytes']:raise RuntimeError('author artifact '+rel)
expected='6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08'
if sha(H/j['native'])!=expected or sha(O/'selected_native.kicad_pcb')!=expected:raise RuntimeError('selected local/author PCB')
(O/'author_binding.json').write_text(json.dumps({'author_manifest_sha256':sha(q),'author_files_verified':200,'exact_selected_native_sha256':expected,'local_snapshot_matches_author':True,'functional_scope':'NEW 5f-based two XCLK joins; no pose changes; bounded SCCB and IO_EN replacements; clock/PDN/reference/process gates remain','independent_electrical_review_pending':True,'NOFAB':True,'NO_POWER':True,'no_remote_action_authorized_or_performed':True},indent=2)+'\n')
