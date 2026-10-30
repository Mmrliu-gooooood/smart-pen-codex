from pathlib import Path
import sys,os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/pressure-ref'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'))
from finite_copper import shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());ts={t.m_Uuid.AsString():t for t in b.GetTracks()};planes={}
for z in b.Zones():
 if not z.GetIsRuleArea()and z.GetNetname()=='GND':planes.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
holes=[];hole_evidence=[]
for index in [7,30]:
 matches=[];poly=planes[p.In4_Cu];t=ts[m['added'][index]]
 for oi in range(poly.OutlineCount()):
  for hi in range(poly.HoleCount(oi)):
   h=p.SHAPE_POLY_SET();h.AddOutline(poly.Hole(oi,hi))
   if h.Contains(t.GetPosition()):matches.append(h)
 if len(matches)!=1:raise RuntimeError('one native reference hole required')
 h=matches[0];holes.append(h);bb=h.BBox()
 centers=[dict(uuid=u,net=v.GetNetname())for u,v in ts.items()if isinstance(v,p.PCB_VIA)and h.Contains(v.GetPosition())]
 hole_evidence.append(dict(index=index,bounds_mm=[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6],area_mm2=h.Area()/1e12,containing_via_centers=centers))
rows=[]
for i in range(19,30):
 t=ts[m['added'][i]];s=shape(t,t.GetLayer());q=p.SHAPE_POLY_SET(s);q.BooleanSubtract(planes[p.In4_Cu]);rawgap=q.Area()/1e12
 for h in holes:q.BooleanSubtract(h)
 if q.Area()>1:raise RuntimeError('new long reference gap beyond exact endpoint holes')
 rows.append(dict(index=i,start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],length_mm=t.GetLength()/1e6,strip_mm2=s.Area()/1e12,ground_In4_uncovered_mm2=rawgap,outside_exact_endpoint_native_holes_mm2=q.Area()/1e12))
lengths={n:sum(t.GetLength()/1e6 for t in b.GetTracks()if t.GetNetname()==n and not isinstance(t,p.PCB_VIA))for n in ['NIB_CONTACT_N','CONTACT','STRAP_GPIO3','SENS_EXTCLK']}
print(json.dumps({'exact_endpoint_native_holes':hole_evidence,'new_long_In3_reference_projection':rows,'total_planar_copper_length_mm':lengths,'open_nominal_RC_us':47.,'closed_nominal_RC_us':47000*1000/(47000+1000)*1e-3,'limits':['RC uses nominal 1nF only, excludes trace/input/cable parasitics and thresholds; not switch debounce','Long high-impedance contact net ESD/noise protection unqualified','Uncovered projection uses actual native ground holes, not ideal enlarged-via circles; endpoints/antipads require interpretation','No reference-plane tracks added; all new signal changes are F/B/In3 plus local through vias']},indent=2))
