from pathlib import Path
import json,collections,hashlib
D=Path(__file__).resolve().parent;A=D.parent/'gate_cam_on_path_maintenance/preflight.native_drc.json';B=D/'preflight.native_drc.json'
def read(f):
 x=json.loads(f.read_text());rows=[]
 for v in x['violations']:
  q=dict(v);q['items']=sorted(q.get('items',[]),key=lambda a:json.dumps(a,sort_keys=True));rows.append(json.dumps(q,sort_keys=True))
 return x,collections.Counter(rows)
a,ca=read(A);b,cb=read(B);added=list((cb-ca).elements());removed=list((ca-cb).elements())
if added:raise RuntimeError('Unexpected new complete DRC findings')
if len(removed)!=11 or len(b['violations'])!=17 or len(b['unconnected_items'])!=38 or b['schematic_parity']:raise RuntimeError('Unexpected exact full DRC result')
print(json.dumps({'before':[len(a[k])for k in ['violations','unconnected_items','schematic_parity']],'after':[len(b[k])for k in ['violations','unconnected_items','schematic_parity']],'added':[],'removed':[json.loads(s)for s in removed],'retained_multiset_count':sum((ca&cb).values()),'comparison':'Complete native violation objects, normalize item order only; no raw-count deduplication. Airwire representatives not treated as physical components.'},indent=2))
