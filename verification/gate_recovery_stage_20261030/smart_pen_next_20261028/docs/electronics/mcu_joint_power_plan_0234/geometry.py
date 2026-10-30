from pathlib import Path
import os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/power0208'
import pcbnew as p
from finite_copper import build,L,shape as finite_shape
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/gate_power_candidate_0228/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));old=list(b.GetTracks());pads=[q for f in b.GetFootprints()for q in f.Pads()];pm={f.GetReference()+'.'+q.GetNumber():q for f in b.GetFootprints()for q in f.Pads()};keep=[];uid=lambda t:t.m_Uuid.AsString();V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6));outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline)
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
