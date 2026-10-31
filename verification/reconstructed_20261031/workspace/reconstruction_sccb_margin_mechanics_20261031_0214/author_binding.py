from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;W=O.parent;H=W/'reconstruction_control_links_20261031_0201';q=H/'review_manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(q)!='dda378e90fc7819c452eeedb115e77baaaa8ce35685b3d2b5e2839969fea0e66':raise RuntimeError('author manifest')
j=json.load(open(q));files=j['files']
if len(files)!=153:raise RuntimeError('153 allowlisted files')
for rel,item in files.items():
 p=H/rel
 if sha(p)!=item['sha256']or p.stat().st_size!=item['bytes']:raise RuntimeError('author artifact '+rel)
expected='c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855'
if sha(H/j['native_path'])!=expected or sha(O/'selected_native.kicad_pcb')!=expected:raise RuntimeError('selected local/author PCB')
(O/'author_binding.json').write_text(json.dumps({'author_manifest_sha256':sha(q),'author_files_verified':153,'exact_selected_native_sha256':expected,'local_snapshot_matches_author':True,'functional_scope':'NEW f27-based two MCU SCCB closures; eight data paths retained; receive remains open; no missing historical recovery claim','independent_electrical_review_pending':True,'NOFAB':True,'NO_POWER':True,'no_remote_action_authorized_or_performed':True},indent=2)+'\n')
