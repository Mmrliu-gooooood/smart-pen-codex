"""Connect actual copper components, not only their nearest via. Native readback/DRC mandatory."""
from pathlib import Path
s=Path(__file__).with_name('grid_core.py').read_text().split('pads={}')[0]
s=s.replace('math.dist(xy(v.GetPosition()),q[1:])<1e-6','math.dist(xy(v.GetPosition()),q[1:])<STEP*.72+1e-6')
exec(compile(s,str(Path(__file__).with_name('grid_core.py')),'exec'))
from scipy import ndimage

def copper_parts(net):
 b.BuildConnectivity();con=b.GetConnectivity();pads=[a for f in b.GetFootprints() for a in f.Pads() if a.GetNetname()==net];todo={a.m_Uuid.AsString():a for a in pads};parts=[]
 while todo:
  q=[next(iter(todo.values()))];seen=set();items=[];labels=[]
  while q:
   a=q.pop();uid=a.m_Uuid.AsString()
   if uid in seen:continue
   seen.add(uid);items.append(a)
   if uid in todo:
    labels.append(a.GetParentFootprint().GetReference()+'.'+a.GetNumber());del todo[uid]
   q.extend(con.GetConnectedTracks(a));q.extend(con.GetConnectedPads(a))
  parts.append({'items':items,'labels':labels})
 parts.sort(key=lambda x:(not any(l.startswith('U101.') for l in x['labels']),-len(x['items'])))
 return parts

def anchors(part,obs):
 out=set()
 def put(k,point):
  ix,iy=round(point[0]/STEP),round(point[1]/STEP)
  if 0<=ix<NX and 0<=iy<NY and not obs[k,ix,iy]:out.add((k,ix,iy))
 for a in part['items']:
  typ=a.GetClass()
  if typ=='PCB_VIA':
   for k in range(2):put(k,xy(a.GetPosition()))
  elif typ=='PAD':
   for k,l in enumerate(layers):
    if a.IsOnLayer(l):put(k,xy(a.GetPosition()))
  elif typ=='PCB_TRACK' and a.GetLayer() in layers:
   k=layers.index(a.GetLayer());aa,zz=xy(a.GetStart()),xy(a.GetEnd());n=max(1,math.ceil(math.dist(aa,zz)/.05))
   for u in np.linspace(0,1,n+1):put(k,(aa[0]+u*(zz[0]-aa[0]),aa[1]+u*(zz[1]-aa[1])))
 return out

def component_search(starts,goals,obs,vb):
 if not starts or not goals:return None,'no unblocked real-copper anchors'
 target_xy=np.zeros((NX,NY),bool)
 for k,x,y in goals:target_xy[x,y]=True
 h=ndimage.distance_transform_edt(~target_xy);shape=(2,NX,NY);dist=np.full(shape,np.inf,dtype=np.float32);prev=np.full(shape,-1,dtype=np.int32)
 def encode(k,x,y):return(k*NX+x)*NY+y
 def decode(v):y=v%NY;v//=NY;return(v//NX,v%NX,y)
 heap=[]
 for k,x,y in starts:dist[k,x,y]=0;heap.append((float(h[x,y]),0,k,x,y))
 heapq.heapify(heap);pops=0;dirs=[(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,math.sqrt(2)),(-1,1,math.sqrt(2)),(1,-1,math.sqrt(2)),(1,1,math.sqrt(2))]
 while heap:
  _,g,k,x,y=heapq.heappop(heap)
  if g>dist[k,x,y]+.001:continue
  pops+=1
  if (k,x,y) in goals:
   path=[];idx=encode(k,x,y)
   while idx!=-1:path.append(decode(idx));idx=int(prev[decode(idx)])
   return path[::-1],str(pops)
  if pops>1000000:return None,'component search budget1000000'
  for dx,dy,cost in dirs:
   xx,yy=x+dx,y+dy
   if not(0<=xx<NX and 0<=yy<NY) or obs[k,xx,yy]:continue
   if dx and dy and (obs[k,x+dx,y] or obs[k,x,y+dy]):continue
   ng=g+cost
   if ng+.001<dist[k,xx,yy]:dist[k,xx,yy]=ng;prev[k,xx,yy]=encode(k,x,y);heapq.heappush(heap,(ng+h[xx,yy],ng,k,xx,yy))
  kk=1-k
  if not vb[x,y] and not obs[kk,x,y]:
   ng=g+50
   if ng+.001<dist[kk,x,y]:dist[kk,x,y]=ng;prev[kk,x,y]=encode(k,x,y);heapq.heappush(heap,(ng+h[x,y],ng,kk,x,y))
 return None,'no physical-copper-to-copper path'

expected_new={}
_original_add=add
def add(net,*args,**kwargs):
 before={t.m_Uuid.AsString() for t in b.GetTracks()}
 result=_original_add(net,*args,**kwargs)
 for t in b.GetTracks():
  uid=t.m_Uuid.AsString()
  if uid not in before:expected_new[uid]=net
 return result
selected=sys.argv[3].split(',');reports=[]
for net in selected:
 
 if net in ['GND','3V3_AON','SENS_VIO_1V8'] or net.startswith('USB_'):raise RuntimeError('forbidden')
 for iteration in range(20):
  parts=copper_parts(net)
  if len(parts)<=1:break
  obs,vb=masks(net);start=anchors(parts[0],obs)
  primary=[pp for pp in parts[1:] if any(l.startswith(('U201.','U202.')) for l in pp['labels'])]
  targets=primary if primary else parts[1:]
  goal=set().union(*(anchors(pp,obs) for pp in targets));t0=time.time();path,why=component_search(start,goal,obs,vb);row={'net':net,'before_components':[pp['labels'] for pp in parts],'source_anchors':len(start),'target_anchors':len(goal),'search':why,'seconds':round(time.time()-t0,3),'path_found':path is not None}
  if path:
   k,x,y=path[0];q,xx,yy=path[-1];add(net,path,(x*STEP,y*STEP),(xx*STEP,yy*STEP),k,q);after=copper_parts(net);row['after_components']=[pp['labels'] for pp in after];row['actual_component_reduction']=len(parts)-len(after);
   if len(after)>=len(parts):raise RuntimeError('no actual component reduction')
  reports.append(row);print(row,flush=True)
  if path is None:break
out=D/(outname+'.kicad_pcb');p.SaveBoard(str(out),b);b=p.LoadBoard(str(out));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out),b);(D/(outname+'.kicad_pro')).write_text((D/(source+'.kicad_pro')).read_text());(D/(outname+'_component_route.json')).write_text(json.dumps(reports,indent=2))

(D/(outname+'.kicad_dru')).write_text((D/(source+'.kicad_dru')).read_text())

if not expected_new:raise RuntimeError('no new route; not a successful candidate')
actual={t.m_Uuid.AsString():t.GetNetname() for t in b.GetTracks()}
if any(actual.get(k)!=v for k,v in expected_new.items()):raise RuntimeError('literal expected-net mismatch')
(D/(outname+'_expected_new.json')).write_text(json.dumps(expected_new,indent=2))
