import geometry as g,json,hashlib
from pathlib import Path
D=g.D;m=json.loads((D/'model.json').read_text());parts=[]
if hashlib.sha256(g.S.read_bytes()).hexdigest()!=m['parent_sha']:raise RuntimeError('parentSHA')
if not m['complete_all']or m['removed']:raise RuntimeError('scope')
for tag,ts in m['parts'].items():
 for t in ts:
  if t['type']=='via':q=g.via(t['net'],t['a']);q.SetWidth(g.p.F_Cu,round(t['width']*1e6));q.SetDrill(round(t['drill']*1e6))
  else:q=g.track(t['net'],g.b.GetLayerID(t['layer']),t['a'],t['b'],t['width'])
  parts.append(q)
e=g.errors(parts)
if e:raise RuntimeError(str(e[:5]))
if len(parts)!=209:raise RuntimeError('count')
# Test that a known foreign-net collision is rejected (same layer and exact physical center).
pad=g.pm['R203.1'];bad=g.track('CAM_IO_EN',g.p.F_Cu,g.xy(pad),(8.7,72),.15)
if not g.errors([bad]):raise RuntimeError('negativecollisionaccepted')
print(json.dumps({'status':'MODEL_FINITE_GEOMETRY_PASS_NOT_NATIVE_RELEASE','objects':len(parts),'errors':e,'known_foreign_pad_negative_rejected':True,'parent_sha':m['parent_sha'],'model_sha':hashlib.sha256((D/'model.json').read_bytes()).hexdigest()},indent=2))
