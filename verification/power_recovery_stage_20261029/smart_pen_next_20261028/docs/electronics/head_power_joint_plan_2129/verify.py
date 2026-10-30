from pathlib import Path
import os,json,hashlib,copy
os.environ['XDG_CONFIG_HOME']='/tmp/pen-head-powerverify'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];data=json.loads((D/'result.json').read_text());S=R/'hardware/complete_net_restore_candidate_2014/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows'];pads={f.GetReference()+'.'+q.GetNumber():q for f in b.GetFootprints()for q in f.Pads()}
def req(x,m):
 if not x:raise ValueError(m)
V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))
def make(o):
 if o['type']=='via':
  t=p.PCB_VIA(b);t.SetPosition(V(o['start']));t.SetWidth(p.F_Cu,round(o['width']*1e6));t.SetDrill(round(o['drill']*1e6));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
 else:
  t=p.PCB_TRACK(b);t.SetStart(V(o['start']));t.SetEnd(V(o['end']));t.SetWidth(round(o['width']*1e6));t.SetLayer(b.GetLayerID(o['layer']))
 t.SetNetCode(b.GetNetcodeFromNetname(o['net']));return t
spec=data['objects'];objs=[make(o)for o in spec]
def shape(t,l):
 z=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(z,l,0,50,p.ERROR_OUTSIDE);return z
cache={}
def g(t,l):
 k=(id(t),l)
 if k not in cache:cache[k]=shape(t,l)
 return cache[k]
def touches(t,q):
 for l in L:
  if t.IsOnLayer(l)and q.IsOnLayer(l):
   z=p.SHAPE_POLY_SET();z.BooleanIntersection(g(t,l),g(q,l))
   if z.Area()>1:return True
 return False
chains=[];negative=[]
contracts=[(r['net'],r['translator_pin'],'J202.'+r['J202_pin'])for r in rows]+[('CAM_3V3_SW','JP301.2','J301.1'),('GND','J106.3','J301.2')]
for net,a,z in contracts:
 ids=[i for i,o in enumerate(spec)if o['net']==net];nodes=[objs[i]for i in ids]+[pads[a],pads[z]];adj=[set()for _ in nodes]
 for i,t in enumerate(nodes):
  for j,q in enumerate(nodes[:i]):
   if touches(t,q):adj[i].add(j);adj[j].add(i)
 def connected(skip=None):
  seen={len(nodes)-2};todo=list(seen)
  while todo:
   i=todo.pop()
   for j in adj[i]:
    if j!=skip and j not in seen:seen.add(j);todo.append(j)
  return len(nodes)-1 in seen
 req(connected(),net+' disconnected')
 cuts=[i for i in range(len(ids))if not connected(i)];req(cuts,net+' missing negative')
 chains.append(dict(net=net,start=a,end=z,object_count=len(ids),finite_copper_connected=True));negative.append(dict(net=net,deleted_object=ids[cuts[0]],rejected=True))
for k in ['copper_conflicts','drill_conflicts','annulus_pad_overlap','edge_conflicts','rule_conflicts']:req(not data[k],k)
req(hashlib.sha256(S.read_bytes()).hexdigest()==data['input_sha'],'source drift')
req(data['full_power_restored']==False and data['return_qualification']==False,'false pass')
# Record old plane exclusions as occupied reference area, not a substitute for refill.
a=p.LoadBoard(str(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'));exclusions=[]
for zone in a.Zones():
 if zone.GetIsRuleArea()or zone.GetNetname()not in ['GND','3V3_AON']:continue
 for l in L:
  if not zone.IsOnLayer(l):continue
  fill=zone.GetFilledPolysList(l);union=p.SHAPE_POLY_SET();hits=[]
  for i,t in enumerate(objs):
   if t.GetNetname()==zone.GetNetname()or not t.IsOnLayer(l):continue
   cut=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(cut,l,zone.GetLocalClearance(),50,p.ERROR_OUTSIDE);cut.BooleanIntersection(fill)
   if cut.Area()>1:union.BooleanAdd(cut);hits.append(i)
  exclusions.append(dict(zone_uuid=zone.m_Uuid.AsString(),net=zone.GetNetname(),layer=b.GetLayerName(l),old_fill_intersection_union_mm2=union.Area()/1e12,object_indices=hits,not_fresh_fill=True))
print(json.dumps(dict(status='FINITE_GEOMETRY_AND_PARTIAL_CONNECTIONS_ONLY_NOFAB',chains=chains,negative_cases=negative,plane_occupancy=exclusions,total_modeled_objects=len(objs),full_AON_39pads_connected=False,complete_GND_return=False,fresh_fill=False,native_saved=False),indent=2))
