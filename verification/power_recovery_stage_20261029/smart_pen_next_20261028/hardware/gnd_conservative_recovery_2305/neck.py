from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-gndneck2159'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(R/'hardware/aon_entry_bridge_candidate_2156/native/mainboard_revD.kicad_pcb'))
def aon(b):
 z=next(z for z in b.Zones()if z.GetNetname()=='3V3_AON');a=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In2_Cu));a.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);return a
a=aon(b);old=aon(base);rows=[]
for i in range(a.OutlineCount()):
 q=a.UnitSet(i);bb=q.BBox();matches=[]
 for j in range(old.OutlineCount()):
  x=p.SHAPE_POLY_SET();x.BooleanIntersection(q,old.UnitSet(j))
  if x.Area()>1:matches.append(dict(base_fragment=j,overlap_mm2=x.Area()/1e12))
 rows.append(dict(fragment=i,area_mm2=q.Area()/1e12,bbox_mm=[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6],base_matches=matches))
print(json.dumps(dict(erosion_radius_mm=.25,base_fragment_count=old.OutlineCount(),candidate_fragment_count=a.OutlineCount(),fragments=rows,note='Screening shape erosion only, not load-path minimum-neck/ampacity proof. Added via antipads may create splits; report does not waive the change.'),indent=2))
