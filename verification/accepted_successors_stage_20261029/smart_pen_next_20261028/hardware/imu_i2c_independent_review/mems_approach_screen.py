from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
from copper_geometry import shape
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))
def rect(x,y,z,w):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for a,c in[(x,y),(z,y),(z,w),(x,w)]:q.Append(round(a*1e6),round(c*1e6))
 return q
body=rect(3,81,5,83);u=next(f for f in b.GetFootprints()if f.GetReference()=='U501');pads=p.SHAPE_POLY_SET()
for pad in u.Pads():pads.BooleanAdd(shape(pad,p.F_Cu))
bands={'AON_I2C_SCL':rect(3,81.075,3.2375,81.425),'AON_I2C_SDA':rect(3,82.575,3.2375,82.925)};out=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)or t.GetLayer()!=p.F_Cu or t.GetNetname()not in bands:continue
 ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(shape(t,p.F_Cu),body)
 if ix.Area()<=1:continue
 outside=p.SHAPE_POLY_SET();outside.BooleanSubtract(ix,pads);remaining=p.SHAPE_POLY_SET();remaining.BooleanSubtract(outside,bands[t.GetNetname()]);out.append({'net':t.GetNetname(),'uuid':t.m_Uuid.AsString(),'a':[t.GetStart().x/1e6,t.GetStart().y/1e6],'z':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'inside_body_mm2':ix.Area()/1e12,'outside_all_native_pads_mm2':outside.Area()/1e12,'outside_necessary_left_approach_mm2':remaining.Area()/1e12})
r={'note':'Only new bus F escape into outer half-land. Bands are explicit project geometric interpretation, not manufacturer exact exception. Central rule and fullbody via/pour independently verified; inherited peripheral links still manual gate.','rows':out,'nonapproach_area_mm2':sum(q['outside_necessary_left_approach_mm2']for q in out)};(D/'mems_approach_screen.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
