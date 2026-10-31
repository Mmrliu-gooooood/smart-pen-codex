import reference_final as z
import json,math,heapq,sys
sys.path.insert(0,str(z.D/'review_dependencies'));from finite_copper import build,components
p=z.p;xy=lambda v:(v.x/1e6,v.y/1e6);out={}
for name,b in [('baseline',z.a),('candidate',z.b)]:
 plane=z.planes(b)[p.In2_Cu,'3V3_AON'];vs=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON'and plane.Contains(t.GetPosition())];nodes=[xy(t.GetPosition())for t in vs];rows=[]
 for w in [.15,.3,.5]:
  g={i:[]for i in range(len(vs))}
  for i,a in enumerate(vs):
   for j in range(i):
    c=vs[j];t=p.PCB_TRACK(b);t.SetLayer(p.F_Cu);t.SetStart(a.GetPosition());t.SetEnd(c.GetPosition());t.SetWidth(round(w*1e6));q=z.shape(t);q.BooleanSubtract(plane)
    if q.Area()==0:g[i].append((j,math.dist(nodes[i],nodes[j])));g[j].append((i,math.dist(nodes[i],nodes[j])))
  start=nodes.index((5.4,14.75));h=[(0,start,[start])];seen=set();paths={}
  while h:
   dist,i,path=heapq.heappop(h)
   if i in seen:continue
   seen.add(i);paths[i]=(dist,path)
   for j,cost in g[i]:
    if j not in seen:heapq.heappush(h,(dist+cost,j,path+[j]))
  rows.append({'corridor_width_mm':w,'paths':[{'endpoint':nodes[i],'length_mm':d,'bends_at_actual_vias':[nodes[j]for j in path]}for i,(d,path)in paths.items()]})
 ns=build(b);out[name]={'all_power_component':{n:next(c for c in components(ns[n])if anchor in c)for n,anchor in [('3V3_AON','J106.2'),('GND','J106.3'),('SENS_VIO_1V8','J202.23')]},'AON_via_corridor_paths':rows,'C104_pads':{q.GetNumber():xy(q.GetPosition())for f in b.GetFootprints()if f.GetReference()=='C104'for q in f.Pads()}}
(z.D/'feed_paths.json').write_text(json.dumps(out,indent=2))
