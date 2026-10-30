from pathlib import Path
import os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/power0208'
import pcbnew as p
from finite_copper import build,L,shape as finite_shape
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/sens_tree_candidate_0158/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));old=list(b.GetTracks());pads=[q for f in b.GetFootprints()for q in f.Pads()];pm={f.GetReference()+'.'+q.GetNumber():q for f in b.GetFootprints()for q in f.Pads()};keep=[];uid=lambda t:t.m_Uuid.AsString();V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6));outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline)
def xy(q):return[q.GetPosition().x/1e6,q.GetPosition().y/1e6]
def track(n,l,a,c,w):
 t=p.PCB_TRACK(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetLayer(l);t.SetStart(V(a));t.SetEnd(V(c));t.SetWidth(round(w*1e6));keep.append(t);return t

def via(n,a):
 t=p.PCB_VIA(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetPosition(V(a));t.SetWidth(p.F_Cu,600000);t.SetDrill(300000);t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);keep.append(t);return t
cache={}
def shape(t,l,m=0):
 k=(id(t),l,m)
 if k not in cache:
  s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,l,m,50,p.ERROR_OUTSIDE);cache[k]=s
 return cache[k]
def desc(q):return q.GetParentFootprint().GetReference()+'.'+q.GetNumber()if isinstance(q,p.PAD)else uid(q)
def errors(new):
 out=[]
 for i,t in enumerate(new):
  for q in new[:i]+old+pads:
   for l in L:
    if not t.IsOnLayer(l)or not q.IsOnLayer(l):continue
    if t.GetNetname()!=q.GetNetname():
     x,y=shape(t,l,150000),shape(q,l)
     if x.BBox().Intersects(y.BBox()):
      z=p.SHAPE_POLY_SET();z.BooleanIntersection(x,y)
      if z.Area()>1:out.append(dict(kind='copper',object=i,net=t.GetNetname(),other=desc(q),other_net=q.GetNetname(),layer=b.GetLayerName(l),overlap_mm2=z.Area()/1e12));break
   if isinstance(t,p.PCB_VIA):
    if isinstance(q,p.PCB_VIA):
     gap=math.hypot(t.GetPosition().x-q.GetPosition().x,t.GetPosition().y-q.GetPosition().y)-(t.GetDrillValue()+q.GetDrillValue())/2
     if gap<249999:out.append(dict(kind='drill',object=i,other=desc(q),gap_mm=gap/1e6))
    if isinstance(q,p.PAD):
     for l in L:
      if not q.IsOnLayer(l):continue
      z=p.SHAPE_POLY_SET();z.BooleanIntersection(shape(t,l),shape(q,l))
      if z.Area()>1:out.append(dict(kind='via_pad_including_same_net',object=i,other=desc(q),layer=b.GetLayerName(l)))
  l=p.F_Cu if isinstance(t,p.PCB_VIA)else t.GetLayer();q=p.SHAPE_POLY_SET(shape(t,l,250000));q.BooleanSubtract(outline)
  if q.Area()>1:out.append(dict(kind='edge',object=i))
  for z in b.Zones():
   if not z.GetIsRuleArea()or not(z.GetDoNotAllowVias()if isinstance(t,p.PCB_VIA)else z.GetDoNotAllowTracks()):continue
   for l in L:
    if z.IsOnLayer(l)and t.IsOnLayer(l):
     q=p.SHAPE_POLY_SET(shape(t,l));q.BooleanIntersection(z.Outline())
     if q.Area()>1:out.append(dict(kind='rule',object=i,zone=z.GetZoneName(),layer=b.GetLayerName(l)))
 return out
A='3V3_AON';G='GND';F=p.F_Cu;B=p.B_Cu
mcu=[track(A,F,[2.575,7.8],[1.9,7.8],.25),track(A,F,[2.575,8.2],[1.9,8.2],.25),track(A,F,[1.9,7.8],[1.2,7.8],.508),track(A,F,[1.9,8.2],[1.2,8.2],.508),track(A,F,[1.2,7.8],[1.2,9.0],.508),via(A,[1.2,9.0])]
gate=[track(A,B,[10.8,66.05],[10.95,66.05],.5),track(A,B,[10.95,66.05],[10.95,64.0],.5),track(A,B,[10.95,64.0],[10.95,62.5],.5),via(A,[10.95,62.5])]
for name,at in [('U301.2',[11.7,67]),('C302.2',[8.8,75.2]),('C303.2',[3.8,69.0]),('R301.2',[4.85,65.5])]:gate.extend([track(G,B,xy(pm[name]),at,.3),via(G,at)])
def spec(t):
 v=isinstance(t,p.PCB_VIA);return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else b.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if v else t.GetWidth())/1e6,drill=.3 if v else None)
result={'status':'READ_ONLY_TWO_SUBSYSTEM_FIRST_GEOMETRY_PASS_NOFAB','base_sha':hashlib.sha256(S.read_bytes()).hexdigest(),'base_objects':len(old),'pads':len(pads),'attempts':[]}
for name,objs in [('mcu_rf_vdd3p3',mcu),('camera_load_gate',gate)]:result['attempts'].append(dict(name=name,objects=[spec(t)for t in objs],errors=errors(objs)))
print(json.dumps(result,indent=2))
# One bounded local alternative set per failed return. No existing net is removed.
alts=[]
for name,at in [('C302.2',[7.6,75.2]),('C302.2',[9.8,75.2]),('C302.2',[8.8,72.8]),('C303.2',[2.8,68]),('C303.2',[3.8,67]),('R301.2',[4.85,67.5]),('R301.2',[4.0,66.5])]:
 items=[track(G,B,xy(pm[name]),at,.3),via(G,at)];alts.append(dict(pad=name,via=at,objects=[spec(t)for t in items],errors=errors(items)))
(D/'alternatives.json').write_text(json.dumps(alts,indent=2)+'\n')
# Coherent gate alternative: reuse verified current GND core access vias, no duplicate holes.
gate2=gate[:6]+[track(G,B,xy(pm['C302.2']),[7.6,74],.3),track(G,B,xy(pm['C303.2']),[3.8875,66.875],.3),track(G,B,xy(pm['R301.2']),[3.8875,66.875],.3)]
(D/'gate2.json').write_text(json.dumps(dict(objects=[spec(t)for t in gate2],errors=errors(gate2)),indent=2)+'\n')
# Final coherent gate model reuses existing AON source-plane via (10.9,64.875), avoiding an unnecessary hole.
gate3=[track(A,B,[10.8,66.05],[10.9,64.875],.5),track(A,B,[10.9,64.875],[10.95,64.0],.5),track(G,B,[10.8,67],[12.0,67],.3),via(G,[12.0,67]),track(G,B,xy(pm['C302.2']),[7.6,74],.3),track(G,B,xy(pm['C303.2']),[3.8875,66.875],.3),track(G,B,xy(pm['R301.2']),[3.8875,66.875],.3)]
(D/'gate3.json').write_text(json.dumps(dict(objects=[spec(t)for t in gate3],errors=errors(gate3)),indent=2)+'\n')
