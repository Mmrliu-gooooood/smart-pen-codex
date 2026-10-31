import reference_final as z
import json,math,heapq
p=z.p;V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6));start=(9.575,42.2375);goal=(9.575,52.0375);out={}
for name,b in [('baseline',z.a),('candidate',z.b)]:
 plane=z.planes(b)[p.In2_Cu,'3V3_AON'];rows=[]
 for width in [.3,.5]:
  nodes={(x/4,y/4)for x in range(3,50)for y in range(160,225)if plane.Contains(V((x/4,y/4)))};nodes|={start,goal};cache={}
  def clear(a,c):
   key=tuple(sorted([a,c]))
   if key not in cache:
    t=p.PCB_TRACK(b);t.SetLayer(p.F_Cu);t.SetStart(V(a));t.SetEnd(V(c));t.SetWidth(round(width*1e6));q=z.shape(t);q.BooleanSubtract(plane);cache[key]=q.Area()==0
   return cache[key]
  h=[(0,start)];dist={start:0};prev={};done=set()
  while h:
   d,a=heapq.heappop(h)
   if a in done:continue
   done.add(a)
   if a==goal:break
   if a==start:near=[v for v in nodes if 0<math.dist(a,v)<.6]
   else:near=[(round(a[0]+dx,6),round(a[1]+dy,6))for dx in [-.25,0,.25]for dy in [-.25,0,.25]if dx or dy];near += [goal]if math.dist(a,goal)<.6 else[]
   for c in near:
    if c not in nodes or c in done or not clear(a,c):continue
    nd=d+math.dist(a,c)
    if nd<dist.get(c,float('inf')):dist[c]=nd;prev[c]=a;heapq.heappush(h,(nd,c))
  path=[]
  if goal in done:
   cur=goal
   while cur!=start:path.append(cur);cur=prev[cur]
   path.append(start);path.reverse()
  rows.append({'width_mm':width,'found':bool(path),'length_mm':dist.get(goal),'path':path,'scope':'Constructive existing filled-plane corridor on bounded .25mm grid, not shortest physical current flow or manufacturing criterion.'})
 out[name]=rows
(z.D/'bridge.json').write_text(json.dumps(out,indent=2));print({k:[(r['width_mm'],r['found'],r['length_mm'])for r in v]for k,v in out.items()})
