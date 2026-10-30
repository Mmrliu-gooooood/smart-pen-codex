from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/pen-voids2321'
import pcbnew as p
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[2]
def circle(x,y,r):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for k in range(512):q.Append(round((x+r*math.cos(k*2*math.pi/512))*1e6),round((y+r*math.sin(k*2*math.pi/512))*1e6))
 return q
# A known rectangle with two true holes. Fracture is a serialization/representation operation.
q=p.SHAPE_POLY_SET();q.NewOutline()
for x,y in [(0,0),(10,0),(10,10),(0,10)]:q.Append(x*1000000,y*1000000)
for x,y in [(3,4),(7,6)]:q.BooleanSubtract(circle(x,y,1))
orig=p.SHAPE_POLY_SET(q);q.Fracture();fract=p.SHAPE_POLY_SET(q);norm=native_fractured_once(q)
def erosion(x):
 x=p.SHAPE_POLY_SET(x);x.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);return dict(pieces=x.OutlineCount(),area_mm2=x.Area()/1e12)
synthetic=dict(original_holes=orig.HoleCount(0),fractured_holes=fract.HoleCount(0),unfractured_holes=norm.HoleCount(0),areas_mm2=[x.Area()/1e12 for x in [orig,fract,norm]],erosion=[erosion(x)for x in [orig,fract,norm]])
if synthetic['original_holes']!=2 or synthetic['fractured_holes']!=0 or synthetic['unfractured_holes']!=2:raise RuntimeError('hole identity')
try:
 native_fractured_once(norm)
 raise RuntimeError('Repeated conversion erroneously accepted')
except RuntimeError as e:
 if 'Already has explicit holes' not in str(e):raise
synthetic['repeat_call_guard_rejected']=True
# Demonstrate why guard matters on a COPY, never returning this as usable geometry.
bad=p.SHAPE_POLY_SET(norm);bad.Unfracture();synthetic['unsafe_repeated_Unfracture_copy_area_mm2']=bad.Area()/1e12;synthetic['unsafe_repeated_Unfracture_copy_holes']=bad.HoleCount(0)
rows=[]
for name in ['power_zone_freshfill_candidate_2150','aon_entry_bridge_candidate_2156','gnd_fixed_branch_candidate_2159','gnd_conservative_recovery_2305']:
 b=p.LoadBoard(str(R/'hardware'/name/'native/mainboard_revD.kicad_pcb'))
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in z.GetLayerSet().Seq():
   raw=p.SHAPE_POLY_SET(z.GetFilledPolysList(l));norm=native_fractured_once(raw)
   for v in b.GetTracks():
    if not isinstance(v,p.PCB_VIA)or v.GetNetname()==z.GetNetname():continue
    x,y=v.GetPosition().x/1e6,v.GetPosition().y/1e6;hole=circle(x,y,v.GetDrillValue()/2e6);inside=circle(x,y,v.GetWidth(p.F_Cu)/2e6+.149)
    result=[]
    for test in [hole,inside]:
     a=p.SHAPE_POLY_SET();a.BooleanIntersection(test,raw);c=p.SHAPE_POLY_SET();c.BooleanIntersection(test,norm);result.append([a.Area()/1e12,c.Area()/1e12])
    if max(sum(result,[]))>1e-8:raise RuntimeError('physical void/149um clearance filled')
    rows.append(dict(candidate=name,zone_uuid=z.m_Uuid.AsString(),layer=b.GetLayerName(l),foreign_via=v.m_Uuid.AsString(),drill_overlap_raw_norm_mm2=result[0],annulus_plus_0149_overlap_raw_norm_mm2=result[1]))
print(json.dumps(dict(synthetic=synthetic,foreign_via_checks=len(rows),all_physical_foreign_holes_and_inside_clearance_remain_empty=True,checks=rows,limits=['Same-net drill holes are accounted by physical via geometry, not inferred from zone filled holes.','0.149mm is an interior void test, not a substitute for the 0.150mm native clearance DRC.']),indent=2))
