import os
os.environ["XDG_CONFIG_HOME"]="/tmp/vsync_advisory"
from pathlib import Path
import pcbnew as p,math,heapq,json
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'));xy=lambda v:(v.x/1e6,v.y/1e6)
def cross(a,c):return a[0]*c[1]-a[1]*c[0]
def sub(a,c):return(a[0]-c[0],a[1]-c[1])
def point(a,z,t):return(a[0]+t*(z[0]-a[0]),a[1]+t*(z[1]-a[1]))
out={}
for net,labels in [('CAM_PCLK',['U101.21','U202.4','R218.1']),('CAM_HREF',['U101.23','U202.6','R220.1']),('CAM_VSYNC',['U101.22','U202.5','R219.1'])]:
 ts=[t for t in b.GetTracks()if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)];vs=[v for v in b.GetTracks()if v.GetNetname()==net and isinstance(v,p.PCB_VIA)];pads={f.GetReference()+'.'+q.GetNumber():q for f in b.GetFootprints()for q in f.Pads()if q.GetNetname()==net};ends=[(xy(t.GetStart()),xy(t.GetEnd()))for t in ts];cuts=[{0.,1.}for t in ts];links=[]
 def proj(v,a,z):
  d=sub(z,a);den=d[0]**2+d[1]**2;u=max(0,min(1,((v[0]-a[0])*d[0]+(v[1]-a[1])*d[1])/den));return u,math.dist(v,point(a,z,u))
 for i,t in enumerate(ts):
  a,z=ends[i];d=sub(z,a)
  for j in range(i):
   if ts[j].GetLayer()!=t.GetLayer():continue
   aa,zz=ends[j];dd=sub(zz,aa);den=cross(d,dd)
   if abs(den)>1e-12:
    u=cross(sub(aa,a),dd)/den;v=cross(sub(aa,a),d)/den
    if -1e-8<=u<=1+1e-8 and-1e-8<=v<=1+1e-8:cuts[i].add(max(0,min(1,u)));cuts[j].add(max(0,min(1,v)))
   else:
    for q in [a,z]:
     v,dist=proj(q,aa,zz)
     if dist<1e-8:cuts[j].add(v)
    for q in [aa,zz]:
     u,dist=proj(q,a,z)
     if dist<1e-8:cuts[i].add(u)
  for v in vs:
   u,dist=proj(xy(v.GetPosition()),a,z)
   if dist<=v.GetWidth(p.F_Cu)/2e6+t.GetWidth()/2e6+1e-8:cuts[i].add(u);links.append((i,u,'via:'+v.m_Uuid.AsString(),dist))
  for name,q in pads.items():
   if not q.IsOnLayer(t.GetLayer()):continue
   u,dist=proj(xy(q.GetPosition()),a,z)
   # These terminals are author-defined pad-center-ended escapes. Do not invent broad pad/body joins.
   if dist<1e-8:cuts[i].add(u);links.append((i,u,'pad:'+name,dist))
 graph={}
 def node(i,u):
  q=point(*ends[i],u);return('point',ts[i].GetLayer(),round(q[0],8),round(q[1],8))
 def edge(a,z,w):graph.setdefault(a,[]).append((z,w));graph.setdefault(z,[]).append((a,w))
 for i,t in enumerate(ts):
  vv=sorted(cuts[i])
  for a,z in zip(vv,vv[1:]):edge(node(i,a),node(i,z),(z-a)*t.GetLength()/1e6)
 for i,u,name,d in links:edge(node(i,u),name,d)
 def shortest(s,g):
  heap=[(0,0,s)];dist={s:0};prev={};counter=0
  while heap:
   d,_,v=heapq.heappop(heap)
   if d>dist[v]+1e-10:continue
   if v==g:
    path=[v]
    while v!=s:v=prev[v];path.append(v)
    path.reverse();vias=[x for x in path if isinstance(x,str)and x.startswith('via:')];layers=[x[1]for x in path if isinstance(x,tuple)];changes=sum(a!=z for a,z in zip(layers,layers[1:]));return{'planar_centerline_mm':d,'via_nodes_traversed':len(vias),'layer_changes':changes,'layer_sequence':[b.GetLayerName(x)for i,x in enumerate(layers)if i==0 or x!=layers[i-1]],'via_uuids':[x[4:]for x in vias]}
   for z,w in graph.get(v,[]):
    nd=d+w
    if nd+1e-10<dist.get(z,math.inf):dist[z]=nd;prev[z]=v;counter+=1;heapq.heappush(heap,(nd,counter,z))
  raise RuntimeError('centerline graph not connected '+s+' '+g)
 out[net]={labels[i]+'__'+labels[j]:shortest('pad:'+labels[i],'pad:'+labels[j])for i,j in[(0,1),(1,2),(0,2)]}
r={'paths':out,'model':'Geometric centerline graph with exact same-layer intersections and in-plane short connectors from track centerline to connected via center. Through-board vertical lengths/delays are NOT included. Via nodes can be traversed on one layer; layer_changes reports actual graph changes separately. Bias paths are terminal-to-terminal geometry, not mislabeled pure open stub length. No timing matching claim.'};(D/'path_geometry.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
