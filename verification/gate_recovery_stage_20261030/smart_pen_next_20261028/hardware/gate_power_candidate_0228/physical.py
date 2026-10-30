from pathlib import Path
import sys,os,json,contextlib,io
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'docs/electronics/remaining_power_return_plan_0208'))
with contextlib.redirect_stdout(io.StringIO()):import plan as q
p=q.p;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());ts={q.uid(t):t for t in b.GetTracks()};new=[ts[u]for u in m['added']]
e=q.errors(new)
if e:raise RuntimeError(str(e))
c=[]
for t in new:
 if not isinstance(t,p.PCB_VIA):continue
 for f in b.GetFootprints():
  f.BuildCourtyardCaches()
  for side in [p.F_CrtYd,p.B_CrtYd]:
   z=f.GetCourtyard(side);x=p.SHAPE_POLY_SET();x.BooleanIntersection(q.shape(t,p.F_Cu),z)
   if x.Area()>1:c.append([f.GetReference(),b.GetLayerName(side),x.Area()/1e12])
if c:raise RuntimeError(str(c))
from native_polygon import native_fractured_once
v=new[3];distance=[]
for z in b.Zones():
 if z.GetIsRuleArea()or z.GetNetname()!='3V3_AON':continue
 poly=native_fractured_once(z.GetFilledPolysList(z.GetLayer()));cut=q.shape(v,z.GetLayer(),150000);x=p.SHAPE_POLY_SET();x.BooleanIntersection(poly,cut)
 distance.append(dict(zone=q.uid(z),antipad_nominal_overlap_mm2=x.Area()/1e12,center_to_copper_mm=poly.Distance(v.GetPosition())/1e6,nominal_radius_mm=.45))
print(json.dumps(dict(all_layer_new_old_clearance_pass=True,same_net_pad_exclusion_pass=True,edge_rule_hole_checks_pass=True,courtyard_overlap=c,AON_antipad_actual=distance,limits=['Nominal geometry only; .05mm margin has no manufacturing tolerance qualification','No current, thermal, load, battery or IPC qualification']),indent=2))
