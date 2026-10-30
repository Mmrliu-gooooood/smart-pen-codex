from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/control-reference0543'
import pcbnew as p
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[1];a=p.LoadBoard(str(R/'hardware/pressure_joint_native_0433/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))
def req(c,m):
 if not c:raise RuntimeError(m)
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
pa,pb=planes(a),planes(b);t=next(t for t in b.GetTracks()if t.m_Uuid.AsString()=='eba5b185-27fd-57f9-b1a5-37b4fa4d4ec8');shape=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(shape,t.GetLayer(),0,100,p.ERROR_INSIDE);rows=[]
for l in [p.In2_Cu,p.In4_Cu]:
 x=p.SHAPE_POLY_SET();x.BooleanIntersection(shape,pa[l]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(shape,pb[l]);x.BooleanSubtract(y);bb=x.BBox();area=x.Area()/1e12;req(abs(area-.0017414094705)<1e-10,'native loss remains nonzero')
 rows.append({'plane':b.GetLayerName(l),'additional_clock_projection_loss_mm2':area,'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6],'center_at_loss_y_inside':x.Contains(p.VECTOR2I(4250000,80100000))})
q=p.SHAPE_POLY_SET(pb[p.In2_Cu]);q.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);parts=[]
for i in range(q.OutlineCount()):
 u=q.UnitSet(i);bb=u.BBox();parts.append({'area_mm2':u.Area()/1e12,'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6]})
req(len(parts)==2,'AON eroded 2');req(min(x['area_mm2']for x in parts)<.006 and max(x['area_mm2']for x in parts)>750,'tiny island plus main')
print(json.dumps({'actual_loss_not_waived':rows,'AON_025_eroded_components':parts,'interpretation':'Positive clock edge loss is a gate, not erased with enlarged hole subtraction. Tiny erosion island is not proof of main backbone split or current qualification.'},indent=2))
