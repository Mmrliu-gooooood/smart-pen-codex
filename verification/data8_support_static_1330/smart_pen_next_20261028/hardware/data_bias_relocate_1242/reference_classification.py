from pathlib import Path
import os,sys,json
os.environ['XDG_CONFIG_HOME']='/tmp/sccb1131refs'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from finite_copper import shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());ts=list(b.GetTracks());rows=[]
for net in (['CAM_D'+str(i)for i in range(8)]+['GND']):
 for layer,ref in [(p.F_Cu,p.In1_Cu),(p.B_Cu,p.In4_Cu),(p.In3_Cu,p.In2_Cu),(p.In3_Cu,p.In4_Cu)]:
  projection=p.SHAPE_POLY_SET()
  for t in ts:
   if t.m_Uuid.AsString()in m['added']and not isinstance(t,p.PCB_VIA)and t.GetNetname()==net and t.GetLayer()==layer:projection.BooleanAdd(shape(t,layer))
  if not projection.OutlineCount():continue
  plane=p.SHAPE_POLY_SET();pn=set()
  for z in b.Zones():
   if not z.GetIsRuleArea()and z.GetLayer()==ref:plane.BooleanAdd(native_fractured_once(z.GetFilledPolysList(ref)));pn.add(z.GetNetname())
  missing=p.SHAPE_POLY_SET();missing.BooleanSubtract(projection,plane);own=p.SHAPE_POLY_SET();hole_rows=[]
  for i in range(plane.OutlineCount()):
   for j in range(plane.HoleCount(i)):
    h=p.SHAPE_POLY_SET();h.AddOutline(plane.Hole(i,j));q=p.SHAPE_POLY_SET();q.BooleanIntersection(h,missing)
    if q.Area()<=0:continue
    vias=[{'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'added':t.m_Uuid.AsString()in m['added']}for t in ts if isinstance(t,p.PCB_VIA)and h.Contains(t.GetPosition())]
    isolated_own=bool(vias)and all(t['net']==net and t['added']for t in vias)
    if isolated_own:own.BooleanAdd(h)
    hole_rows.append({'area_uncovered_mm2':q.Area()/1e12,'via_centers':vias,'isolated_own_new_vias':isolated_own})
  other=p.SHAPE_POLY_SET();other.BooleanSubtract(missing,own)
  rows.append({'net':net,'layer':b.GetLayerName(layer),'reference_layer':b.GetLayerName(ref),'reference_plane_nets':sorted(pn),'uncovered_mm2':missing.Area()/1e12,'uncovered_outside_isolated_own_new_via_holes_mm2':other.Area()/1e12,'intersecting_native_union_holes':hole_rows})
print(json.dumps({'reports':rows,'scope':'Actual filled same-layer union; all new paths disclosed, not an automatic reference acceptance. In2 is mixed power-plane union, not necessarily GND.'},indent=2))
