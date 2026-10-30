from pathlib import Path
import os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/translator0130'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/mcu_power_ground_clearance_0109/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];old=[t for t in b.GetTracks()if t.m_Uuid.AsString()not in ['65eab90d-6060-4683-a290-98053d52e2b9','4840f47d-9bac-414c-95e5-5f939fd72d28']];
for f in b.GetFootprints():
 if f.GetReference()=='C207':f.SetPosition(p.VECTOR2I(10000000,65000000))
 if f.GetReference()=='C208':f.SetPosition(p.VECTOR2I(2000000,65000000))
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
def link(a,c,tag):
 n=pm[a].GetNetname()
 if n!=pm[c].GetNetname():raise RuntimeError('domain mismatch')
 add([track(n,p.F_Cu,xy(pm[a]),xy(pm[c]))],tag)
# Exact same-domain adjacent local cap links. These do not claim source/core reachability yet.
for r,c in [('U201.1','C201.1'),('U201.24','C202.1'),('U201.23','U201.24'),('U202.1','C203.1'),('U202.16','C204.1'),('U203.1','C205.1'),('U203.16','C206.1'),('U203.1','U203.2'),('U203.2','U203.3'),('U201.11','U201.12'),('U202.2','U202.3')]:link(r,c,r+'_'+c)
# Same-domain TCA links after the explicit two-cap pose exchange; no domain rename.
for net,pts,tag in [('3V3_AON',[(8.1125,64.025),(9.225,64.025),(9.225,65.775),(10,65.775)],'TCA_AON_local'),('SENS_VIO_1V8',[(3.8875,64.025),(2.775,64.025),(2.775,65.775),(2,65.775)],'TCA_SENS_local')]:
 add([track(net,p.F_Cu,a,c,.254)for a,c in zip(pts,pts[1:])],tag)
# Bounded radial candidate set around actual pad; all-layer annulus/pad exclusion including same net.
def padvia(name):
 q=pm[name];x,y=xy(q);n=q.GetNetname();cands=[]
 for d in [.9,1.1,1.3,1.5,1.8]:
  for dx,dy in [(0,-d),(0,d),(-d,0),(d,0),(-d,-d),(-d,d),(d,-d),(d,d)]:
   a=(round(x+dx,4),round(y+dy,4));items=[track(n,p.F_Cu,(x,y),a),via(n,a)];er=errors(items);cands.append(dict(at=a,errors=er))
   if not er:add(items,name+'_localvia');attempts.append(dict(pad=name,selected=a,attempts=cands));return a
 attempts.append(dict(pad=name,selected=None,attempts=cands));return None
# Ground references first, including tied-low controls. Source-ground names are explicit.
for name in ['C201.2','C202.2','C203.2','C204.2','C205.2','C206.2','C208.2','U201.2','U201.12','U201.13','U202.3','U202.8','U202.9','U203.8','U203.9','U204.4']:
 padvia(name)
# AON cap branches via to the existing AON plane (fresh-fill/core validation remains mandatory).
for name in ['C201.1','C203.1','C205.1','C207.1']:padvia(name)
# Independent SENS local supply access vias, not a source or an internally generated rail.
# SENSOR through-vias deliberately not added until a complete external-source route exists.
result=dict(status='BOUNDED_LOCAL_MODEL_NOFAB',base_sha=hashlib.sha256(S.read_bytes()).hexdigest(),objects=spec,local_via_attempts=attempts,unresolved=[x['pad']for x in attempts if x['selected']is None],note='SENS local vias are not source-connected; do not materialize dangling sensor vias without a verified rail path. No native board saved.')
(D/'plan_v2.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(objects=len(spec),unresolved=result['unresolved'],selected=[(r['pad'],r['selected'])for r in attempts]),indent=2))
