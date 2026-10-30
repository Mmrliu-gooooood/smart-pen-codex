from pathlib import Path
import os,sys,json
os.environ.update(XDG_CONFIG_HOME='/tmp/review1103/config',XDG_DATA_HOME='/tmp/review1103/data',XDG_CACHE_HOME='/tmp/review1103/cache')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'))
from finite_copper import shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());vias=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.m_Uuid.AsString()in m['added']]
def req(c,m):
 if not c:raise RuntimeError(m)
def holes(q,v):
 hs=[]
 for i in range(q.OutlineCount()):
  for j in range(q.HoleCount(i)):
   h=p.SHAPE_POLY_SET();h.AddOutline(q.Hole(i,j))
   if h.Contains(v.GetPosition()):hs.append(h)
 return hs
rows=[]
for layer,ref in [(p.F_Cu,p.In1_Cu),(p.B_Cu,p.In4_Cu)]:
 zones=[z for z in b.Zones()if not z.GetIsRuleArea()and z.GetLayer()==ref];req(all(z.GetNetname()=='GND'for z in zones),'reference zones GND');normalized=[native_fractured_once(z.GetFilledPolysList(ref))for z in zones];plane=p.SHAPE_POLY_SET();reverse=p.SHAPE_POLY_SET()
 for q in normalized:plane.BooleanAdd(q)
 for q in reversed(normalized):reverse.BooleanAdd(q)
 d1=p.SHAPE_POLY_SET();d1.BooleanSubtract(plane,reverse);d2=p.SHAPE_POLY_SET();d2.BooleanSubtract(reverse,plane);req(d1.Area()==d2.Area()==0,'union order area')
 for v in vias:
  hs=holes(plane,v);req(len(hs)==1,'exactly one union hole');h=hs[0];projection=p.SHAPE_POLY_SET()
  for t in b.GetTracks():
   if not isinstance(t,p.PCB_VIA)and t.GetNetname()==v.GetNetname()and t.GetLayer()==layer:projection.BooleanAdd(shape(t,layer))
  missing=p.SHAPE_POLY_SET();missing.BooleanSubtract(projection,plane);outside=p.SHAPE_POLY_SET();outside.BooleanSubtract(missing,h);req(outside.Area()==0,'no positive outside-hole area, no numerical waiver')
  other=[t.m_Uuid.AsString()for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.m_Uuid.AsString()!=v.m_Uuid.AsString()and h.Contains(t.GetPosition())];req(not other,'isolated hole')
  rows.append({'net':v.GetNetname(),'reference':b.GetLayerName(ref),'zone_count':len(zones),'per_zone_contains_hole':[len(holes(q,v))for q in normalized],'union_holes':len(hs),'union_reverse_order_material_difference_nm2':0,'actual_union_hole_area_mm2':h.Area()/1e12,'uncovered_mm2':missing.Area()/1e12,'outside_actual_union_hole_area_nm2':outside.Area(),'other_vias_in_hole':other,'zone_outline_x_ranges_mm':[[z.Outline().BBox().GetX()/1e6,z.Outline().BBox().GetRight()/1e6]for z in zones]})
(D/'independent_union_classifier.json').write_text(json.dumps({'reports':rows,'verdict':'Union before hole extraction correct; RESET per-zone notches are not a union copper gap. No expanded masks; outside-hole equality required exactly zero.'},indent=2)+'\n')
