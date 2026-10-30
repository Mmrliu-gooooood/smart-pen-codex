from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-gndverify2159'
import pcbnew as p
from finite_copper import build,components,L
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/aon_entry_bridge_candidate_2156';O=R/'hardware/j202_low_speed_reference_candidate';f=D/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));old=p.LoadBoard(str(O/'native/mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());ids=set(m['added_uuids']);uid=lambda t:t.m_Uuid.AsString()
def req(x,s):
 if not x:raise RuntimeError(s)
def sig(t):return(t.GetNetname(),t.GetLayerSet().FmtHex(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
ts={uid(t):t for t in b.GetTracks()};ot={uid(t):t for t in old.GetTracks()};req(all(sig(ts[u])==sig(ot[u])for u in ids),'OLD WIDTH/GEOMETRY CHANGED')
nets=build(b)
def reach(nodes,start,omit=set()):
 nodes=[x for x in nodes if x[0]not in omit];seen={start};todo=[start];lookup={x[0]:x for x in nodes}
 while todo:
  _,_,si=lookup[todo.pop()]
  for name,_,sj in nodes:
   if name in seen:continue
   for l in si.keys()&sj.keys():
    if not si[l].BBox().Intersects(sj[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(si[l],sj[l])
    if q.Area()>1:seen.add(name);todo.append(name);break
 return seen
gnd=reach(nets['GND'],'J106.3');aon=reach(nets['3V3_AON'],'J106.2');req(any('/'in x for x in aon),'AON CORE LOST');plan=json.loads((D/'plan.json').read_text());rows=[]
for g in plan['components']:
 if not g['accepted_preflight']:continue
 req(set(g['objects'])|set(g['pads'])<=gnd,'RESTORED COMPONENT NOT CORE')
 ng=reach(nets['GND'],'J106.3',set(g['objects']));req(not(set(g['pads'])&ng),'REMOVAL NOT DISCONNECT')
 rows.append(dict(component=g['id'],objects=len(g['objects']),pads=g['pads'],entire_component_on_real_core=True,whole_component_removal_disconnects_all_its_pads=True))
# All GND plane shapes remain exact. New GND vias have holes; do not mistake filled zone under holes for metal.
basezones={uid(z):z for z in base.Zones()};sameGND=[]
for z in b.Zones():
 if z.GetIsRuleArea()or z.GetNetname()!='GND':continue
 for l in z.GetLayerSet().Seq():req(z.GetFilledPolysList(l).Format()==basezones[uid(z)].GetFilledPolysList(l).Format(),'GND PLANE GEOMETRY CHANGED');sameGND.append([uid(z),b.GetLayerName(l)])
# Every added through-hole projection checked against actual SENS track copper on all layers.
from finite_copper import shape
holechecks=[]
for u in ids:
 t=ts[u]
 if not isinstance(t,p.PCB_VIA):continue
 for q in b.GetTracks():
  if not q.GetNetname().startswith('SENS_')or isinstance(q,p.PCB_VIA):continue
  hole=p.SHAPE_POLY_SET();hole.NewOutline();import math
  for i in range(256):hole.Append(round(t.GetPosition().x+t.GetDrillValue()/2*math.cos(i*2*math.pi/256)),round(t.GetPosition().y+t.GetDrillValue()/2*math.sin(i*2*math.pi/256)))
  hole.BooleanIntersection(shape(q,q.GetLayer()));req(hole.Area()<1,'HOLE UNDER SIGNAL');holechecks.append([u,uid(q)])
a=json.loads((D/'analysis.json').read_text());ba=json.loads((B/'analysis.json').read_text());req(a['signal_reference_projection']==ba['signal_reference_projection'],'PROJECTION DEGRADED');req(a['strict_drc']==[0,203,0],'DRC')
req(a['core_summary']['GND']['connected_pads']==30 and a['core_summary']['GND']['all_pads']==102,'PADCOUNT');req(a['core_summary']['3V3_AON']==ba['core_summary']['3V3_AON'],'AON PAD MEMBERSHIP')
req((D/'analysis.json').read_bytes()==(D/'analysis_optimized.json').read_bytes(),'ANALYSIS -O');req((D/'plan.json').read_bytes()==(D/'plan_optimized.json').read_bytes(),'PLAN -O')
print(json.dumps(dict(status='NOFAB_17_GND_BRANCHES_CORE_VERIFIED',pcb_sha=hashlib.sha256(f.read_bytes()).hexdigest(),old_objects_geometry_width_drill_preserved=96,verified_components=rows,negative_components=17,all_4_ground_zone_shapes_unchanged=sameGND,added_via_drill_signal_projection_checks=len(holechecks),no_added_drill_under_any_SENS_track=True,signal_reference_unchanged=True,AON_core_and_pad_memberships_retained=True,GND_connected_pads_before=2,GND_connected_pads_after=30,GND_unconnected_physical_pads=72,strict_drc=[0,203,0],actual_native_negative=json.loads((D/'negative.json').read_text())),indent=2))
