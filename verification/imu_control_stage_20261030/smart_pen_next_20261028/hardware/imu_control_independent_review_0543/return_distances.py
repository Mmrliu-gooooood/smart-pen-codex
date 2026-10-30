import io,contextlib,json,math
with contextlib.redirect_stdout(io.StringIO()):import independent as a
p=a.p;ns,adj=a.graph(a.b,'GND');root=next(u for u,n,_ in ns if n=='J106.3');core=a.reach(adj,root);grounds=[t for t in a.b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND'and a.uid(t)in core];rows=[]
for u in a.m['added']:
 v=a.t[u]
 if not isinstance(v,p.PCB_VIA):continue
 def dist(q):return math.hypot(v.GetPosition().x-q.GetPosition().x,v.GetPosition().y-q.GetPosition().y)/1e6
 g=min(grounds,key=dist);rows.append({'uuid':u,'net':v.GetNetname(),'at':[v.GetPosition().x/1e6,v.GetPosition().y/1e6],'nearest_core_GND_via':[g.GetPosition().x/1e6,g.GetPosition().y/1e6],'center_distance_mm':dist(g)})
a.need(len(rows)==13,'13via');irq=next(x for x in rows if x['at']==[4.7,80.125]);a.need(abs(irq['center_distance_mm']-3.779302315)<1e-6,'IRQ distance')
print(json.dumps({'method':'Independent physical UUID graph, core-connected GND via only','new_vias':rows,'not_SI_acceptance':True},indent=2))
