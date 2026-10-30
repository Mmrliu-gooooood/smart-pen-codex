from pathlib import Path
import json,collections
from pcb_preflight import verify
D=Path(__file__).resolve().parent;B=D.parent/'j107_mode_port_closure';lock=json.loads((D/'preflight_lock.json').read_text());r=verify(D/'native/mainboard_revD.kicad_pcb',lock,'routing')
try:verify(D/'native/mainboard_revD.kicad_pcb',lock,'manufacturing')
except ValueError as e:r['manufacturing_rejection']=str(e)
else:raise RuntimeError('Manufacturing unexpectedly released')
def norm(f):
 d=json.loads(f.read_text());c=collections.Counter()
 for v in d['violations']:v=dict(v);v['items']=sorted(v.get('items',[]),key=lambda x:json.dumps(x,sort_keys=True));c[json.dumps(v,sort_keys=True)]+=1
 return d,c
old,a=norm(B/'preflight.native_drc.json');new,b=norm(D/'drc.json')
if a!=b or len(new['unconnected_items'])!=38 or new['schematic_parity']:raise RuntimeError('DRC delta not expected')
r['DRC']={'violations':17,'unconnected':38,'parity':0,'violation_multiset_identical':True,'exit':int((D/'drc.exit').read_text())}
if r['DRC']['exit']!=5:raise RuntimeError('Bad native exit handling')
r.pop('checked_utc',None);print(json.dumps(r,indent=2))
