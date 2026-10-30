import geometry_native as g
import json
p=g.p;m=json.loads((g.D/'materialization.json').read_text());new=[t for t in g.old if t.m_Uuid.AsString()in m['added']];g.old=[t for t in g.old if t.m_Uuid.AsString()not in m['added']];errs=g.errors(new)
if errs:raise RuntimeError(errs)
rows=[]
for f in g.b.GetFootprints():f.BuildCourtyardCaches()
for t in new:
 if not isinstance(t,p.PCB_VIA):continue
 for f in g.b.GetFootprints():
  for l in [p.F_CrtYd,p.B_CrtYd]:
   s=g.shape(t,p.F_Cu);s.BooleanIntersection(f.GetCourtyard(l))
   if s.Area()>1:rows.append({'ref':f.GetReference(),'layer':g.b.GetLayerName(l),'area_mm2':s.Area()/1e12})
if rows:raise RuntimeError(rows)
print(json.dumps({'new_copper':len(new),'finite_geometry_errors':errs,'new_via_courtyard_intersections':rows,'scope':'nominal CAD only, no assembly/mask/tenting qualification'},indent=2))
