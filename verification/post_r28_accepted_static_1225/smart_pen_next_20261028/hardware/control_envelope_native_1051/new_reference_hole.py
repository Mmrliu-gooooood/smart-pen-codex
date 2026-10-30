from pathlib import Path
import os,sys,json
os.environ['XDG_CONFIG_HOME']='/tmp/unused1017holes'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());vs=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.m_Uuid.AsString()in m['added']];rows=[]
for v in vs:
 for signal,ref in [(p.F_Cu,p.In1_Cu),(p.B_Cu,p.In4_Cu)]:
  plane=p.SHAPE_POLY_SET();holes=[];zone_holes=[]
  for z in b.Zones():
   if z.GetIsRuleArea()or z.GetLayer()!=ref:continue
   if z.GetNetname()!='GND':raise RuntimeError('unexpected reference net')
   sh=native_fractured_once(z.GetFilledPolysList(ref));plane.BooleanAdd(sh)
   count=0
   for oi in range(sh.OutlineCount()):
    for hi in range(sh.HoleCount(oi)):
     zz=p.SHAPE_POLY_SET();zz.AddOutline(sh.Hole(oi,hi));count+=bool(zz.Contains(v.GetPosition()))
   zone_holes.append(count)
  # Adjacent same-net zones overlap x11.4..11.7: classify the UNION, not individual zone edge notches.
  for i in range(plane.OutlineCount()):
   for j in range(plane.HoleCount(i)):
    h=p.SHAPE_POLY_SET();h.AddOutline(plane.Hole(i,j))
    if h.Contains(v.GetPosition()):holes.append(h)
  if len(holes)!=1:raise RuntimeError('one actual filled-plane hole containing new via')
  h=holes[0];pins=[t.m_Uuid.AsString()for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and h.Contains(t.GetPosition())];projection=p.SHAPE_POLY_SET()
  for t in b.GetTracks():
   if not isinstance(t,p.PCB_VIA)and t.GetNetname()==v.GetNetname()and t.GetLayer()==signal:projection.BooleanAdd(shape(t,signal))
  missing=p.SHAPE_POLY_SET();missing.BooleanSubtract(projection,plane);outside=p.SHAPE_POLY_SET();outside.BooleanSubtract(missing,h);bb=h.BBox();rows.append({'net':v.GetNetname(),'via':v.m_Uuid.AsString(),'signal_layer':b.GetLayerName(signal),'reference_layer':b.GetLayerName(ref),'per_zone_containing_hole_counts':zone_holes,'union_containing_holes':len(holes),'actual_hole_area_mm2':h.Area()/1e12,'actual_hole_bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6],'via_centers_in_actual_hole':pins,'new_input_uncovered_mm2':missing.Area()/1e12,'uncovered_outside_actual_hole_mm2':outside.Area()/1e12})
  if pins!=[v.m_Uuid.AsString()]or outside.Area()/1e12>1e-8:raise RuntimeError('new uncovered area not solely isolated own actual via hole')
print(json.dumps({'new_vias':[v.m_Uuid.AsString()for v in vs],'actual_native_hole_reports':rows,'scope':'Classification uses native actual hole of same-layer filled-zone UNION (not individual zone edge notches), no ideal/expanded-hole masking, not SI/current/thermal qualification'},indent=2))
