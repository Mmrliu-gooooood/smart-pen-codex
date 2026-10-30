from pathlib import Path
import os,sys,json
os.environ['XDG_CONFIG_HOME']='/tmp/imucontrol-neck0522'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from native_polygon import native_fractured_once
out=[]
for label,path in [('parent',D.parent/'pressure_joint_native_0433/native/mainboard_revD.kicad_pcb'),('candidate',D/'native/mainboard_revD.kicad_pcb')]:
 b=p.LoadBoard(str(path));z=next(z for z in b.Zones()if not z.GetIsRuleArea()and z.GetNetname()=='3V3_AON');q=native_fractured_once(z.GetFilledPolysList(z.GetLayer()));rows=[]
 for radius in[.1,.15,.2,.25]:
  e=p.SHAPE_POLY_SET(q);e.Deflate(round(radius*1e6),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);cs=[]
  for oi in range(e.OutlineCount()):
   part=e.UnitSet(oi);bb=part.BBox();cs.append({'area_mm2':part.Area()/1e12,'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6]})
  rows.append({'erosion_radius_mm':radius,'components':cs})
 out.append({'board':label,'normalized_outline_count':q.OutlineCount(),'normalized_holes':sum(q.HoleCount(i)for i in range(q.OutlineCount())),'screens':rows})
print(json.dumps({'status':'GEOMETRIC_NECK_SCREEN_NOT_CURRENT_RATING','boards':out,'limits':['Guarded native fracture removal applied once to native polygons; no repeated canonical Unfracture','Erosion is a geometric screening operation, not actual disconnection or current capacity','Components include possible small islands; inspect coordinates before inferring affected power paths']},indent=2))
