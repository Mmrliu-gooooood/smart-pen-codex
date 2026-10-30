from pathlib import Path
import os,json,sys
os.environ['XDG_CONFIG_HOME']='/tmp/imu-ownholes0416'
import pcbnew as p
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());ts={t.m_Uuid.AsString():t for t in b.GetTracks()};new=[ts[u]for u in m['added']]
def req(c,m):
 if not c:raise RuntimeError(m)
planes={}
for z in b.Zones():
 if not z.GetIsRuleArea():planes.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
rows=[]
for i in range(19,30):
 t=new[i]
 for layer in [p.In4_Cu]:
  q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,p.In3_Cu,0,100,p.ERROR_INSIDE);q.BooleanSubtract(planes[layer]);raw=q.Area()/1e12;holes=[]
  for vi in [7,30]:
   matches=[];plane=planes[layer]
   for oi in range(plane.OutlineCount()):
    for hi in range(plane.HoleCount(oi)):
     h=p.SHAPE_POLY_SET();h.AddOutline(plane.Hole(oi,hi))
     if h.Contains(new[vi].GetPosition()):matches.append(h)
   req(len(matches)==1,'unique actual native hole');h=matches[0];bb=h.BBox();q.BooleanSubtract(h);holes.append({'via':vi,'bbox':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6]})
  req(q.Area()<=1,'uncovered copper outside exact actual holes');rows.append({'object':i,'plane':b.GetLayerName(layer),'raw_gap_mm2':raw,'only_exact_holes_subtracted_residual_mm2':q.Area()/1e12,'holes':holes})
print(json.dumps({'method':'Subtract actual native contour only, no preceding ideal disk and no relaxed area tolerance','rows':rows},indent=2))
