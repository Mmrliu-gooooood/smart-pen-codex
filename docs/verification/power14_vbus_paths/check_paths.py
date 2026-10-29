from pathlib import Path
import pcbnew as p,json,hashlib,math,heapq
O=Path(__file__).resolve().parent;D=O.parents[2]/'hardware/power_integrated_layout_14x45';fn=D/'power_integrated_study.kicad_pcb';b=p.LoadBoard(str(fn));core=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));oldids={t.m_Uuid.AsString() for t in core.GetTracks()};net='VBUS_5V'
pads=[(f.GetReference(),a) for f in b.GetFootprints() for a in f.Pads() if a.GetNetname()==net];tracks=[t for t in b.GetTracks() if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)];vias=[t for t in b.GetTracks() if t.GetNetname()==net and isinstance(t,p.PCB_VIA)];points=set();pp={}
assert not any(z.GetNetname()==net for z in b.Zones()),'Plane resistance cannot be treated as zero length'
for r,a in pads:
 q=a.GetPosition();k=(p.F_Cu if a.IsOnLayer(p.F_Cu) else p.B_Cu,q.x,q.y);points.add(k);pp[r+'.'+a.GetNumber()]=k
for t in tracks:
 for q in [t.GetStart(),t.GetEnd()]:points.add((t.GetLayer(),q.x,q.y))
for v in vias:
 for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:points.add((l,v.GetPosition().x,v.GetPosition().y))
pts=sorted(points);ix={q:i for i,q in enumerate(pts)};adj=[[] for q in pts]
def edge(i,j,length,typ,**meta):
 d={'length_mm':length,'type':typ,**meta};adj[i].append((j,d));adj[j].append((i,d))
for r,a in pads:
 ids=[i for i,(l,x,y) in enumerate(pts) if a.IsOnLayer(l) and a.HitTest(p.VECTOR2I(x,y))]
 for i in ids[1:]:edge(ids[0],i,0,'pad',ref=r,pin=a.GetNumber())
for t in tracks:
 a,z=t.GetStart(),t.GetEnd();dx=z.x-a.x;dy=z.y-a.y;ll=dx*dx+dy*dy;inside=[]
 for i,(l,x,y) in enumerate(pts):
  if l!=t.GetLayer():continue
  u=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/ll))
  if math.hypot(x-a.x-u*dx,y-a.y-u*dy)<=2:inside.append((u,i))
 inside.sort()
 for (u,i),(v,j) in zip(inside,inside[1:]):edge(i,j,(v-u)*math.sqrt(ll)/1e6,'track',uuid=t.m_Uuid.AsString(),width_mm=p.ToMM(t.GetWidth()),layer=b.GetLayerName(t.GetLayer()),added=t.m_Uuid.AsString() not in oldids)
for v in vias:
 ids=[i for i,(l,x,y) in enumerate(pts) if x==v.GetPosition().x and y==v.GetPosition().y]
 for i in ids[1:]:edge(ids[0],i,0,'via',uuid=v.m_Uuid.AsString())
start=ix[pp['J2.1']];dist=[math.inf]*len(pts);prev={};dist[start]=0;h=[(0,start)]
while h:
 d,i=heapq.heappop(h)
 if d>dist[i]+1e-10:continue
 for j,e in adj[i]:
  nd=d+e['length_mm']
  if nd<dist[j]-1e-10:dist[j]=nd;prev[j]=(i,e);heapq.heappush(h,(nd,j))
rho=1.724e-8*(1+.00393*(85-20));rows=[]
for label,k in sorted(pp.items()):
 if label=='J2.1':continue
 i=ix[k];assert math.isfinite(dist[i]);path=[]
 while i!=start:i,e=prev[i];path.append(e)
 path.reverse();tt=[e for e in path if e['type']=='track'];rows.append({'target':label,'source':'J2.1','shortest_XY_centerline_path_mm':dist[ix[k]],'added_track_path_mm':sum(e['length_mm'] for e in tt if e['added']),'minimum_track_width_mm':min(e['width_mm'] for e in tt),'layers':sorted({e['layer'] for e in tt}),'distinct_vias':len({e['uuid'] for e in path if e['type']=='via'}),'conditional_trace_only_R_85C_31p5um_ohm':sum(rho*e['length_mm']/(e['width_mm']*31.5e-6) for e in tt),'track_UUIDs':list(dict.fromkeys(e['uuid'] for e in tt))})
result={'pcb_sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'method':'Dijkstra shortest XY trace-centreline path. Tracks split at exact <=2nm centreline contacts; actual pad HitTest zero-length connections; via XY zero length. No VBUS plane. Not distributed resistance solution. Pad spreading/via barrel/return/source impedance excluded. Width is track-only, not pad copper neck.','new_whole_net_trace_sum_mm':sum(p.ToMM(t.GetLength()) for t in tracks if t.m_Uuid.AsString() not in oldids),'all_whole_net_trace_sum_mm':sum(p.ToMM(t.GetLength()) for t in tracks),'paths':rows}
(O/'paths.json').write_text(json.dumps(result,indent=2))
for r in rows:print(r['target'],round(r['shortest_XY_centerline_path_mm'],3),round(r['added_track_path_mm'],3),r['minimum_track_width_mm'],r['distinct_vias'],round(r['conditional_trace_only_R_85C_31p5um_ohm'],4))

# Separate the geometrically preserved power trunk from any new parallel shortcuts.
dist2=[math.inf]*len(pts);prev2={};dist2[start]=0;h=[(0,start)]
while h:
 d,i=heapq.heappop(h)
 if d>dist2[i]+1e-10:continue
 for j,e in adj[i]:
  if e['type']=='track' and e['added']:continue
  nd=d+e['length_mm']
  if nd<dist2[j]-1e-10:dist2[j]=nd;prev2[j]=(i,e);heapq.heappush(h,(nd,j))
original=[]
for label in ['C1.1','U1.13','R6.1']:
 i=ix[pp[label]];assert math.isfinite(dist2[i]);path=[]
 while i!=start:i,e=prev2[i];path.append(e)
 tt=[e for e in path if e['type']=='track'];original.append({'target':label,'retained_core_only_path_mm':dist2[ix[pp[label]]],'minimum_track_width_mm':min(e['width_mm'] for e in tt),'trace_only_R_85C_31p5um_ohm':sum(rho*e['length_mm']/(e['width_mm']*31.5e-6) for e in tt),'distinct_vias':len({e['uuid'] for e in path if e['type']=='via'})})
result['retained_core_only_paths']=original
result['parallel_path_warning']='New VBUS additions form a parallel J2-to-C1 shortcut. They are not all exclusively thermal-current segments. Preserved wide trunk remains connected, but actual current division needs distributed R and load/inrush analysis. Shortest geometric route is not the sole current path.'
(O/'paths.json').write_text(json.dumps(result,indent=2));print('CORE ONLY',json.dumps(original))
# Conditional linear resistor network; ideal pad/via junctions only. Not an ampacity model.
import numpy as np
parent=list(range(len(pts)))
def root(i):
 while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
 return i
for i,edges in enumerate(adj):
 for j,e in edges:
  if e['type']!='track' or e['length_mm']<1e-12:parent[root(i)]=root(j)
roots=sorted({root(i) for i in range(len(pts))});ri={r:i for i,r in enumerate(roots)};edges=[]
for i,es in enumerate(adj):
 for j,e in es:
  if i>=j or e['type']!='track' or root(i)==root(j):continue
  thickness=18 if e['layer'].startswith('In') else 31.5
  resistance=rho*e['length_mm']/(e['width_mm']*thickness*1e-6)
  edges.append((ri[root(i)],ri[root(j)],resistance,e))
N=len(roots);L=np.zeros((N,N))
for i,j,r,e in edges:L[i,i]+=1/r;L[j,j]+=1/r;L[i,j]-=1/r;L[j,i]-=1/r
src=ri[root(start)];keep=[i for i in range(N) if i!=src];models=[]
for target,amps,title in [('U1.13',1.,'unit-current transfer sensitivity, NOT USB authorization'),('U102.4',.025,'single thermal load 25mA hypothetical, NOT actual/max rating')]:
 sink=ri[root(ix[pp[target]])];I=np.zeros(N);I[sink]=-amps;V=np.zeros(N);V[keep]=np.linalg.solve(L[np.ix_(keep,keep)],I[keep]);curr=[]
 for i,j,r,e in edges:
  curr.append({'uuid':e['uuid'],'current_A':abs((V[i]-V[j])/r),'segment_length_mm':e['length_mm'],'width_mm':e['width_mm'],'layer':e['layer'],'added':e['added']})
 added=sorted((e for e in curr if e['added']),key=lambda e:e['current_A'],reverse=True)
 models.append({'scenario':title,'source':'J2.1 ideal0V','target':target,'sink_A':amps,'trace_network_drop_mV':-V[sink]*1000,'max_added_segment_current_A':added[0]['current_A'],'largest_added_currents':added[:6]})
result['resistor_screen']={'temperature_C':85,'outer_copper_um':31.5,'inner_copper_um':18,'model':'All trace branches simultaneously. Actual segment widths/lengths; pads and via barrels ideal zero-R, no contact/return/source resistance, no dynamic inductance, no measured load/temperature/ampacity. This deliberately differs from geometric shortest-path analysis.','scenarios':models}
(O/'paths.json').write_text(json.dumps(result,indent=2));print('NETWORK',json.dumps(models))
