from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;W=O.parent;H=W/'reconstruction_vsync_20261031_0322';q=H/'review_manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(q)!='366a2decc5716159936674369ab9304b20e72279f194c400c35e7ad33762514f':raise RuntimeError('author manifest')
j=json.load(open(q));files=j['files']
if len(files)!=182:raise RuntimeError('182 allowlisted files')
for item in files:
 rel=item['path']
 p=H/rel
 if sha(p)!=item['sha256']or p.stat().st_size!=item['bytes']:raise RuntimeError('author artifact '+rel)
expected='5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433'
if sha(H/j['native'])!=expected or sha(O/'selected_native.kicad_pcb')!=expected:raise RuntimeError('selected local/author PCB')
(O/'author_binding.json').write_text(json.dumps({'author_manifest_sha256':sha(q),'author_files_verified':182,'exact_selected_native_sha256':expected,'local_snapshot_matches_author':True,'functional_scope':'NEW d855-based two VSYNC joins; no pose changes; bounded SENS_D6 same-pad/via fanout replacement; long bias/return/capture gates remain','independent_electrical_review_pending':True,'NOFAB':True,'NO_POWER':True,'no_remote_action_authorized_or_performed':True},indent=2)+'\n')
