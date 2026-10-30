import geometry as q,json
p=q.p;F=p.F_Cu
fps={f.GetReference():f for f in q.b.GetFootprints()}
def spec(t):
 v=isinstance(t,p.PCB_VIA)
 return {'type':'via'if v else'track','net':t.GetNetname(),'layer':'through'if v else q.b.GetLayerName(t.GetLayer()),'start':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'width':(t.GetWidth(F)if v else t.GetWidth())/1e6,'drill':t.GetDrillValue()/1e6 if v else None}
results=[]
for name,ry,vy in [('local_upper',11.5,8.0),('local_lower',13.0,8.45)]:
 fps['C103'].SetPosition(q.V([.8,7.025]));fps['R503'].SetPosition(q.V([2.5,ry]));q.cache.clear()
 A='3V3_AON'
 n=[q.track(A,F,[2.575,7.8],[1.8,7.8],.25),q.track(A,F,[2.575,8.2],[1.8,8.2],.25),q.track(A,F,[1.8,7.8],[1.8,8.2],.635),q.track(A,F,[1.8,7.8],[.8,7.8],.635),q.track(A,F,[1.8,8.0],[1.8,vy],.635),q.via(A,[1.8,vy]),q.track('GND',F,[.8,6.25],[1.2,6.25],.3)]
 # Exclude zero-length connect segment.
 n=[t for t in n if isinstance(t,p.PCB_VIA)or t.GetStart()!=t.GetEnd()]
 errors=q.errors(n)
 # Moved pads against all old copper and other physical pads, including same-net drills.
 moved=[]
 for ref in ['C103','R503']:
  for pad in fps[ref].Pads():
   for o in q.old+[z for z in q.pads if z.GetParentFootprint().GetReference()!=ref]:
    for l in q.L:
     if not pad.IsOnLayer(l)or not o.IsOnLayer(l):continue
     if pad.GetNetname()!=o.GetNetname():
      z=p.SHAPE_POLY_SET(q.shape(pad,l,150000));z.BooleanIntersection(q.shape(o,l))
      if z.Area()>1:moved.append({'pad':ref+'.'+pad.GetNumber(),'other':q.desc(o),'layer':q.b.GetLayerName(l),'kind':'clearance','overlap_mm2':z.Area()/1e12})
     if isinstance(o,p.PCB_VIA):
      z=p.SHAPE_POLY_SET(q.shape(pad,l));z.BooleanIntersection(q.shape(o,l))
      if z.Area()>1:moved.append({'pad':ref+'.'+pad.GetNumber(),'other':q.desc(o),'kind':'via_ring'})
 results.append({'name':name,'poses':{'C103':[.8,7.025,90,'F.Cu'],'R503':[2.5,ry,0,'B.Cu']},'objects':[spec(t)for t in n],'route_errors':errors,'moved_pad_errors':moved})
print(json.dumps(results,indent=2))
