from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/gnd-holecheck2322'
import pcbnew as p
D=Path(__file__).resolve().parent;H=D.parent

def circle(x,y,r):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for k in range(512):q.Append(round(x+r*math.cos(k*math.tau/512)),round(y+r*math.sin(k*math.tau/512)))
 return q
rows=[]
for v in ['aon_entry_bridge_candidate_2156','gnd_fixed_branch_candidate_2159','gnd_conservative_recovery_2305']:
 b=p.LoadBoard(str(H/v/'native/mainboard_revD.kicad_pcb'));n=0;maxarea=0;own=0
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for layer in z.GetLayerSet().Seq():
   q=p.SHAPE_POLY_SET(z.GetFilledPolysList(layer));q.Unfracture()
   for t in b.GetTracks():
    if not isinstance(t,p.PCB_VIA) or not t.IsOnLayer(layer):continue
    if t.GetNetname()==z.GetNetname():own+=1;continue
    c=t.GetPosition();h=circle(c.x,c.y,t.GetDrillValue()/2);a=p.SHAPE_POLY_SET();a.BooleanIntersection(q,h);area=a.Area()/1e12;maxarea=max(maxarea,area);n+=1
    if area>1e-8:raise RuntimeError(('foreign drill filled',v,z.GetNetname(),t.m_Uuid.AsString(),area))
 rows.append({'variant':v,'foreign_drill_tests':n,'max_overlap_mm2':maxarea,'same_net_via_zone_projection_excluded':own,'same_net_note':'Physical own-net drill subtraction belongs to conductor model, not assumed from same-net zone fill.'})
# independent exact rectangular hole specimen
q=p.SHAPE_POLY_SET();q.NewOutline()
for x,y in [(0,0),(10,0),(10,10),(0,10)]:q.Append(x*1000000,y*1000000)
h=p.SHAPE_POLY_SET();h.NewOutline()
for x,y in [(4,4),(6,4),(6,6),(4,6)]:h.Append(x*1000000,y*1000000)
q.BooleanSubtract(h);f=p.SHAPE_POLY_SET(q);f.Fracture();u=p.SHAPE_POLY_SET(f);u.Unfracture();delta=p.SHAPE_POLY_SET();delta.BooleanXor(q,u)
if q.HoleCount(0)!=1 or u.HoleCount(0)!=1 or u.Contains(p.VECTOR2I(5000000,5000000)) or delta.Area()>1:raise RuntimeError('synthetic hole lost')
qe=p.SHAPE_POLY_SET(q);qe.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);fe=p.SHAPE_POLY_SET(f);fe.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);ue=p.SHAPE_POLY_SET(u);ue.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
synthetic={'expected_area_mm2':96,'canonical_area_mm2':q.Area()/1e12,'fractured_area_mm2':f.Area()/1e12,'restored_area_mm2':u.Area()/1e12,'restored_holes':u.HoleCount(0),'xor_mm2':delta.Area()/1e12,'hole_center_false':not u.Contains(p.VECTOR2I(5000000,5000000)),'canonical_eroded_area_mm2':qe.Area()/1e12,'raw_fractured_eroded_area_mm2':fe.Area()/1e12,'restored_eroded_area_mm2':ue.Area()/1e12}
bad=p.SHAPE_POLY_SET(q);bad.Unfracture();synthetic['incorrect_second_unfracture_area_mm2']=bad.Area()/1e12;synthetic['incorrect_second_unfracture_holes']=bad.HoleCount(0)
(D/'hole_checks.json').write_text(json.dumps({'real_via_holes':rows,'synthetic':synthetic},indent=2));print(json.dumps(synthetic,indent=2))
