from pathlib import Path
import os,sys,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/imu-physical0405';D=Path(__file__).resolve().parent;R=D.parents[1]
sys.path.insert(0,str(R/'hardware/imu_power_return_candidate_0333'));import geometry as g
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from native_polygon import native_fractured_once
p=g.p;m=json.loads((D/'materialization.json').read_text());g.b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));alltracks={g.desc(t):t for t in g.b.GetTracks()};g.old=[t for u,t in alltracks.items()if u not in m['added']];new=[alltracks[u]for u in m['added']];g.pads=[pad for f in g.b.GetFootprints()for pad in f.Pads()];g.cache.clear();g.outline=p.SHAPE_POLY_SET();g.b.GetBoardPolygonOutlines(g.outline)
def req(c,m):
 if not c:raise RuntimeError(m)
e=g.errors(new);req(not e,'native all finite clearance')
fps={f.GetReference():f for f in g.b.GetFootprints()};req(fps['R503'].GetValue()=='47k 1%','R503');req(fps['JP301'].GetValue()=='OPEN / DO NOT BRIDGE','JP301OPEN')
for f in fps.values():f.BuildCourtyardCaches()
cts=[]
for i,t in enumerate(new):
 if isinstance(t,p.PCB_VIA):
  for ref,f in fps.items():
   for l in [p.F_CrtYd,p.B_CrtYd]:
    a=g.shape(t,p.F_Cu);a.BooleanIntersection(f.GetCourtyard(l))
    if a.Area()>1:cts.append({'index':i,'ref':ref,'side':g.b.GetLayerName(l),'overlap_mm2':a.Area()/1e12})
req(all(x['ref']=='U501'and x['index']==15 for x in cts),'unexpected via courtyard')
planes={}
for z in g.b.Zones():
 if not z.GetIsRuleArea():planes.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
holes={};hole_evidence=[]
for layer,poly in planes.items():
 holes[layer]=[]
 for k in [29,31]:
  matches=[]
  for oi in range(poly.OutlineCount()):
   for hi in range(poly.HoleCount(oi)):
    hole=p.SHAPE_POLY_SET();hole.AddOutline(poly.Hole(oi,hi))
    if hole.Contains(new[k].GetPosition()):matches.append(hole)
  req(len(matches)==1,'one actual antipad hole per clock via')
  hole=matches[0];bb=hole.BBox();req(bb.GetWidth()<800000 and bb.GetHeight()<800000,'antipad local bounded not merged')
  holes[layer].append(hole);hole_evidence.append({'via_index':k,'layer':g.b.GetLayerName(layer),'bounds_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6],'area_mm2':hole.Area()/1e12})
rows=[]
for i in range(28,33):
 t=new[i]
 for ref in ([p.In2_Cu,p.In4_Cu]if i==30 else[p.In4_Cu]):
  a=g.shape(t,p.In3_Cu if i==30 else p.B_Cu);a.BooleanSubtract(planes[ref]);raw=a.Area()/1e12
  for k in [29,31]:a.BooleanSubtract(g.shape(new[k],ref,150000))
  nominal_residual=a.Area()/1e12
  for h in holes[ref]:a.BooleanSubtract(h)
  req(a.Area()<=1,'clock gap beyond exact native own holes')
  rows.append({'index':i,'ref':g.b.GetLayerName(ref),'total_projection_gap_mm2':raw,'outside_ideal_antipad_edge_sliver_mm2':nominal_residual,'outside_actual_native_own_holes_mm2':a.Area()/1e12})
print(json.dumps({'native_all_layer_new_copper_pad_hole_edge_rule_errors':e,'new_via_courtyard_intersections':cts,'clock_reference_coverage':rows,'exact_native_clock_antipad_holes':hole_evidence,'R503':'47k 1%','JP301':'OPEN','boundary_nominal_mm':{'JP201_courtyard_gap':.18,'J107_courtyard_gap':.43,'clock_upper_via_to_AON_copper_gap':.20,'extra_over_rule_not_manufacturing_tolerance':.05},'mechanics_link':'../../docs/electronics/imu_access_corridor_0345/mechanical_screen.json','mechanics_scope':'same J107 case2 pose; full2mm budget four contexts; no actual harness/assembly/stress qualification'},indent=2))
