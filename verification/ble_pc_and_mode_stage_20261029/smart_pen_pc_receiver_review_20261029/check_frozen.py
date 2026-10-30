from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent.parent
out={}
for name in ['smart_pen_pc_receiver_candidate_20261029','smart_pen_pc_receiver_v2_candidate_20261029','smart_pen_ble_transport_candidate_20261029']:
 p=root/name; manifest=p/'verification/MANIFEST.json'
 if not manifest.exists():manifest=p/'verification/source_manifest.json'
 d=json.loads(manifest.read_text()); files=d.get('files',d);bad=[k for k,v in files.items() if hashlib.sha256((p/k).read_bytes()).hexdigest()!=(v['sha256'] if isinstance(v,dict) else v)]
 out[name]={'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'entries':len(files),'mismatches':bad}
 assert not bad
print(json.dumps(out,indent=2))
