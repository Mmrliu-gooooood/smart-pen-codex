#!/usr/bin/env python3
import pcbnew as b,numpy as np,scipy.ndimage as nd,heapq,pathlib,math,json
P=pathlib.Path(__file__).resolve().parents[1];bd=b.LoadBoard(str(P/'pickup_contact.kicad_pcb'));S=.05;NX=241;NY=401
tracks=[];vias=[]
def xy(p):return (b.ToMM(p.x),b.ToMM(p.y))
def grid(p):return tuple(round(v/S) for v in p)
def pt(p):return b.VECTOR2I(b.FromMM(p[0]),b.FromMM(p[1]))
pads=[]
for f in bd.GetFootprints():
 for p in f.Pads():
  box=p.GetBoundingBox();pads.append((p.GetNetCode(),xy(p.GetPosition()),(b.ToMM(box.GetLeft()),b.ToMM(box.GetTop()),b.ToMM(box.GetRight()),b.ToMM(box.GetBottom()))))
pads.sort(key=lambda p:(p[0],p[1]))
def rect(mask,box,inflate):
 x0,y0,x1,y1=box;mask[max(0,int(math.floor((x0-inflate)/S))):min(NX,int(math.ceil((x1+inflate)/S))+1),max(0,int(math.floor((y0-inflate)/S))):min(NY,int(math.ceil((y1+inflate)/S))+1)]=1

def obstacles(net):
 raw=np.zeros((2,NX,NY),dtype=bool)
 for n,pos,box in pads:
  if n!=net:rect(raw[0],box,0)
 for n,l,a,z in tracks:
  if n==net:continue
  steps=max(abs(z[0]-a[0]),abs(z[1]-a[1]))
  for k in range(steps+1):
   x=round(a[0]+(z[0]-a[0])*k/max(1,steps));y=round(a[1]+(z[1]-a[1])*k/max(1,steps));raw[l,x,y]=1
  # inflate track copper separately later conservative allraw .30 vs pad .225
 for n,p in vias:
  if n!=net:
   x,y=p;rect(raw[0],((x*S-.3),(y*S-.3),(x*S+.3),(y*S+.3)),0);rect(raw[1],((x*S-.3),(y*S-.3),(x*S+.3),(y*S+.3)),0)
 blocked=np.empty_like(raw)
 for l in range(2):blocked[l]=nd.distance_transform_edt(~raw[l])*S < .30
 # pad clearance only .225 needed at fine-pitch LGA; replace region near chip computed accurately
 for l in [0]:
  region=np.zeros((NX,NY),bool)
  for n,pos,box in pads:
   if n!=net:rect(region,box,.225)
  for n,ll,a,z in tracks:
   if n==net or ll!=l:continue
   for k in range(max(abs(z[0]-a[0]),abs(z[1]-a[1]))+1):
    steps=max(abs(z[0]-a[0]),abs(z[1]-a[1]));x=round(a[0]+(z[0]-a[0])*k/max(1,steps));y=round(a[1]+(z[1]-a[1])*k/max(1,steps));rect(region,(x*S,y*S,x*S,y*S),.30)
  # use main conservative raw away from LGA
  blocked[l,94:147,134:187]=region[94:147,134:187]
 # Central body prohibits unrelated routes; back side no routing under entire MEMS body.
 rect(blocked[0],(5.5,7.5,6.5,8.5),0);rect(blocked[1],(4.95,6.95,7.05,9.05),0)
 blocked[:,:12,:]=1;blocked[:,-12:,:]=1;blocked[:,:,:12]=1;blocked[:,:,-12:]=1
 viaok=np.ones((NX,NY),bool)
 for l in range(2):viaok &= nd.distance_transform_edt(~raw[l])*S>.55
 rect(viaok,(0,0,0,0),0) if False else None
 viaok[:16,:]=False;viaok[-16:,:]=False;viaok[:,:16]=False;viaok[:,-16:]=False
 viaok[94:147,134:187]=False
 pad_holes=np.zeros((NX,NY),bool)
 for n,pos,box in pads:rect(pad_holes,box,.30)
 viaok[pad_holes]=False
 for n,pp in vias:
  xx,yy=pp
  for x in range(max(0,xx-12),min(NX,xx+13)):
   for y in range(max(0,yy-12),min(NY,yy+13)):
    if math.hypot(x-xx,y-yy)*S<.6:viaok[x,y]=False
  if n==net:viaok[xx,yy]=True
 return blocked,viaok

def route(net,a,z):
 blocked,viaok=obstacles(net);start=a;goal=z
 if blocked[start] or blocked[goal]:print('blocked endpoints',net,a,z);return None
 def h(s):return abs(s[1]-z[1])+abs(s[2]-z[2])+20*(s[0]!=z[0])
 heap=[(h(start),0,start)];cost={start:0};prev={};done=False
 while heap:
  _,g,s=heapq.heappop(heap)
  if g!=cost[s]:continue
  if s==goal:done=True;break
  l,x,y=s
  neigh=[(l,x+dx,y+dy,14 if dx and dy else 10) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]]
  if viaok[x,y]:neigh.append((1-l,x,y,250))
  for ll,xx,yy,w in neigh:
   t=(ll,xx,yy)
   if not(0<=xx<NX and 0<=yy<NY) or blocked[t]:continue
   if ll==l and xx!=x and yy!=y and (blocked[l,xx,y] or blocked[l,x,yy]):continue
   ng=g+w
   if ng<cost.get(t,1e20):cost[t]=ng;prev[t]=s;heapq.heappush(heap,(ng+10*h(t),ng,t))
 if not done:return None
 path=[goal]
 while path[-1]!=start:path.append(prev[path[-1]])
 return path[::-1]
def addtrack(net,l,a,z):
 if a==z:return
 t=b.PCB_TRACK(bd);t.SetStart(pt((a[0]*S,a[1]*S)));t.SetEnd(pt((z[0]*S,z[1]*S)));t.SetWidth(b.FromMM(.15));t.SetLayer(b.F_Cu if l==0 else b.B_Cu);t.SetNetCode(net);bd.Add(t);tracks.append((net,l,a,z))
# Explicit outward MEMS escapes, completed before interconnect routing.
def fan(name,paths,vpos):
 net=bd.FindNet(name).GetNetCode()
 for path in paths:
  for a,z in zip(path,path[1:]):addtrack(net,0,grid(a),grid(z))
 for pp in vpos:
  v=b.PCB_VIA(bd);v.SetPosition(pt(pp));v.SetWidth(b.F_Cu,b.FromMM(.6));v.SetDrill(b.FromMM(.3));v.SetViaType(b.VIATYPE_THROUGH);v.SetLayerPair(b.F_Cu,b.B_Cu);v.SetNetCode(net);bd.Add(v);vias.append((net,grid(pp)))
fan('AON_I2C_SCL',[[(5.2375,7.25),(4.2,7.25)]],[(4.2,7.25)])
fan('AON_I2C_SDA',[[(5.2375,8.75),(4.2,8.75)]],[(4.2,8.75)])
fan('PICKUP_INT_N',[[(5.75,7.2375),(5.75,6.4)]],[(5.75,6.4)])
fan('3V3_AON',[[(5.2375,7.75),(4.7,7.75),(4.7,8),(4.2,8)],[(5.2375,8.25),(4.7,8.25),(4.7,8)],[(6.7625,7.25),(7.3,7.25),(7.3,7.5),(7.8,7.5)],[(6.7625,7.75),(7.3,7.75),(7.3,7.5)]],[(4.2,8),(7.8,7.5)])
fan('GND',[[(6.7625,8.25),(7.3,8.25),(7.3,8.5),(7.8,8.5)],[(6.7625,8.75),(7.3,8.75),(7.3,8.5)],[(5.75,8.7625),(5.75,9.3),(6,9.3),(6,9.5)],[(6.25,8.7625),(6.25,9.3),(6,9.3)]],[(7.8,8.5),(6,9.5)])
anchors={'AON_I2C_SCL':[(4.2,7.25)],'AON_I2C_SDA':[(4.2,8.75)],'PICKUP_INT_N':[(5.75,6.4)],'3V3_AON':[(4.2,8),(7.8,7.5)],'GND':[(7.8,8.5),(6,9.5)]}
results=[]
# critical single signals then multipoint rails
order=['PICKUP_INT_N','AON_I2C_SCL','AON_I2C_SDA','NIB_CONTACT_N','CONTACT','3V3_AON','GND']
for name in order:
 net=bd.FindNet(name).GetNetCode();points=[(0,*grid(pos)) for n,pos,box in pads if n==net and not(5<=pos[0]<=7 and 7<=pos[1]<=9)];points += [(1,*grid(pp)) for pp in anchors.get(name,[])];tree=[points.pop(0)]
 while points:
  _,a,z=min((abs(a[1]-z[1])+abs(a[2]-z[2])+20*(a[0]!=z[0]),a,z) for a in tree for z in points);path=route(net,a,z)
  if path is None:results.append({'net':name,'failed':[a,z]});print('FAIL',name,a,z);points.remove(z);tree.append(z);continue
  run=path[0];last=run;direction=None
  for t in path[1:]:
   if t[0]!=last[0]:
    addtrack(net,last[0],run[1:],last[1:]);v=b.PCB_VIA(bd);v.SetPosition(pt((t[1]*S,t[2]*S)));v.SetWidth(b.F_Cu,b.FromMM(.6));v.SetDrill(b.FromMM(.3));v.SetViaType(b.VIATYPE_THROUGH);v.SetLayerPair(b.F_Cu,b.B_Cu);v.SetNetCode(net);bd.Add(v);vias.append((net,t[1:]));run=t;direction=None
   else:
    d=(t[1]-last[1],t[2]-last[2])
    if direction is not None and d!=direction:addtrack(net,last[0],run[1:],last[1:]);run=last
    direction=d
   last=t
  addtrack(net,last[0],run[1:],last[1:]);points.remove(z);tree.append(z);results.append({'net':name,'routed':[a,z]});print('OK',name,a,z)
# Remove duplicate holes and unnecessary one-layer fanout vias, not DRC exclusions.
seen=set()
for t in list(bd.GetTracks()):
 if isinstance(t,b.PCB_VIA):
  key=(t.GetPosition().x,t.GetPosition().y,t.GetNetCode())
  if key in seen:bd.Remove(t)
  else:seen.add(key)
# A redundant fanout via may end a route that remained entirely front-side.
for t in list(bd.GetTracks()):
 if not isinstance(t,b.PCB_VIA):continue
 vx,vy=xy(t.GetPosition());layers=set()
 for tr in bd.GetTracks():
  if isinstance(tr,b.PCB_VIA) or tr.GetNetCode()!=t.GetNetCode():continue
  ax,ay=xy(tr.GetStart());zx,zy=xy(tr.GetEnd());den=(zx-ax)**2+(zy-ay)**2
  u=max(0,min(1,((vx-ax)*(zx-ax)+(vy-ay)*(zy-ay))/den)) if den else 0
  if math.hypot(vx-ax-u*(zx-ax),vy-ay-u*(zy-ay))<.375:layers.add(tr.GetLayer())
 if len(layers)<2:bd.Remove(t)
b.SaveBoard(str(P/'pickup_contact.kicad_pcb'),bd);(P/'routing_attempt.json').write_text(json.dumps(results,indent=2));print(len(tracks),'segments',len(vias),'vias')
