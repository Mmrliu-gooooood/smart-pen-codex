from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/gate-detail0228'
import pcbnew as p
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[1];a=p.LoadBoard(str(R/'hardware/sens_tree_candidate_0158/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));out=[]
for x in a.Zones():
 if x.GetIsRuleArea():continue
 y=next(z for z in b.Zones()if z.m_Uuid==x.m_Uuid);l=x.GetLayer();v=native_fractured_once(x.GetFilledPolysList(l));w=native_fractured_once(y.GetFilledPolysList(l));q=p.SHAPE_POLY_SET();q.BooleanSubtract(v,w);parts=[]
 for i in range(q.OutlineCount()):
  line=q.Outline(i);bb=line.BBox();parts.append(dict(area_mm2=line.Area()/1e12,bbox_mm=[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6]))
 out.append(dict(net=x.GetNetname(),layer=b.GetLayerName(l),lost_parts=parts))
print(json.dumps(out,indent=2))
