#!/usr/bin/env python3
import os,pathlib,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/pen-rf-check/config';os.environ['XDG_CACHE_HOME']='/tmp/pen-rf-check/cache'
import pcbnew as p
D=pathlib.Path(__file__).resolve().parent
b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'))
L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def shape(o,l):
 q=p.SHAPE_POLY_SET();o.TransformShapeToPolygon(q,l,0,500,p.ERROR_INSIDE)
 if isinstance(o,p.PCB_VIA):
  h=p.SHAPE_POLY_SET();h.NewOutline();v=o.GetPosition();r=o.GetDrillValue()/2
  for k in range(192):h.Append(round(v.x+r*math.cos(k*2*math.pi/192)),round(v.y+r*math.sin(k*2*math.pi/192)))
  q.BooleanSubtract(h)
 return q
nodes=[];keep=p.SHAPE_POLY_SET();keep.NewOutline()
for x,y in [(5.5,-6.5),(12,-6.5),(12,0),(5.5,0)]:keep.Append(p.FromMM(x),p.FromMM(y))
viol=[]
def add(label,net,sh,pad=False,allowed=False):
 for l,q in sh.items():
  z=p.SHAPE_POLY_SET();z.BooleanIntersection(q,keep)
  if z.Area()>1 and not allowed:viol.append([label,l,z.Area()/1e12])
 if net=='GND':nodes.append(dict(id=label,pad=pad,shapes=sh))
for f in b.GetFootprints():
 for x in f.Pads():add(f.GetReference()+'.'+x.GetNumber(),x.GetNetname(),{l:shape(x,l) for l in L if x.IsOnLayer(l)},True,f.GetReference()=='AE101')
for t in b.GetTracks():
 allowed=not isinstance(t,p.PCB_VIA) and t.GetNetname()=='RF_ANT' and min(t.GetStart().y,t.GetEnd().y)<=0 and t.GetStart().x==p.FromMM(9.5) and t.GetEnd().x==p.FromMM(9.5) and min(t.GetStart().y,t.GetEnd().y)>=p.FromMM(-1.9) and max(t.GetStart().y,t.GetEnd().y)<=p.FromMM(.9)
 add(t.m_Uuid.AsString(),t.GetNetname(),{l:shape(t,l) for l in L if isinstance(t,p.PCB_VIA) or t.GetLayer()==l},allowed=allowed)
for z in b.Zones():
 if z.GetIsRuleArea():continue
 q=z.GetFilledPolysList(z.GetLayer())
 for i in range(q.OutlineCount()):add(z.m_Uuid.AsString()+'/'+str(i),z.GetNetname(),{z.GetLayer():q.UnitSet(i)})
if viol:raise RuntimeError('Copper in radiator keepout: '+str(viol))
parent=list(range(len(nodes)))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for i,x in enumerate(nodes):
 for j,z in enumerate(nodes[:i]):
  for l in x['shapes'].keys()&z['shapes'].keys():
   xx=x['shapes'][l];zz=z['shapes'][l]
   if not xx.BBox().Intersects(zz.BBox()):continue
   q=p.SHAPE_POLY_SET();q.BooleanIntersection(xx,zz)
   if q.Area()>1:parent[root(i)]=root(j);break
comps={root(i) for i,n in enumerate(nodes) if n['pad']}
if len(comps)!=1:raise RuntimeError('Ground pad components: '+str(len(comps)))
z=next(z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()=='RF_RADIATOR_CLEARANCE_ALL_COPPER_LAYERS_NOFAB')
if set(z.GetLayerSet().Seq())!=set(L) or not z.GetDoNotAllowCopperPour() or not z.GetDoNotAllowVias():raise RuntimeError('Rule area incomplete')
wing_uuids={z.m_Uuid.AsString() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.Outline().BBox().GetRight()>p.FromMM(12)}
wing_nodes=[(i,n) for i,n in enumerate(nodes) if n['id'].split('/')[0] in wing_uuids]
if len(wing_uuids)!=2 or not wing_nodes:raise RuntimeError('expected two ground wing zones')
if any(root(i) not in comps for i,n in wing_nodes):raise RuntimeError('isolated ground wing finite island')
result=dict(ground_pad_shapes=sum(n['pad']for n in nodes),ground_components=len(comps),ground_wing_finite_islands=len(wing_nodes),ground_wing_islands_all_connected=True,radiator_other_copper_intersections=viol,matching_ground_connected=True,rf_feed_routed=True,qualification='NOFAB conditional geometry only',candidate_sha256=hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest())
print(json.dumps(result,indent=2,sort_keys=True))
