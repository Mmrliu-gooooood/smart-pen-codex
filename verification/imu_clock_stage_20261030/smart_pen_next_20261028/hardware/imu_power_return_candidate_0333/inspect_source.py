"""Read-only, bounded all-layer via probe. No board object is saved."""
from geometry import *
import xml.etree.ElementTree as ET
expected='6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c'
if hashlib.sha256(S.read_bytes()).hexdigest()!=expected:raise RuntimeError('wrong source')
rows=[]
for f in b.GetFootprints():
 if f.GetReference() in ['U501','C501','C502','C503','R503','J107']:
  rows.append(dict(ref=f.GetReference(),value=f.GetValue(),position=xy(f),pads=[dict(number=q.GetNumber(),net=q.GetNetname(),position=xy(q),size=[q.GetSize().x/1e6,q.GetSize().y/1e6],layers=[b.GetLayerName(l)for l in L if q.IsOnLayer(l)])for q in f.Pads()]))
probes=[]
for n,x,y in [('3V3_AON',2.65,79.9),('GND',4.45,83.4),('GND',7.3,81.3),('3V3_AON',5.72,79.7),('3V3_AON',4.35,85.8),('GND',7.2,84.5)]:
 probes.append(dict(net=n,position=[x,y],errors=errors([via(n,(x,y))])))
if probes[0]['errors'] or any(not x['errors']for x in probes[1:]):raise RuntimeError('bounded probe result changed')
print(json.dumps(dict(status='REJECTED_PLAN_ONLY_NOT_NATIVE',source_sha256=expected,old_copper_count=len(old),footprints=rows,probes=probes),indent=2))
