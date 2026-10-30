from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
from copper_geometry import shape,L
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));a=p.LoadBoard(str(D.parent/'j107_mode_port_closure/native/mainboard_revD.kicad_pcb'));xy=lambda v:[v.x/1e6,v.y/1e6]
def stats(b,net):
 ts=[t for t in b.GetTracks()if t.GetNetname()==net];return{'tracks':sum(not isinstance(t,p.PCB_VIA)for t in ts),'vias':sum(isinstance(t,p.PCB_VIA)for t in ts),'track_length_mm':sum(t.GetLength()/1e6 for t in ts if not isinstance(t,p.PCB_VIA)),'tracks_below_0p1_mm':sum(t.GetLength()<100000 for t in ts if not isinstance(t,p.PCB_VIA))}
plane={}
for layer in [p.In1_Cu,p.In4_Cu]:
 q=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea()and z.GetNetname()=='GND'and z.IsOnLayer(layer):q.BooleanAdd(z.GetFilledPolysList(layer))
 plane[layer]=q
rows=[]
for t in b.GetTracks():
 if t.GetNetname()!='PICKUP_INT_N'or isinstance(t,p.PCB_VIA):continue
 ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;q=shape(t,t.GetLayer());ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(q,plane[ref]);length=t.GetLength()/1e6;steps=max(1,math.ceil(length/.025));v0=t.GetStart();v1=t.GetEnd();runs=[];start=None
 for i in range(steps+1):
  v=p.VECTOR2I(round(v0.x+(v1.x-v0.x)*i/steps),round(v0.y+(v1.y-v0.y)*i/steps));inside=plane[ref].Contains(v)
  if not inside and start is None:start=i
  if inside and start is not None:runs.append((i-start)*length/steps);start=None
 if start is not None:runs.append((steps-start)*length/steps)
 rows.append({'uuid':t.m_Uuid.AsString(),'layer':b.GetLayerName(t.GetLayer()),'a':xy(t.GetStart()),'z':xy(t.GetEnd()),'reference':b.GetLayerName(ref),'length_mm':length,'projected_area_mm2':q.Area()/1e12,'uncovered_projected_area_mm2':(q.Area()-ix.Area())/1e12,'per_segment_centerline_uncovered_runs_mm':runs})
gvias=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND'];viarefs=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)and t.GetNetname()=='PICKUP_INT_N':
  vv=sorted(gvias,key=lambda q:math.dist(xy(q.GetPosition()),xy(t.GetPosition())))[:3];viarefs.append({'signal_via':t.m_Uuid.AsString(),'xy_mm':xy(t.GetPosition()),'nearest_existing_GND_vias':[{'uuid':q.m_Uuid.AsString(),'xy_mm':xy(q.GetPosition()),'center_distance_mm':math.dist(xy(q.GetPosition()),xy(t.GetPosition()))}for q in vv]})
body=p.SHAPE_POLY_SET();body.NewOutline()
for x,y in[(3,81),(5,81),(5,83),(3,83)]:body.Append(p.FromMM(x),p.FromMM(y))
u=next(f for f in b.GetFootprints()if f.GetReference()=='U501');pads=p.SHAPE_POLY_SET()
for q in u.Pads():pads.BooleanAdd(shape(q,p.F_Cu))
approach=p.SHAPE_POLY_SET();approach.NewOutline()
for x,y in[(3.575,81),(3.925,81),(3.925,81.2375),(3.575,81.2375)]:approach.Append(p.FromMM(x),p.FromMM(y))
new_f=[]
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='PICKUP_INT_N'and t.GetLayer()==p.F_Cu:
  ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(body,shape(t,p.F_Cu));outside=p.SHAPE_POLY_SET();outside.BooleanSubtract(ix,pads)
  remaining=p.SHAPE_POLY_SET();remaining.BooleanSubtract(outside,approach)
  if ix.Area()>1:new_f.append({'uuid':t.m_Uuid.AsString(),'inside_nominal_body_mm2':ix.Area()/1e12,'outside_native_U501_lands_mm2':outside.Area()/1e12,'outside_explicit_pin12_outward_approach_mm2':remaining.Area()/1e12,'project_approach_rectangle_mm':[3.575,81,3.925,81.2375],'approach_status':'Necessary connection from nominal body edge to native outer half-land; project interpretation, not manufacturer exact approved exemption'})
r={'status':'PROJECTED_REFERENCE_AND_LENGTH_SCREEN_NOT_SIGNAL_INTEGRITY_OR_WAKEUP_QUALIFICATION','native_net_length_note':'Sum of all copper track centerlines, excludes pad traversal and via electrical delay. 117.439382mm long path excludes MCU fanout; full native IRQ net reported below.','net_stats':{n:{'before':stats(a,n),'after':stats(b,n)}for n in['PICKUP_INT_N','BOOT_N','AON_I2C_SCL','AON_I2C_SDA']},'maximum_per_segment_gap_mm':max((v for r in rows for v in r['per_segment_centerline_uncovered_runs_mm']),default=0),'via_return_geometry':viarefs,'new_IRQ_F_body_intersections':new_f,'rows':rows};(D/'reference_and_lengths.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items()if k!='rows'},indent=2))
