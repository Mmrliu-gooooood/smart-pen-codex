from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-native1950-config'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'dvp_joint_native_candidate_1950/native/mainboard_revD.kicad_pcb';layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def poly(x,l,c=0):
 q=p.SHAPE_POLY_SET();x.TransformShapeToPolygon(q,l,c,50,p.ERROR_OUTSIDE);return q
out=[]
for ref,pts in [('R206',[(8,47),(9,45.5),(8,45.5),(7,47),(9,46)]),('J107',[(3.2,84),(3.7,84),(2.7,83.5),(2.7,84.5)])]:
 for xy in pts:
  b=p.LoadBoard(str(S));fs={f.GetReference():f for f in b.GetFootprints()};f=fs[ref];f.SetPosition(p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6)));coll=[]
  for pad in f.Pads():
   for t in b.GetTracks():
    if t.GetNetname()==pad.GetNetname():continue
    for l in layers:
     if pad.IsOnLayer(l)and t.IsOnLayer(l):
      q=poly(pad,l,150000);q.BooleanIntersection(poly(t,l))
      if q.Area()>1:coll.append(['copper',pad.GetNumber(),t.GetNetname(),b.GetLayerName(l)])
   for other,g in fs.items():
    if other==ref:continue
    for pp in g.Pads():
     for l in layers:
      if pad.IsOnLayer(l)and pp.IsOnLayer(l):
       q=poly(pad,l,150000);q.BooleanIntersection(poly(pp,l))
       if q.Area()>1:coll.append(['pad',pad.GetNumber(),other,pp.GetNumber()])
  f.BuildCourtyardCaches()
  for other,g in fs.items():
   if other==ref or g.GetLayer()!=f.GetLayer():continue
   g.BuildCourtyardCaches();q=p.SHAPE_POLY_SET();q.BooleanIntersection(f.GetCourtyard(f.GetLayer()),g.GetCourtyard(g.GetLayer()))
   if q.Area()>1:coll.append(['courtyard',other,q.Area()/1e12])
  out.append({'ref':ref,'xy':xy,'collisions':coll})
(D/'position_screen.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
