from pathlib import Path
import os,sys,json
os.environ['XDG_CONFIG_HOME']='/tmp/unused1017holes'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());v=next(t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.m_Uuid.AsString()in m['added']);rows=[]
for signal,ref in [(p.F_Cu,p.In1_Cu),(p.B_Cu,p.In4_Cu)]:
 plane=p.SHAPE_POLY_SET();holes=[]
 for z in b.Zones():
  if z.GetIsRuleArea()or z.GetLayer()!=ref:continue
  sh=native_fractured_once(z.GetFilledPolysList(ref));plane.BooleanAdd(sh)
  for i in range(sh.OutlineCount()):
   for j in range(sh.HoleCount(i)):
    h=p.SHAPE_POLY_SET();h.AddOutline(sh.Hole(i,j))
    if h.Contains(v.GetPosition()):holes.append(h)
 if len(holes)!=1:raise RuntimeError('one actual filled-plane hole containing new via')
 h=holes[0];pins=[t.m_Uuid.AsString()for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and h.Contains(t.GetPosition())];projection=p.SHAPE_POLY_SET()
 for t in b.GetTracks():
  if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='UNUSED_B_INPUT'and t.GetLayer()==signal:projection.BooleanAdd(shape(t,signal))
 missing=p.SHAPE_POLY_SET();missing.BooleanSubtract(projection,plane);outside=p.SHAPE_POLY_SET();outside.BooleanSubtract(missing,h);bb=h.BBox();rows.append({'signal_layer':b.GetLayerName(signal),'reference_layer':b.GetLayerName(ref),'actual_hole_area_mm2':h.Area()/1e12,'actual_hole_bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6],'via_centers_in_actual_hole':pins,'new_input_uncovered_mm2':missing.Area()/1e12,'uncovered_outside_actual_hole_mm2':outside.Area()/1e12})
 if pins!=[v.m_Uuid.AsString()]or outside.Area()/1e12>1e-8:raise RuntimeError('new uncovered area not solely isolated own actual via hole')
print(json.dumps({'new_via':v.m_Uuid.AsString(),'actual_native_hole_reports':rows,'scope':'Classification uses native actual hole, no ideal/expanded-hole masking, not SI/current/thermal qualification'},indent=2))
