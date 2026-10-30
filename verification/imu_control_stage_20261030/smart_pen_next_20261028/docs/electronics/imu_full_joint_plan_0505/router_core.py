from pathlib import Path
import os,sys,json,math,heapq,time
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p,numpy as np
from scipy import ndimage
D=Path(__file__).resolve().parent;b=g.b
STEP=.025;NX=561;NY=3801;layers=[p.F_Cu,p.In3_Cu,p.B_Cu];N=len(layers);rows=[];report=[]
xy=lambda a:(a.x/1e6,a.y/1e6)
def pt(a):return p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6))
def rect(arr,x,y,w,h,m):
 x0=max(0,math.floor((x-w/2-m)/STEP));x1=min(NX,math.ceil((x+w/2+m)/STEP)+1);y0=max(0,math.floor((y-h/2-m)/STEP));y1=min(NY,math.ceil((y+h/2+m)/STEP)+1)
 if x1<=x0 or y1<=y0:return
 xx=np.arange(x0,x1)[:,None]*STEP;yy=np.arange(y0,y1)[None,:]*STEP;arr[x0:x1,y0:y1]|=(abs(xx-x)<=w/2+m)&(abs(yy-y)<=h/2+m)
def capsule(arr,a,z,r):
 x0=max(0,math.floor((min(a[0],z[0])-r)/STEP));x1=min(NX,math.ceil((max(a[0],z[0])+r)/STEP)+1);y0=max(0,math.floor((min(a[1],z[1])-r)/STEP));y1=min(NY,math.ceil((max(a[1],z[1])+r)/STEP)+1)
 if x1<=x0 or y1<=y0:return
 xx=np.arange(x0,x1)[:,None]*STEP;yy=np.arange(y0,y1)[None,:]*STEP;dx=z[0]-a[0];dy=z[1]-a[1];den=dx*dx+dy*dy;u=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/den,0,1)if den else 0;arr[x0:x1,y0:y1]|=(xx-a[0]-u*dx)**2+(yy-a[1]-u*dy)**2<=r*r
def copper_rect(arr,x,y,w,h,m):
 # Equality at requested copper clearance is allowed; 1e-9mm only arithmetic tolerance.
 rect(arr,x,y,w,h,m-1e-9)
def copper_capsule(arr,a,z,r):
 capsule(arr,a,z,r-1e-9)
def actual_edge_masks(width):
 xx=np.arange(NX)[:,None]*STEP;yy=np.arange(NY)[None,:]*STEP
 inside=np.zeros((NX,NY),bool);dist2=np.full((NX,NY),np.inf)
 edges=[]
 for d in b.GetDrawings():
  if d.GetLayer()!=p.Edge_Cuts:continue
  if d.GetShapeStr()!='Line':raise RuntimeError('UNSUPPORTED_EDGE_SHAPE')
  a,z=xy(d.GetStart()),xy(d.GetEnd());edges.append((a,z));dx=z[0]-a[0];dy=z[1]-a[1];den=dx*dx+dy*dy
  u=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/den,0,1);dist2=np.minimum(dist2,(xx-a[0]-u*dx)**2+(yy-a[1]-u*dy)**2)
  if abs(dy)>1e-12:inside^=((a[1]>yy)!=(z[1]>yy))&(xx<(z[0]-a[0])*(yy-a[1])/dy+a[0])
 if len(edges)!=6:raise RuntimeError('EDGE_VERSION_MISMATCH')
 return (~inside)|(dist2<(.25+width/2-1e-9)**2),(~inside)|(dist2<(.25+.225-1e-9)**2)
def masks(net,width):
 obs=np.zeros((N,NX,NY),bool);vb=np.zeros((NX,NY),bool);margin=.1501+width/2
 obs[:,:16,:]=True;obs[:,548:,:]=True;obs[:,:,:]=obs # y domain below chosen root and away from RF
 obs[:,:,:20]=True;obs[:,:,3788:]=True;vb[:20,:]=True;vb[542:,:]=True;vb[:,:30]=True;vb[:,3750:]=True
 # MEMS native rule forbids planes/vias, not tracks. Do not invent a pad-blocking track ban.
 rect(vb,4,82,2,2,.2251)
 # Keep new via holes outside connector conservative underside until qualified.
 rect(vb,7,92,13.9,4,.15)
 for f in b.GetFootprints():
  for a in f.Pads():
   x,y=xy(a.GetPosition());w,h=xy(a.GetSize());ang=round(a.GetOrientationDegrees())%180
   if ang==90:w,h=h,w
   for k,l in enumerate(layers):
    if a.IsOnLayer(l)and a.GetNetname()!=net:copper_rect(obs[k],x,y,w,h,margin)
   rect(vb,x,y,w,h,.2251) if a.GetNetname()==net else copper_rect(vb,x,y,w,h,.375)
 for t in b.GetTracks():
  if t.m_Uuid.AsString()in SKIP:continue
  a,z=xy(t.GetStart()),xy(t.GetEnd());other=t.GetNetname()!=net
  if isinstance(t,p.PCB_VIA):
   r=t.GetWidth(p.F_Cu)/2e6
   if other:
    for k in range(N):copper_capsule(obs[k],a,a,r+margin)
   copper_capsule(vb,a,a,r+.3751) if other else capsule(vb,a,a,t.GetDrillValue()/2e6+.15+.26)
  else:
   r=t.GetWidth()/2e6
   if other:
    if t.GetLayer()in layers:copper_capsule(obs[layers.index(t.GetLayer())],a,z,r+margin)
    copper_capsule(vb,a,z,r+.3751)
 # Reserve bus corridor: no new through-via barrier in right long run. Existing same-net vias remain usable.
 # No invented right-side via blanket ban; exact existing copper preserved.
 for t in b.GetTracks():
  if t.m_Uuid.AsString()in SKIP:continue
  if isinstance(t,p.PCB_VIA)and t.GetNetname()==net:
   x,y=xy(t.GetPosition());ix,iy=round(x/STEP),round(y/STEP)
   if 0<=ix<NX and 0<=iy<NY and not any(obs[:,ix,iy]):vb[ix,iy]=False
 rect(obs[0],4,82,1.15,1.175,width/2)
 eo,ev=actual_edge_masks(width);obs|=eo[None,:,:];vb|=ev
 return obs,vb

def parts(net,labels):
 b.BuildConnectivity();c=b.GetConnectivity();pads=[q for f in b.GetFootprints()for q in f.Pads()if q.GetNetname()==net];todo={q.m_Uuid.AsString():q for q in pads};out=[]
 while todo:
  q=[next(iter(todo.values()))];seen=set();items=[];names=[]
  while q:
   a=q.pop();u=a.m_Uuid.AsString()
   if u in seen:continue
   seen.add(u);items.append(a)
   if u in todo:names.append(a.GetParentFootprint().GetReference()+'.'+a.GetNumber());del todo[u]
   q.extend(c.GetConnectedTracks(a));q.extend(c.GetConnectedPads(a))
  if set(names)&set(labels):out.append((items,names))
 return sorted(out,key=lambda a:-len(a[0]))
def anchors(part,obs):
 out=set()
 def put(k,xy):
  ix,iy=round(xy[0]/STEP),round(xy[1]/STEP)
  if 0<=ix<NX and 0<=iy<NY and not obs[k,ix,iy]:out.add((k,ix,iy))
 for a in part[0]:
  if a.GetClass()=='PAD':
   for k,l in enumerate(layers):
    if a.IsOnLayer(l):put(k,xy(a.GetPosition()))
  elif isinstance(a,p.PCB_VIA):
   for k in range(N):put(k,xy(a.GetPosition()))
  elif a.GetLayer()in layers:
   aa,zz=xy(a.GetStart()),xy(a.GetEnd());n=max(1,math.ceil(math.dist(aa,zz)/.05))
   for u in np.linspace(0,1,n+1):put(layers.index(a.GetLayer()),(aa[0]+u*(zz[0]-aa[0]),aa[1]+u*(zz[1]-aa[1])))
 return out

def search(starts,goals,obs,vb):
 if not starts or not goals:return None,'blocked anchors'
 target=np.zeros((NX,NY),bool)
 for k,x,y in goals:target[x,y]=True
 h=ndimage.distance_transform_edt(~target);dist=np.full((N,NX,NY),np.inf,dtype=np.float32);prev=np.full((N,NX,NY),-1,np.int32)
 enc=lambda k,x,y:(k*NX+x)*NY+y
 def dec(a):y=a%NY;a//=NY;return a//NX,a%NX,y
 heap=[]
 for k,x,y in starts:dist[k,x,y]=0;heap.append((float(h[x,y]),0,k,x,y))
 heapq.heapify(heap);pops=0
 dirs=[(-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,2**.5),(-1,1,2**.5),(1,-1,2**.5),(1,1,2**.5)]
 while heap:
  _,g,k,x,y=heapq.heappop(heap)
  if g>dist[k,x,y]+.001:continue
  pops+=1
  if (k,x,y)in goals:
   path=[];idx=enc(k,x,y)
   while idx!=-1:path.append(dec(idx));idx=int(prev[dec(idx)])
   return path[::-1],pops
  if pops>1500000:return None,'budget'
  for dx,dy,cost in dirs:
   xx,yy=x+dx,y+dy
   if not(0<=xx<NX and 0<=yy<NY)or obs[k,xx,yy]or(dx and dy and(obs[k,x+dx,y]or obs[k,x,y+dy])):continue
   ng=g+cost
   if ng+.001<dist[k,xx,yy]:dist[k,xx,yy]=ng;prev[k,xx,yy]=enc(k,x,y);heapq.heappush(heap,(ng+h[xx,yy],ng,k,xx,yy))
  if not vb[x,y]:
   for kk in range(N):
    if kk==k or obs[kk,x,y]:continue
    ng=g+35
    if ng+.001<dist[kk,x,y]:dist[kk,x,y]=ng;prev[kk,x,y]=enc(k,x,y);heapq.heappush(heap,(ng+h[x,y],ng,kk,x,y))
 return None,'no path'
def add(net,path,w):
 pts=[(k,x*STEP,y*STEP)for k,x,y in path];simple=[pts[0]]
 for i in range(1,len(pts)-1):
  a,v,z=pts[i-1:i+2]
  if a[0]==v[0]==z[0]and abs((v[1]-a[1])*(z[2]-v[2])-(v[2]-a[2])*(z[1]-v[1]))<1e-8:continue
  simple.append(v)
 simple.append(pts[-1])
 for a,z in zip(simple,simple[1:]):
  if a[0]!=z[0]:
   if any(isinstance(t,p.PCB_VIA)and t.GetNetname()==net and math.dist(xy(t.GetPosition()),a[1:])<.035 for t in b.GetTracks()):continue
   t=p.PCB_VIA(b);t.SetPosition(pt(a[1:]));t.SetWidth(p.F_Cu,p.FromMM(.45));t.SetDrill(p.FromMM(.20));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(b.FindNet(net));b.Add(t);rows.append({'uuid':t.m_Uuid.AsString(),'net':net,'type':'via','xy':a[1:],'diameter':.45,'drill':.20})
  elif math.dist(a[1:],z[1:])>1e-6:
   t=p.PCB_TRACK(b);t.SetStart(pt(a[1:]));t.SetEnd(pt(z[1:]));t.SetLayer(layers[a[0]]);t.SetWidth(p.FromMM(w));t.SetNet(b.FindNet(net));b.Add(t);rows.append({'uuid':t.m_Uuid.AsString(),'net':net,'type':'track','a':a[1:],'z':z[1:],'width':w,'layer':b.GetLayerName(layers[a[0]])})

