from geometry import *
from finite_copper import build,components,shape as finite
N='SENS_VIO_1V8';items=[]
def line(l,pts):
 for a,c in zip(pts,pts[1:]):items.append(track(N,l,a,c,.25))
for name,pt in [('C202.1',(10.975,35.9625)),('C204.1',(9.575,47.9625)),('C206.1',(9.575,57.9625)),('U204.1',(3.8875,63.125)),('R242.2',(8.325,75)),('R243.2',(11.05,75.15))]:
 line(p.F_Cu,[xy(pm[name]),pt]);items.append(via(N,pt))
line(p.B_Cu,[(1.75,90.5),(1.75,91.4),(3.5,91.4)]);items.append(via(N,(3.5,91.4)))
line(p.In3_Cu,[(3.5,91.4),(3.5,77),(3,76.5),(3,63.125),(3.8875,63.125),(4.6,62.4125),(4.6,51.6),(4.3,51.3),(4.3,50.5),(4.6,50.2),(4.6,40.6),(2.4,40.6),(2.4,35.9625),(10.975,35.9625)])
line(p.In3_Cu,[(4.6,47.9625),(9.575,47.9625)])
line(p.In3_Cu,[(4.6,57.9625),(9.575,57.9625)])
line(p.In3_Cu,[(3,74.5),(6.8,74.5),(7.2,74.8),(8,74.8),(8.4,74.5),(10.45,74.5),(11.05,75.15)])
line(p.In3_Cu,[(8.325,74.5),(8.325,75)])
def serial(t):
 v=isinstance(t,p.PCB_VIA)
 return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else b.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(p.F_Cu)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
rows=[dict(index=i,object=serial(t),conflicts=errors([t]))for i,t in enumerate(items)];whole=errors(items);ns=build(b);sensor=ns[N]+[(str(i),False,{l:finite(t,l)for l in L if t.IsOnLayer(l)})for i,t in enumerate(items)];cs=components(sensor)
result=dict(base_sha=hashlib.sha256(S.read_bytes()).hexdigest(),status='REJECTED_COLLISIONS'if whole else'GEOMETRY_ONLY_PENDING_NATIVE_AUTHORITY',removed=[],moved_footprints=[],objects=[serial(t)for t in items],checks=rows,whole_conflicts=whole,all12_conceptual_components=cs,oldpad_components_unchanged={n:components(v)for n,v in ns.items()},note='No original objects removed; same-net conceptual continuity is not valid electrical circuit when clearance fails. Source/native remain unchanged.')
(D/'plan.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],objects=len(items),blocked=[x for x in rows if x['conflicts']],components=cs),indent=2))
