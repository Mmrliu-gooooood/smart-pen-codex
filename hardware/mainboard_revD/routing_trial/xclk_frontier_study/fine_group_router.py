#!/usr/bin/python3
"""Conservative local two-signal-layer grid search. Actual KiCad DRC is required afterwards."""
from pathlib import Path
import pcbnew as p,numpy as np,math,heapq,json,time,sys,os
D=Path(__file__).resolve().parent;STEP=.025;NX=481;NY=3801;TRACK_HALF=.127/2;EXTRA=.005
FINE=set(json.loads((D.parent/'fine_signal_process/fine_seed_v7_manifest.json').read_text())['fine_netclass_exact_names'])
def pair_clearance(other):return .127 if other in FINE else .15
def margin_to(other):return pair_clearance(other)+TRACK_HALF+EXTRA
source=sys.argv[1] if len(sys.argv)>1 else 'knownnets_commissioning'
outname=sys.argv[2] if len(sys.argv)>2 else 'knownnets_digital'
b=p.LoadBoard(str(D/(source+'.kicad_pcb')));layers=[p.F_Cu,p.B_Cu];results=[]
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

def masks(net):
 assert net in FINE, 'This process router may only draw explicitly approved fine signal nets'
 obs=np.zeros((2,NX,NY),bool);vb=np.zeros((NX,NY),bool)
 obs[:,:math.ceil(.6/STEP),:]=True;obs[:,math.floor(11.4/STEP)+1:,:]=True;obs[:,:,:math.ceil(.6/STEP)]=True;obs[:,:,math.floor(94.4/STEP)+1:]=True
 vb[:math.ceil(.8/STEP),:]=True;vb[math.floor(11.2/STEP)+1:,:]=True;vb[:,:math.ceil(.8/STEP)]=True;vb[:,math.floor(94.2/STEP)+1:]=True
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
    for k in range(2):capsule(obs[k],a,a,radius+margin_to(t.GetNetname()))
   capsule(vb,a,a,.3+radius+pair_clearance(t.GetNetname())+.01 if other else .3+.25+.01)
  else:
   radius=p.ToMM(t.GetWidth())/2
   if t.GetLayer() in layers:
    if other:capsule(obs[layers.index(t.GetLayer())],a,z,radius+margin_to(t.GetNetname()))
   if other:capsule(vb,a,z,radius+.3+pair_clearance(t.GetNetname())+.01)
 # Reuse an already fabricated same-net via; no new drill there.
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) and t.GetNetname()==net:
   x,y=xy(t.GetPosition());ix=round(x/STEP);iy=round(y/STEP)
   if not obs[0,ix,iy] and not obs[1,ix,iy]:vb[ix,iy]=False
 return obs,vb

def search(a,z,obs,vb,ak=0,zk=0):
 start=(ak,round(a[0]/STEP),round(a[1]/STEP));goal=(zk,round(z[0]/STEP),round(z[1]/STEP))
 if obs[start] or obs[goal]:return None,'endpoint blocked'
 shape=(2,NX,NY);dist=np.full(shape,np.inf,dtype=np.float32);prev=np.full(shape,-1,dtype=np.int32);dist[start]=0
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
  kk=1-k
  if not vb[x,y] and not obs[kk,x,y]:
   ng=g+50
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
   t=p.PCB_TRACK(b);t.SetStart(pt(q[1:]));t.SetEnd(pt(v[1:]));t.SetWidth(p.FromMM(.127));t.SetLayer(layers[q[0]]);t.SetNet(b.FindNet(net));b.Add(t)
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
pads={}
for fp in b.GetFootprints():
 for a in fp.Pads():pads.setdefault(a.GetNetname(),[]).append((fp.GetReference()+'.'+a.GetNumber(),xy(a.GetPosition())))
skip={'GND','3V3_AON','RF_SIP','RF_ANT'}
priority=['ISO_GATE','SCCB_EN_SAFE','IO_ENABLE_LINK','SCCB_ENABLE_LINK','UNUSED_A_INPUT','UNUSED_B_INPUT','STRAP_GPIO3','STRAP_GPIO45','STRAP_GPIO46','CAM_IO_EN','CAM_PWR_EN','CAM_BUS_EN','ILLUM_STROBE','CAM_SCL','CAM_SDA','SENS_SCL','SENS_SDA']
if os.environ.get('IC_ONLY')=='1':pads={n:[a for a in aa if a[0].startswith('U')] for n,aa in pads.items()}
for net in pads:pads[net].sort(key=lambda a:(0 if a[0].startswith('U101.') else 1 if a[0].startswith('U2') else 2,a[0]))
selected=sys.argv[3].split(',') if len(sys.argv)>3 else priority
for net in selected:
 if net in skip or net not in pads or len(pads[net])<2:continue
 assert net in FINE, net
 remaining=pads[net][1:];connected=[pads[net][0]]
 while remaining:
  choices=[(math.dist(a[1],z[1]),a,z) for a in connected for z in remaining];_,a,z=min(choices)
  b.BuildConnectivity();ca,va=component(a[0]);cz,vz=component(z[0])
  if ca&cz:
   remaining.remove(z);connected.append(z);continue
  ap=min(va,key=lambda v:math.dist(v,z[1])) if va else a[1];zp=min(vz,key=lambda v:math.dist(v,ap)) if vz else z[1];ak=1 if va else 0;zk=1 if vz else 0
  obs,vb=masks(net);t0=time.time();path,why=search(ap,zp,obs,vb,ak,zk)
  result={'net':net,'from':a[0],'to':z[0],'success':path is not None,'actual_start':ap,'start_layer':ak,'actual_end':zp,'end_layer':zk,'search':why,'seconds':round(time.time()-t0,3)}
  if path:result['points']=add(net,path,ap,zp,ak,zk)
  print(result,flush=True);results.append(result);remaining.remove(z);connected.append(z)
 out=D/(outname+'.kicad_pcb');p.SaveBoard(str(out),b)
# Fill after readback; restoring project prevents SaveBoard resetting default .15mm rule.
out=D/(outname+'.kicad_pcb');p.SaveBoard(str(out),b);b=p.LoadBoard(str(out));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out),b);(D/(outname+'.kicad_pro')).write_text((D/(source+'.kicad_pro')).read_text());(D/(outname+'_search.json')).write_text(json.dumps(results,indent=2))

(D/(outname+'.kicad_dru')).write_text((D/(source+'.kicad_dru')).read_text())
