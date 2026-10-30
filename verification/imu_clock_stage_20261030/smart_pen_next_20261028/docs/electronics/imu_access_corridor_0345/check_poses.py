import sys,json,io,contextlib
from pathlib import Path
D=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):import explore as z
q=z.g;p=q.p
out=[]
for pose in [(3.2,88),(5.2,84)]:
 z.fps['J107'].SetPosition(q.V(pose));errors=[]
 # Use uncached native pad TransformShapeToPolygon for moving pads, actual cached OLD other objects.
 for pad in z.fps['J107'].Pads():
  for t in q.old+[x for x in q.pads if x.GetParentFootprint().GetReference()!='J107']:
   if pad.GetNetname()==t.GetNetname():continue
   for l in q.L:
    if pad.IsOnLayer(l)and t.IsOnLayer(l):
     a=p.SHAPE_POLY_SET();pad.TransformShapeToPolygon(a,l,150000,1000,p.ERROR_INSIDE);b=p.SHAPE_POLY_SET();b.BooleanIntersection(a,q.shape(t,l))
     if b.Area()>1:errors.append({'pad':pad.GetNumber(),'other':q.desc(t),'net':t.GetNetname(),'layer':q.b.GetLayerName(l),'clearance_overlap_mm2':b.Area()/1e12})
 for f in q.b.GetFootprints():f.BuildCourtyardCaches()
 fp=[]
 for f in q.b.GetFootprints():
  if f.GetReference()=='J107':continue
  a=p.SHAPE_POLY_SET();a.BooleanIntersection(z.fps['J107'].GetCourtyard(p.B_CrtYd),f.GetCourtyard(p.B_CrtYd))
  if a.Area()>1:fp.append({'other':f.GetReference(),'overlap_mm2':a.Area()/1e12})
 out.append({'pose':pose,'pads':[{'number':x.GetNumber(),'net':x.GetNetname(),'xy':[x.GetPosition().x/1e6,x.GetPosition().y/1e6]}for x in z.fps['J107'].Pads()],'foreign_old_copper_clearance_failures':errors,'courtyard_failures':fp,'accept':not(errors or fp)})
print(json.dumps({'status':'TWO_PLACEMENTS_REJECTED_NO_NATIVE','cases':out},indent=2))
