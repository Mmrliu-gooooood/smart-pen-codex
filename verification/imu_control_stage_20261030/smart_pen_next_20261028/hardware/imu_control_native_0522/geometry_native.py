from pathlib import Path
import os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/imu0333'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=D/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];old=list(b.GetTracks());
pads=[q for f in b.GetFootprints() for q in f.Pads()];pm={f.GetReference()+'.'+q.GetNumber():q for f in b.GetFootprints()for q in f.Pads()};objs=[];spec=[];attempts=[];outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline)
V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6))
xy=lambda x:(x.GetPosition().x/1e6,x.GetPosition().y/1e6)
def track(n,l,a,c,w=.3):
 t=p.PCB_TRACK(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetLayer(l);t.SetWidth(round(w*1e6));t.SetStart(V(a));t.SetEnd(V(c));return t

def via(n,a):
 t=p.PCB_VIA(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetPosition(V(a));t.SetWidth(p.F_Cu,600000);t.SetDrill(300000);t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);return t

def shape(t,l,m=0):
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,m,50,p.ERROR_OUTSIDE);return q
cache={}
def geom(t,l,m=0):
 k=(id(t),l,m)
 if k not in cache:cache[k]=shape(t,l,m)
 return cache[k]
# Keep temporary items alive so cache keys cannot alias a recycled object.
alltemps=[]
def errors(new):
 alltemps.extend(new);out=[]
 for i,t in enumerate(new):
  for q in new[:i]+objs+old+pads:
   if t.GetNetname()!=q.GetNetname():
    for l in L:
     if t.IsOnLayer(l)and q.IsOnLayer(l):
      if not geom(t,l,150000).BBox().Intersects(geom(q,l).BBox()):continue
      z=p.SHAPE_POLY_SET();z.BooleanIntersection(geom(t,l,150000),geom(q,l))
      if z.Area()>1:out.append(('copper',t.GetNetname(),q.GetNetname(),desc(q),b.GetLayerName(l)));break
   if isinstance(t,p.PCB_VIA):
    if isinstance(q,p.PCB_VIA):
     dist=math.hypot(t.GetPosition().x-q.GetPosition().x,t.GetPosition().y-q.GetPosition().y)-(t.GetDrillValue()+q.GetDrillValue())/2
     if dist<249999:out.append(('drill',desc(q),dist/1e6))
    if isinstance(q,p.PAD):
     for l in L:
      if not q.IsOnLayer(l):continue
      z=p.SHAPE_POLY_SET();z.BooleanIntersection(geom(t,l),geom(q,l))
      if z.Area()>1:out.append(('via_pad',desc(q),q.GetNetname(),b.GetLayerName(l)))
  l=p.F_Cu if isinstance(t,p.PCB_VIA) else t.GetLayer();q=shape(t,l,250000);q.BooleanSubtract(outline)
  if q.Area()>1:out.append(('edge',))
  for z in b.Zones():
   if not z.GetIsRuleArea()or not(z.GetDoNotAllowVias() if isinstance(t,p.PCB_VIA)else z.GetDoNotAllowTracks()):continue
   for l in L:
    if z.IsOnLayer(l)and t.IsOnLayer(l):
     q=shape(t,l);q.BooleanIntersection(z.Outline())
     if q.Area()>1:out.append(('rule',z.GetZoneName(),b.GetLayerName(l)))
 return out

def desc(q):return q.GetParentFootprint().GetReference()+'.'+q.GetNumber() if isinstance(q,p.PAD)else q.m_Uuid.AsString()
def add(items,tag):
 er=errors(items)
 if er:raise RuntimeError(str((tag,er[:12])))
 for t in items:
  isv=isinstance(t,p.PCB_VIA);objs.append(t);spec.append(dict(tag=tag,type='via'if isv else'track',net=t.GetNetname(),layer='through'if isv else b.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(p.F_Cu)if isv else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if isv else None))
