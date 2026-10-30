import json
import geometry as q
p=q.p;b=q.b;m=json.loads((q.D/'materialization.json').read_text());ts={q.uid(t):t for t in b.GetTracks()};new=[ts[u]for u in m['added']]
e=q.errors(new)
if e:raise RuntimeError(str(e))
c=[]
for i,t in enumerate(new):
 if not isinstance(t,p.PCB_VIA):continue
 for f in b.GetFootprints():
  f.BuildCourtyardCaches()
  for side in [p.F_CrtYd,p.B_CrtYd]:
   x=p.SHAPE_POLY_SET();x.BooleanIntersection(q.shape(t,p.F_Cu),f.GetCourtyard(side))
   if x.Area()>1:c.append(dict(object=i,ref=f.GetReference(),side=b.GetLayerName(side),overlap_mm2=x.Area()/1e12))
if {(r['object'],r['ref'])for r in c}!={(5,'U101'),(5,'C103'),(8,'C103')}:raise RuntimeError('unexpected courtyard changes')
print(json.dumps(dict(route_errors=e,all_actual_layers_checked=True,same_net_via_annulus_pad_overlap_excluded=True,courtyard_overlaps=c,courtyard_qualification=False,short_025_escape_qualification=False,manufacturing_release=False,power_release=False),indent=2))
