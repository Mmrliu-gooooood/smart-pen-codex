import sys,json,math,hashlib
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad-python3/lib'])
import FreeCAD as A,Part
R=Path(__file__).resolve().parent;raw=json.loads((R/'input.json').read_text());env=json.loads((R/'envelopes_snapshot.json').read_text());prior=json.loads((R.parent/'rf_width14_mixed_final_screen/input.json').read_text());applied=json.loads((R.parent/'rf_width14_mixed_final_screen/results.json').read_text());y=applied['best']['main_B_y'];V=A.Vector
if hashlib.sha256(Path(raw['source']).read_bytes()).hexdigest()!=raw['sha256']:raise RuntimeError('Changed native')
new={p['ref']:p for p in raw['parts']}
for p in prior['parts']:
 if p!=new[p['ref']]:raise RuntimeError('Prior entity changed '+p['ref'])
def box(bounds,h,side='B'):
 a,b,c,d=bounds;lo=y-h if side=='B' else y+.93
 return Part.makeBox(c-a,h,d-b,V(a-7,lo,127-d))
def radial(bounds,h,side='B'):
 a,b,c,d=bounds;ys=[y-h,y] if side=='B' else [y+.93,y+.93+h]
 return max(math.hypot(x-7,v) for x in [a,c] for v in ys)
existing={p['ref']:box(p['bounds'],p['height_total'],p['side']) for p in applied['applied_parts'] if not p['dnp']}
existing['refill']=Part.makeCylinder(1.175,67,V(0,-3.8,0));existing['contact']=Part.makeCylinder(3,12,V(0,-3.8,68));existing['power']=Part.makeBox(14,4.15,45,V(-7,y-5.9,82))
wiredata=[];wires={};con=None
for e in env['new_footprints']:
 for p in e['pads']:
  if p['pin'] and new[e['ref']]['nets'][p['pin']]!=p['net']:raise RuntimeError('New net mismatch')
 for w in e.get('resident_wire_envelopes',[]):
  name=e['ref']+'.'+w['pin'];bounds=w['board_xy_bbox_mm'];h=w['depth_below_B_copper_mm'];wires[name]=box(bounds,h);wiredata.append(dict(name=name,bounds=bounds,height=h,radius=radial(bounds,h)))
 if e['ref']=='J202':con=e['connector_envelopes']
closed=box(con['closed_conservative_board_xy'],con['closed_depth_below_B']);opened=box(con['open_conservative_board_xy'],con['open_depth_below_B'])
newsolids={**wires,'J202_closed':closed};hits=[]
for name,s in newsolids.items():
 for other,t in existing.items():
  v=s.common(t).Volume
  if v>1e-8:hits.append(dict(a=name,b=other,volume=v))
for i,(name,s) in enumerate(newsolids.items()):
 for other,t in list(newsolids.items())[i+1:]:
  v=s.common(t).Volume
  if v>1e-8:hits.append(dict(a=name,b=other,volume=v))
openhits=[]
for name,s in {**existing,**wires}.items():
 v=opened.common(s).Volume
 if v>1e-8:openhits.append(dict(other=name,volume=v))
# A rejected route example: extend same-height solder-column rectangles toward head.
straight=[]
for w in wiredata:
 a,b,c,d=w['bounds'];route=box([a,b,c,99],2.)
 straight.append(dict(name=w['name'],connector_closed_overlap_mm3=route.common(closed).Volume,connector_open_overlap_mm3=route.common(opened).Volume))
clear=.2;openbottom=y-con['open_depth_below_B'];refilltop=-3.8+1.175
corridor=dict(assumption='Only necessary empty cross-section bounds, not routed bundle approval; clearance0.2 study allowance, no wire selected',top_max_for_open=openbottom-clear,bottom_min_above_refill=refilltop+clear,available_height=openbottom-refilltop-2*clear,at_center_Y_minus1_max_radius=min(openbottom-clear+1,-1-refilltop-clear),wire_count=len(wires),bend_radius_and_strain_relief='UNSPECIFIED: cannot qualify full fanout/FPC exit')
result=dict(status='LOCAL_ENVELOPES_ONLY_HARNESS_ROUTE_NOT_APPROVED',source_sha256=raw['sha256'],count=raw['count'],old79_equal=True,main_B_y=y,new_wire_solder_envelopes=wiredata,connector_closed_radius=radial(con['closed_conservative_board_xy'],con['closed_depth_below_B']),local_collision_hits=hits,open_sweep_hits=openhits,rejected_straight_routes=straight,low_corridor_requirements=corridor)
print(json.dumps(result,indent=2))
