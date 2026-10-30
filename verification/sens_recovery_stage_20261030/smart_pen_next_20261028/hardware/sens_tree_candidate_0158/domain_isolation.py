from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/sens-isolation0158'
import pcbnew as p
from finite_copper import build
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));nodes=build(b);bad=[]
for name,_,s in nodes['SENS_VIO_1V8']:
 for net in ['3V3_AON','GND','CAM_3V3_SW']:
  for other,_,t in nodes[net]:
   for l in s.keys()&t.keys():
    if not s[l].BBox().Intersects(t[l].BBox()):continue
    z=p.SHAPE_POLY_SET();z.BooleanIntersection(s[l],t[l])
    if z.Area()>1:bad.append([name,net,other,b.GetLayerName(l),z.Area()])
if bad:raise RuntimeError(str(bad))
print(json.dumps(dict(SENS_to_other_domains_physical_intersections=bad,checked_domains=['3V3_AON','GND','CAM_3V3_SW'],method='finite physical copper including pads/tracks/vias/filled zone units; via drill removed',limits='Nominal geometry only; not powered backfeed or voltage isolation test'),indent=2))
