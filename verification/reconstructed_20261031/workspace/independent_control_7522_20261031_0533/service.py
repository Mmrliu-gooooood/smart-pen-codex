from pathlib import Path
import os,json,hashlib,math
os.makedirs('/tmp/service0520',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/service0520';import pcbnew as p
O=Path(__file__).resolve().parent;sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
b=p.LoadBoard(str(O/'selected_native.kicad_pcb'));f=next(f for f in b.GetFootprints()if f.GetReference()=='J104');f.BuildCourtyardCaches();court=f.GetCourtyard(p.B_CrtYd);need(court.OutlineCount()==1 and court.HoleCount(0)==0,'native single court');c=court.Outline(0);pts=[(c.CPoint(i).x,c.CPoint(i).y)for i in range(c.PointCount())];bb=[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)];ex=[bb[0]-50000,bb[1]-50000,bb[2]+50000,bb[3]+50000]
def rect(a):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for x,y in [(a[0],a[1]),(a[2],a[1]),(a[2],a[3]),(a[0],a[3])]:q.Append(x,y)
 return q
service=rect(ex);ids=set(json.load(open(O/'native_derived_delta.json'))['added']);allowed={'CAM_RESET_UART_TX':('1',(10000000,53000000),(8600000,53000000)),'CAM_PWDN_UART_RX':('2',(10000000,54800000),(11900000,55500000))};hits=[]
for t in b.GetTracks():
 if t.m_Uuid.AsString()not in ids or not t.IsOnLayer(p.B_Cu):continue
 s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,p.B_Cu,0,50,p.ERROR_OUTSIDE)
 for label,q in [('actual_cached_court',court),('historical_planning_rectangle_plus_0p05_not_measured',service)]:
  common=p.SHAPE_POLY_SET();common.BooleanIntersection(s,q);area=common.Area()/1e12
  if area<1e-8:continue
  need(not isinstance(t,p.PCB_VIA),'no via allowed in service footprint');need(t.GetNetname()in allowed,'no unrelated service overlap');pad,a,z=allowed[t.GetNetname()];need((t.GetStart().x,t.GetStart().y)==a and(t.GetEnd().x,t.GetEnd().y)==z and t.GetWidth()==150000,'only exact terminal segment');pp=next(v for v in f.Pads()if v.GetNumber()==pad);need(pp.IsOnLayer(p.B_Cu)and(pp.GetPosition().x,pp.GetPosition().y)==a and pp.GetNetname()==t.GetNetname(),'actual terminal');need(common.OutlineCount()==1 and common.HoleCount(0)==0,'single connected escape overlap');need(z[0]<ex[0]or z[0]>ex[2]or z[1]<ex[1]or z[1]>ex[3],'exits expanded rectangle');hits.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'pad':pad,'region':label,'area_mm2':area,'single_connected_pad_ended_segment':True})
need(len(hits)==4,'exact two terminal escapes in both definitions')
# Deliberate nonterminal horizontal crossing must intersect both definitions, not be admitted by target net alone.
t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(8000000,56000000));t.SetEnd(p.VECTOR2I(12000000,56000000));t.SetWidth(150000);t.SetLayer(p.B_Cu);t.SetNetCode(next(v for v in f.Pads()if v.GetNumber()=='1').GetNetCode());need(t.GetNetname()in allowed,'negative uses allowed net');_,na,nz=allowed[t.GetNetname()];need(not((t.GetStart().x,t.GetStart().y)==na and(t.GetEnd().x,t.GetEnd().y)==nz),'negative must fail exact terminal guard');s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,p.B_Cu,0,50,p.ERROR_OUTSIDE);neg=[]
for q in [court,service]:
 common=p.SHAPE_POLY_SET();common.BooleanIntersection(s,q);need(common.Area()>1e8,'negative service crossing');neg.append(common.Area()/1e12)
(O/'service_results.json').write_text(json.dumps({'pcb_sha256':sha(O/'selected_native.kicad_pcb'),'actual_cached_court_bounds_mm':[x/1e6 for x in bb],'expanded_planning_bounds_mm':[x/1e6 for x in ex],'expanded_bound_basis':'actual native vertex bbox +0.05 each side, historical conservative planning only, NOT measured service/tool/probe envelope','allowed_actual_terminal_escapes':hits,'no_other_new_B_copper_or_via_intersections':True,'negative_nonterminal_crossing_areas_mm2':neg,'negative_same_net_fails_exact_terminal_guard':True,'probe_access_electrical_camera_off_and_manufacturing_gates_still_open':True},indent=2)+'\n')
