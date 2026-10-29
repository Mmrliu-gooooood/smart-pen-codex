#!/usr/bin/python3
"""Conservative local two-signal-layer grid search. Actual KiCad DRC is required afterwards."""
from pathlib import Path
import pcbnew as p,numpy as np,math,heapq,json,time,sys,os
D=Path(__file__).resolve().parent;STEP=.025;NX=561;NY=1801;TRACK_HALF=.15/2;EXTRA=.015
def pair_clearance(other):return .15
def margin_to(other):return .15+TRACK_HALF+EXTRA
import shutil
b=p.LoadBoard(str(D/'power_integrated_study.kicad_pcb'));layers=[p.F_Cu,p.B_Cu,p.In2_Cu];results=[]
def xy(v):return(p.ToMM(v.x),p.ToMM(v.y))
def pt(a):return p.VECTOR2I(p.FromMM(float(a[0])),p.FromMM(float(a[1])))
def rectangle(arr,x,y,w,h,margin):
 x0=max(0,int(math.floor((x-w/2-margin)/STEP)));x1=min(NX,int(math.ceil((x+w/2+margin)/STEP))+1);y0=max(0,int(math.floor((y-h/2-margin)/STEP)));y1=min(NY,int(math.ceil((y+h/2+margin)/STEP))+1)
 xx=np.arange(x0,x1)[:,None]*STEP;yy=np.arange(y0,y1)[None,:]*STEP
 arr[x0:x1,y0:y1]|=(abs(xx-x)<=w/2+margin)&(abs(yy-y)<=h/2+margin)

def capsule(arr,a,z,r):
 x0=max(0,int(math.floor((min(a[0],z[0])-r)/STEP)));x1=min(NX,int(math.ceil((max(a[0],z[0])+r)/STEP))+1);y0=max(0,int(math.floor((min(a[1],z[1])-r)/STEP)));y1=min(NY,int(math.ceil((max(a[1],z[1])+r)/STEP))+1)
 if x1<=x0 or y1<=y0:return
 xx=np.arange(x0,x1)[:,None]*STEP;yy=np.arange(y0,y1)[None,:]*STEP;dx=z[0]-a[0];dy=z[1]-a[1];den=dx*dx+dy*dy
 u=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/den,0,1) if den>0 else 0
 arr[x0:x1,y0:y1]|=(xx-a[0]-u*dx)**2+(yy-a[1]-u*dy)**2<=r*r

# Explicit escape fanouts before long routes; verified separately by native DRC.
def explicit(net,points,layer=p.B_Cu,width=.15,via=True):
 for a,z in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(a));t.SetEnd(pt(z));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(b.FindNet(net));b.Add(t)
 if via:
  v=p.PCB_VIA(b);v.SetPosition(pt(points[-1]));v.SetWidth(p.F_Cu,p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));b.Add(v)
SYS_MASK=None
def masks(net):
 global SYS_MASK
 obs=np.zeros((3,NX,NY),bool);vb=np.zeros((NX,NY),bool)
 obs[:,:math.ceil(.6/STEP),:]=True;obs[:,math.floor(13.4/STEP)+1:,:]=True;obs[:,:,:math.ceil(.6/STEP)]=True;obs[:,:,math.floor(44.4/STEP)+1:]=True
 vb[:math.ceil(.8/STEP),:]=True;vb[math.floor(13.2/STEP)+1:,:]=True;vb[:,:math.ceil(.8/STEP)]=True;vb[:,math.floor(44.2/STEP)+1:]=True
 for fp in b.GetFootprints():
  for a in fp.Pads():
   x,y=xy(a.GetPosition());w,h=xy(a.GetSize());angle=int(round(a.GetOrientationDegrees()))%180
   if angle==90:w,h=h,w
   for k,l in enumerate(layers):
    if a.IsOnLayer(l) and a.GetNetname()!=net:rectangle(obs[k],x,y,w,h,margin_to(a.GetNetname()))
   rectangle(vb,x,y,w,h,.3+.05 if a.GetNetname()==net else .3+pair_clearance(a.GetNetname())+.01) # no added via-in-pad, even own net
 for t in b.GetTracks():
  a=xy(t.GetStart());z=xy(t.GetEnd());other=t.GetNetname()!=net
  if isinstance(t,p.PCB_VIA):
   radius=p.ToMM(t.GetWidth(p.F_Cu))/2
   if other:
    for k in range(3):capsule(obs[k],a,a,radius+margin_to(t.GetNetname()))
   capsule(vb,a,a,.3+radius+pair_clearance(t.GetNetname())+.01 if other else .3+.25+.01)
  else:
   radius=p.ToMM(t.GetWidth())/2
   if other:capsule(vb,a,z,radius+.3+.15+.02)
   if t.GetLayer() in layers:
    if other:capsule(obs[layers.index(t.GetLayer())],a,z,radius+margin_to(t.GetNetname()))
    if other:capsule(vb,a,z,radius+.3+pair_clearance(t.GetNetname())+.01)
 # Reuse an already fabricated same-net via; no new drill there.
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) and t.GetNetname()==net:
   x,y=xy(t.GetPosition());ix=round(x/STEP);iy=round(y/STEP)
   if not obs[0,ix,iy] and not obs[1,ix,iy]:vb[ix,iy]=False
 # Keep new F copper out of preserved converter SW/FB/decoupling region.
 rectangle(obs[0],6,22.2,5.2,10.4,.1)
 rectangle(vb,6,22.2,5.2,10.4,.1)
 # No new thermal trace below inductor/SW box on back either.
 rectangle(obs[1],6,19.2,4.8,4.8,.1)
 # Preserve SYS polygon island: no new signal on its original defined region.
 if SYS_MASK is None:
  SYS_MASK=np.zeros((NX,NY),bool)
  for z in b.Zones():
   if z.GetLayer()==p.In2_Cu:
    poly=z.Outline()
    for ix in range(NX):
     for iy in range(NY):
      if poly.Contains(pt((ix*STEP,iy*STEP))):SYS_MASK[ix,iy]=True
 # Clearance dilation applies only to the preserved SYS zone, not already inflated track obstacles.
 from scipy.ndimage import binary_dilation
 obs[2]|=binary_dilation(SYS_MASK,iterations=10)
 return obs,vb

def search(a,z,obs,vb,ak=0,zk=0):
 start=(ak,round(a[0]/STEP),round(a[1]/STEP));goal=(zk,round(z[0]/STEP),round(z[1]/STEP))
 if obs[start] or obs[goal]:return None,'endpoint blocked'
 shape=(3,NX,NY);dist=np.full(shape,np.inf,dtype=np.float32);prev=np.full(shape,-1,dtype=np.int32);dist[start]=0
 def encode(k,x,y):return(k*NX+x)*NY+y
 def decode(v):y=v%NY;v//=NY;return(v//NX,v%NX,y)
 def h(x,y):dx=abs(x-goal[1]);dy=abs(y-goal[2]);return max(dx,dy)+.41421356*min(dx,dy)
 heap=[(h(start[1],start[2]),0,*start)];pops=0
 dirs=[(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,1.41421356),(-1,1,1.41421356),(1,-1,1.41421356),(1,1,1.41421356)]
 while heap:
  _,g,k,x,y=heapq.heappop(heap)
  if g>dist[k,x,y]+.001:continue
  pops+=1
  if (k,x,y)==goal:
   path=[];idx=encode(k,x,y)
   while idx!=-1:path.append(decode(idx));idx=int(prev[decode(idx)])
   return path[::-1],str(pops)
  if pops>2400000:return None,'search budget2400000 finergrid'
  for dx,dy,c in dirs:
   xx=x+dx;yy=y+dy
   if not(0<=xx<NX and 0<=yy<NY) or obs[k,xx,yy]:continue
   if dx and dy and (obs[k,x+dx,y] or obs[k,x,y+dy]):continue
   ng=g+c
   if ng+.001<dist[k,xx,yy]:dist[k,xx,yy]=ng;prev[k,xx,yy]=encode(k,x,y);heapq.heappush(heap,(ng+h(xx,yy),ng,k,xx,yy))
  for kk in range(3):
   if kk==k:continue
   if not vb[x,y] and not obs[kk,x,y]:
    ng=g+60
    if ng+.001<dist[kk,x,y]:dist[kk,x,y]=ng;prev[kk,x,y]=encode(k,x,y);heapq.heappush(heap,(ng+h(x,y),ng,kk,x,y))
 return None,'no path'

def add(net,path,a,z,ak=0,zk=0):
 points=[(k,x*STEP,y*STEP) for k,x,y in path];points=[(ak,*a)]+points+[(zk,*z)];segments=[]
 # Compress collinear grid sections, preserving layer switches.
 simple=[points[0]]
 for i in range(1,len(points)-1):
  q=points[i-1];v=points[i];w=points[i+1]
  if q[0]==v[0]==w[0] and abs((v[1]-q[1])*(w[2]-v[2])-(v[2]-q[2])*(w[1]-v[1]))<1e-8:continue
  simple.append(v)
 simple.append(points[-1])
 for q,v in zip(simple,simple[1:]):
  if q[0]!=v[0]:
   existing=any(isinstance(v,p.PCB_VIA) and v.GetNetname()==net and math.dist(xy(v.GetPosition()),q[1:])<1e-6 for v in b.GetTracks())
   if existing:continue
   via=p.PCB_VIA(b);via.SetPosition(pt(q[1:]));via.SetWidth(p.F_Cu,p.FromMM(.6));via.SetDrill(p.FromMM(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(b.FindNet(net));b.Add(via)
  elif math.hypot(q[1]-v[1],q[2]-v[2])>1e-7:
   t=p.PCB_TRACK(b);t.SetStart(pt(q[1:]));t.SetEnd(pt(v[1:]));t.SetWidth(p.FromMM(.15));t.SetLayer(layers[q[0]]);t.SetNet(b.FindNet(net));b.Add(t)
 return len(simple)

def component(label):
 ref,pin=label.split('.')
 a=next(a for f in b.GetFootprints() if f.GetReference()==ref for a in f.Pads() if a.GetNumber()==pin)
 con=b.GetConnectivity();q=[a];seen=set();vias=[]
 while q:
  a=q.pop();key=a.m_Uuid.AsString()
  if key in seen:continue
  seen.add(key)
  if a.GetClass()=='PCB_VIA':vias.append(xy(a.GetPosition()))
  q.extend(con.GetConnectedTracks(a));q.extend(con.GetConnectedPads(a))
 return seen,vias


from scipy.ndimage import label

def physical(seed):
 con=b.GetConnectivity();q=[seed];seen=set();anchors=[]
 while q:
  item=q.pop();uid=item.m_Uuid.AsString()
  if uid in seen:continue
  seen.add(uid)
  if isinstance(item,p.PAD):
   for k,l in enumerate(layers):
    if item.IsOnLayer(l):anchors.append((k,*xy(item.GetPosition())))
  elif isinstance(item,p.PCB_VIA):
   for k in range(3):anchors.append((k,*xy(item.GetPosition())))
  elif item.GetLayer() in layers:
   k=layers.index(item.GetLayer());anchors.extend([(k,*xy(item.GetStart())),(k,*xy(item.GetEnd()))])
  q.extend(con.GetConnectedTracks(item));q.extend(con.GetConnectedPads(item))
 return seen,list(set(anchors))

def free_regions(obs,vb):
 lab=[];offsets=[];total=1
 for k in range(3):
  a,n=label(~obs[k]);offsets.append(total);a=np.where(a>0,a+total,0);lab.append(a);total+=n+1
 parent=list(range(total+1))
 def root(i):
  while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a in range(3):
  for c in range(a+1,3):
   valid=(~vb)&(~obs[a])&(~obs[c]);pairs=np.unique(np.stack([lab[a][valid],lab[c][valid]],axis=1),axis=0)
   for x,y in pairs:parent[root(int(x))]=root(int(y))
 lut=np.array([root(i) for i in range(total+1)])
 return [lut[a] for a in lab]


net='VBUS_5V';obs,vb=masks(net);obs[0,:,:]=True;obs[2,:,:]=True;vb[:,:]=True
path,why=search((7.9,5.875),(11.65,5.25),obs,vb,1,1)
if not path:raise RuntimeError(why)
add(net,path,(7.9,5.875),(11.65,5.25),1,1)
removed=[]
for t in list(b.GetTracks()):
 if t.GetNetname()==net and not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.In2_Cu and max(t.GetStart().y,t.GetEnd().y)<=p.FromMM(5.875) and min(t.GetStart().x,t.GetEnd().x)>=p.FromMM(7.9):
  removed.append(t.m_Uuid.AsString());b.Delete(t)
b.BuildConnectivity();filler=p.ZONE_FILLER(b);filler.Fill(b.Zones());p.SaveBoard(str(D/'power_integrated_study.kicad_pcb'),b)
(D/'revB_bridge.json').write_text(json.dumps({'route_grid':path,'why':why,'removed_dangling_In2':removed},indent=2));print('PASS route',len(path),'remove',len(removed))
