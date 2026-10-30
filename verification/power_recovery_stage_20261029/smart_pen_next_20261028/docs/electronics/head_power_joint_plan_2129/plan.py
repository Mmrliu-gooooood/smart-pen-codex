from pathlib import Path
import json,hashlib,math,os
os.environ['XDG_CONFIG_HOME']='/tmp/pen-head-power2129'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/complete_net_restore_candidate_2014/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));before=hashlib.sha256(S.read_bytes()).hexdigest()
rows=json.loads((R/'docs/electronics/dvp_joint_feasibility_1942/result.json').read_text())['routes'];head={r['net']:r['J202_xy']for r in json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows']};dvpnets=set(head);old=[t for t in b.GetTracks()if t.GetNetname()not in dvpnets];pads=[q for f in b.GetFootprints()for q in f.Pads()];L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];objs=[];spec=[]
V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))
def line(n,l,pts,w=.15):
 for a,c in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetLayer(l);t.SetWidth(round(w*1e6));t.SetStart(V(a));t.SetEnd(V(c));objs.append(t);spec.append(dict(type='track',net=n,layer=b.GetLayerName(l),start=a,end=c,width=w))
def via(n,xy,power=False):
 t=p.PCB_VIA(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetPosition(V(xy));t.SetWidth(p.F_Cu,600000 if power else 450000);t.SetDrill(300000 if power else 200000);t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);objs.append(t);spec.append(dict(type='via',net=n,layer='through',start=xy,end=xy,width=.6 if power else .45,drill=.3 if power else .2))
for i,r in enumerate(rows):
 n=r['net'];x,y=r['source'];sx,sy=(r['source_via']or[x,r['trunk_entry_y']]);hx,hy=head[n];ly=b.GetLayerID(r['layer']);ey=r['head_exit_y']-(3 if i>=4 else 0);lane=r['trunk'];ey=78.6 if n=='SENS_EXTCLK'else ey;line(n,p.F_Cu,[(x,y),(x,sy)])
 if i>=4:via(n,(x,sy))
 endx=8.0 if n=='SENS_D7'else hx
 line(n,ly,[(x,sy),(lane,sy),(lane,ey),(endx,ey)])
 if i<8:via(n,(endx,ey))
 if n=='SENS_D7':line(n,p.B_Cu,[(endx,ey),(hx,ey),(hx,84.0),(7.4,84.2),(7.4,89.8),(hx,hy)])
 else:line(n,p.B_Cu,[(hx,ey),(hx,hy)])
# Core AON and GND entries; no selected plane fill exists.
line('3V3_AON',p.F_Cu,[(10.6,83.9),(11.9,83.9)],.5);via('3V3_AON',(11.9,83.9),True)
line('GND',p.F_Cu,[(8.2,88.7),(8.2,86.3),(10.6,86.3),(11.9,86.3)],.5);via('GND',(11.9,86.3),True)
line('CAM_3V3_SW',p.F_Cu,[(5.8,88.7),(6.825,87.6)],.5);via('CAM_3V3_SW',(6.825,87.6),True);line('CAM_3V3_SW',p.In2_Cu,[(6.825,87.6),(6.85,82.05),(6.85,79.0),(10.15,79.0),(10.15,78.5)],.5)
# Retained feasible AON middle replacement; mutually exclusive alternatives not combined.
line('3V3_AON',p.In2_Cu,[(11.2,55.75),(11.2,64),(11.3,64.8)],.5)
# Retain only the source-side SW fragment, replace the local seven-object bend.
prior=json.loads((R/'docs/electronics/copper_recovery_plan_2005/recovery_plan.json').read_text());upper=next(c for c in prior['components']if c['net']=='CAM_3V3_SW'and c['fixed_pad_contacts']==['JP301.2']);a=p.LoadBoard(str(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'));lookup={t.m_Uuid.AsString():t for t in a.GetTracks()}
skip={'549c7ef3-c97d-4eca-92aa-036dcad33cdf','7b5134ec-f0fb-4a9b-9a93-48d2bce80b7c','b4ca0f9e-a535-4c23-b7aa-6467183483b7','b736c260-abc8-4a10-8dd9-b1dea06225bb','dbe975fa-67ca-460f-933a-b96cb64213b7','33a62260-d86a-495d-86ad-5488161dc02e','b987d609-a10c-4b51-b920-fe34622eafad'}
for u in upper['uuids']:
 if u in skip:continue
 t=lookup[u];objs.append(t);isv=isinstance(t,p.PCB_VIA);spec.append(dict(type='via'if isv else'track',net=t.GetNetname(),layer='through'if isv else a.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(p.F_Cu)if isv else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if isv else None,old_uuid=u))
def shape(t,l,margin=0):
 z=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(z,l,margin,50,p.ERROR_OUTSIDE);return z
cache={}
def geom(t,l,m=0):
 k=(id(t),l,m)
 if k not in cache:cache[k]=shape(t,l,m)
 return cache[k]
def desc(t):
 if isinstance(t,p.PAD):return t.GetParentFootprint().GetReference()+'.'+t.GetNumber()
 return t.m_Uuid.AsString()
conflicts=[];drill=[];samepad=[];edge=[];rules=[];outline=p.SHAPE_POLY_SET()
if not b.GetBoardPolygonOutlines(outline):raise RuntimeError('outline')
for i,t in enumerate(objs):
 for j,q in enumerate(objs[:i]+old+pads):
  if t.GetNetname()!=q.GetNetname():
   layers=[]
   for l in L:
    if t.IsOnLayer(l)and q.IsOnLayer(l):
     z=p.SHAPE_POLY_SET();z.BooleanIntersection(geom(t,l,150000),geom(q,l))
     if z.Area()>1:layers.append(b.GetLayerName(l))
   if layers:conflicts.append(dict(index=i,net=t.GetNetname(),other_index=j if j<i else None,other=desc(q),other_net=q.GetNetname(),layers=layers))
  if isinstance(t,p.PCB_VIA):
   if isinstance(q,p.PCB_VIA):
    d=math.hypot(t.GetPosition().x-q.GetPosition().x,t.GetPosition().y-q.GetPosition().y)-(t.GetDrillValue()+q.GetDrillValue())/2
    if d<249999:drill.append(dict(index=i,other=desc(q),gap=d/1e6))
   if isinstance(q,p.PAD):
    for l in L:
     if q.IsOnLayer(l):
      z=p.SHAPE_POLY_SET();z.BooleanIntersection(geom(t,l),geom(q,l))
      if z.Area()>1:samepad.append(dict(index=i,other=desc(q),same_net=t.GetNetname()==q.GetNetname(),layer=b.GetLayerName(l)))
 l=p.F_Cu if isinstance(t,p.PCB_VIA)else t.GetLayer();z=shape(t,l,250000);z.BooleanSubtract(outline)
 if z.Area()>1:edge.append(i)
 for z in b.Zones():
  if not z.GetIsRuleArea()or not(z.GetDoNotAllowVias()if isinstance(t,p.PCB_VIA)else z.GetDoNotAllowTracks()):continue
  for l in L:
   if z.IsOnLayer(l)and t.IsOnLayer(l):
    q=shape(t,l);q.BooleanIntersection(z.Outline())
    if q.Area()>1:rules.append(dict(index=i,zone=z.GetZoneName(),layer=b.GetLayerName(l)))
if hashlib.sha256(S.read_bytes()).hexdigest()!=before:raise RuntimeError('input mutation')
result=dict(status='READ_ONLY_SINGLE_JOINT_TOPOLOGY_NOFAB',input_sha=before,objects=spec,existing_non_dvp_copper=len(old),pad_count=len(pads),pad_display=[dict(ref=q.GetParentFootprint().GetReference(),pin=q.GetNumber(),net=q.GetNetname(),reported_GetLayer=b.GetLayerName(q.GetLayer()),footprint_side=b.GetLayerName(q.GetParentFootprint().GetLayer()),copper_layers=[b.GetLayerName(l)for l in L if q.IsOnLayer(l)],bbox=[q.GetBoundingBox().GetX()/1e6,q.GetBoundingBox().GetY()/1e6,q.GetBoundingBox().GetWidth()/1e6,q.GetBoundingBox().GetHeight()/1e6])for q in pads],copper_conflicts=conflicts,drill_conflicts=drill,annulus_pad_overlap=samepad,edge_conflicts=edge,rule_conflicts=rules,full_power_restored=False,old_zones_restored=False,return_qualification=False)
(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['objects','copper_conflicts','pad_display']},indent=2));print('COPPER',len(conflicts));print(conflicts)
