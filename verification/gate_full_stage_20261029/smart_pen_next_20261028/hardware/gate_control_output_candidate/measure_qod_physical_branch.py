from pathlib import Path
import json,heapq,math,hashlib
D=Path(__file__).resolve().parent;s=(D/'audit_gate.py').read_text();exec(compile(s[:s.index('na,nb=build')],__file__,'exec'))
net='CAM_3V3_PRELINK';nodes=[n for n in build(b)[net]if '/'not in n[0]];tracks={t.m_Uuid.AsString():t for t in b.GetTracks()};edges={i:[]for i in range(len(nodes))}
for i,(_,_,aa)in enumerate(nodes):
 for j,(_,_,zz)in enumerate(nodes[:i]):
  for l in aa.keys()&zz.keys():
   if not aa[l].BBox().Intersects(zz[l].BBox()):continue
   q=p.SHAPE_POLY_SET();q.BooleanIntersection(aa[l],zz[l])
   if q.Area()>1:edges[i].append(j);edges[j].append(i);break
weights=[]
for name,_,_ in nodes:
 t=tracks.get(name);weights.append(math.dist((t.GetStart().x,t.GetStart().y),(t.GetEnd().x,t.GetEnd().y))/1e6 if t is not None and not isinstance(t,p.PCB_VIA)else 0)
start=next(i for i,n in enumerate(nodes)if n[0]=='R303.1');end=next(i for i,n in enumerate(nodes)if n[0]=='U301.6');dist={start:0};prev={};heap=[(0,start)]
while heap:
 d,i=heapq.heappop(heap)
 if d>dist[i]:continue
 if i==end:break
 for j in edges[i]:
  nd=d+weights[j]
  if nd<dist.get(j,float('inf')):dist[j]=nd;prev[j]=i;heapq.heappush(heap,(nd,j))
require(end in dist,'Physical QOD-to-output branch absent');path=[];i=end
while True:
 name=nodes[i][0];t=tracks.get(name);path.append({'node':name,'full_segment_length_mm':weights[i],'layer':b.GetLayerName(t.GetLayer())if t else None})
 if i==start:break
 i=prev[i]
print(json.dumps({'pcb_sha256':hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'from':'R303.1','to':'U301.6','actual_finite_copper_intersection_path':path[::-1],'sum_full_track_lengths_mm':dist[end],'metric':'Sum of whole segments in a genuine copper-connected branch, conservative relative to partial-segment traversal. Excludes pad spread/barrel; NOT a loop inductance/current path simulation.'},indent=2))
