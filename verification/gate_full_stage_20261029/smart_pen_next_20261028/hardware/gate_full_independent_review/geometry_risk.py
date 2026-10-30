from pathlib import Path
import json,collections,math
D=Path(__file__).resolve().parent
s=(D/'audit.py').read_text();exec(compile(s[:s.index('na,nb=build')],__file__,'exec'))
nb=build(b);critical={'CAM_PWR_EN','CAM_ON','CAM_CT','CAM_QOD','CAM_3V3_PRELINK','CAM_3V3_SW'};hits=[]
for net in sorted(critical):
 for other in sorted(nb):
  if net==other or (other in critical and other<net):continue
  for name,_,ss in nb[net]:
   for oname,_,oo in nb[other]:
    for l in ss.keys()&oo.keys():
     if not ss[l].BBox().Intersects(oo[l].BBox()):continue
     q=p.SHAPE_POLY_SET();q.BooleanIntersection(ss[l],oo[l])
     if q.Area()>1:hits.append([net,other,name,oname,b.GetLayerName(l),q.Area()/1e12])
require(not hits,'Cross-net finite copper overlap on gate net '+str(hits))
keep=p.SHAPE_POLY_SET();keep.NewOutline()
for x,y in [(5.5,-6.5),(12,-6.5),(12,0),(5.5,0)]:keep.Append(p.FromMM(x),p.FromMM(y))
rfhits=[]
for net,nodes in nb.items():
 for name,ispad,ss in nodes:
  for l,q in ss.items():
   ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(q,keep)
   if ix.Area()<=1:continue
   if ispad and name.startswith('AE101.'):continue
   t=next((t for t in b.GetTracks() if t.m_Uuid.AsString()==name),None)
   if t is not None and not isinstance(t,p.PCB_VIA) and net=='RF_ANT' and l==p.F_Cu and t.GetStart().x==t.GetEnd().x==9500000 and min(t.GetStart().y,t.GetEnd().y)>=-1900000 and max(t.GetStart().y,t.GetEnd().y)<=900000:continue
   rfhits.append([net,name,l])
require(not rfhits,'RF keepout intrusion')
rows=json.loads((S/'new_routes.json').read_text());ids={r['uuid'] for r in rows};summary={}
for t in b.GetTracks():
 if t.m_Uuid.AsString() not in ids:continue
 n=t.GetNetname();v=summary.setdefault(n,{'tracks':0,'vias':0,'total_trace_mm':0,'sub_0p1mm_segments':0,'min_segment_mm':1e9,'widths_mm':set(),'layers':set()})
 if isinstance(t,p.PCB_VIA):v['vias']+=1;continue
 length=p.ToMM(t.GetLength());v['tracks']+=1;v['total_trace_mm']+=length;v['min_segment_mm']=min(v['min_segment_mm'],length);v['sub_0p1mm_segments']+=length<.1;v['widths_mm'].add(p.ToMM(t.GetWidth()));v['layers'].add(b.GetLayerName(t.GetLayer()))
for v in summary.values():v['widths_mm']=sorted(v['widths_mm']);v['layers']=sorted(v['layers'])
def planes(board):
 out=[]
 for z in board.Zones():
  if z.GetIsRuleArea():continue
  for l in L:
   if not z.IsOnLayer(l):continue
   q=z.GetFilledPolysList(l);out.append({'uuid':z.m_Uuid.AsString(),'net':z.GetNetname(),'layer':board.GetLayerName(l),'islands':q.OutlineCount(),'area_mm2':q.Area()/1e12,'island_areas_mm2':sorted(q.UnitSet(i).Area()/1e12 for i in range(q.OutlineCount()))})
 return out
print(json.dumps({'gate_nets_cross_net_physical_overlap':hits,'RF_six_layer_actual_keepout_intrusions':rfhits,'new_route_statistics':summary,'plane_before':planes(old),'plane_after':planes(b),'limits':'Island-count/area is diagnostic, not plane-neck ampacity or HF return proof. Finite connectivity and full DRC do not prove dynamic PI or implicit semiconductor isolation.'},indent=2))
