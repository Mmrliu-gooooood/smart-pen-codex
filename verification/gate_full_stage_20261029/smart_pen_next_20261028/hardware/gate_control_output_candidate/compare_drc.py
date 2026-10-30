from pathlib import Path
import json,hashlib,collections
D=Path(__file__).resolve().parent
A=D.parent/'gate_input_local_routing/preflight.native_drc.json';B=D/'preflight.native_drc.json';a=json.loads(A.read_text());b=json.loads(B.read_text())
def key(v):return(v['type'],tuple(sorted(i['uuid']for i in v.get('items',[]))))
aa={key(v):v for v in a['violations']};bb={key(v):v for v in b['violations']}
print(json.dumps({'before_file_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'after_file_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'before_counts':{k:len(a[k])for k in ['violations','unconnected_items','schematic_parity']},'after_counts':{k:len(b[k])for k in ['violations','unconnected_items','schematic_parity']},'comparison_identity':'type plus sorted involved UUIDs; warning representative may vary; no deduplication applied to raw native totals','added':[bb[k]for k in sorted(bb.keys()-aa.keys())],'removed':[aa[k]for k in sorted(aa.keys()-bb.keys())],'retained_count':len(aa.keys()&bb.keys()),'NOFAB':True},indent=2))
