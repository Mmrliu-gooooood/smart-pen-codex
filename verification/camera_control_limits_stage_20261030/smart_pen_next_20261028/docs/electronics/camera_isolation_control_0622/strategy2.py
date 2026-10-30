import geometry as g,types,json,sys
from pathlib import Path
p=g.p;D=g.D;F=p.F_Cu
class Local:
 def via(self,net,a):
  t=g.via(net,a);t.SetWidth(F,450000);t.SetDrill(200000);return t
local=Local()
c=types.SimpleNamespace(g=g,SKIP=set(),__file__=str(D/'router_core.py'));exec((D/'router_core.py').read_text(),c.__dict__);c.D=D/"topology2_search";c.D.mkdir(exist_ok=True);exec((D/'cpp_search.py').read_text().replace("D/'grid_astar'","D.parent/'grid_astar'"),c.__dict__)
parts={'r203_supply':[g.track('3V3_AON',F,(10.325,72),(10.325,70.5),.3),g.via('3V3_AON',(10.325,70.5))]};kept=[]
g.objs.extend(sum(parts.values(),[]))
for t in g.objs:
 z=t.Duplicate();kept.append(z);c.b.Add(z)
report=[]
def compact(path):
 out=[path[0]]
 for a,b,d in zip(path,path[1:],path[2:]):
  if a[0]==b[0]==d[0]and(b[1]-a[1])*(d[2]-b[2])==(b[2]-a[2])*(d[1]-b[1]):continue
  out.append(b)
 out.append(path[-1]);return out

def run(net,tag,ss_fn,gg_fn,preferred=1,box=None):
 obs,vb=c.masks(net,.15)
 if box:
  xmin,xmax,ymin,ymax=[round(a/c.STEP)for a in box];obs[:,:xmin,:]=True;obs[:,xmax+1:,:]=True;obs[:,:,:ymin]=True;obs[:,:,ymax+1:]=True
 ss=ss_fn(obs);gg=gg_fn(obs);soft=c.np.ones_like(obs);soft[preferred]=0
 path,why=c.cpp_search(ss,gg,obs,vb,soft=soft,penalties=(.25,0.,1.));print(tag,why,flush=True)
 row={'tag':tag,'net':net,'preferred_layer':c.b.GetLayerName(c.layers[preferred]),'search':why,'complete':False};report.append(row)
 if path is None:return False
 path=compact(path);new=[]
 for a,b in zip(path,path[1:]):
  k,x,y=a;kk,u,v=b;aa=(x*c.STEP,y*c.STEP);bb=(u*c.STEP,v*c.STEP)
  if k!=kk:
   # Existing endpoint vias are reused, never stacked into duplicate drill holes.
   if any(isinstance(t,p.PCB_VIA)and t.GetNetname()==net and g.xy(t)==aa for t in list(g.old)+g.objs):continue
   t=local.via(net,aa)
  else:t=g.track(net,c.layers[k],aa,bb,.15)
  new.append(t)
 e=g.errors(new);row.update({'path':[[c.b.GetLayerName(c.layers[k]),x*c.STEP,y*c.STEP]for k,x,y in path],'finite_errors':e});print('finite',len(e),e[:3],flush=True)
 if e:return False
 parts[tag]=new;g.objs.extend(new)
 for t in new:z=t.Duplicate();kept.append(z);c.b.Add(z)
 row['complete']=True;return True

def port(xy):
 def a(obs):
  x,y=[round(v/c.STEP)for v in xy];return{(k,x,y)for k in range(3)if not obs[k,x,y]}
 return a

def pad(name):
 q=g.pm[name];xy=g.xy(q)
 def a(obs):
  x,y=[round(v/c.STEP)for v in xy];return{(k,x,y)for k,l in enumerate(c.layers)if q.IsOnLayer(l)and not obs[k,x,y]}
 return a
jobs=[('CAM_ISO_OE_N','oe_u202_pair',pad('U202.14'),pad('U202.15'),0,(5,9,47,51)),('CAM_ISO_OE_N','oe_u203_pair',pad('U203.14'),pad('U203.15'),0,(5,9,57,61)),('CAM_ISO_OE_N','oe_u201_to_u202',pad('U201.22'),pad('U202.15'),1,(.4,13.5,35,51)),('CAM_ISO_OE_N','oe_u202_to_u203',pad('U202.14'),pad('U203.14'),1,(.4,13.5,47,61)),('CAM_ISO_OE_N','oe_u203_to_r203',pad('U203.15'),pad('R203.1'),1,(.4,13.5,57,74)),('CAM_ISO_OE_N','oe_q201',pad('Q201.3'),pad('R203.1'),0,(.4,13.5,67,74)),('IO_ENABLE_LINK','io_link',pad('JP201.2'),pad('R201.1'),2,(.4,13.5,70,79)),('CAM_IO_EN','io_mcu_pull',pad('U101.48'),pad('R107.1'),0,(.4,13.5,2.5,9)),('CAM_IO_EN','io_long',pad('R107.1'),pad('JP201.1'),2,(.4,13.5,.5,79))]
jobs=[jobs[7],jobs[8],jobs[6]]+jobs[:6]
for args in jobs:
 if not run(*args):break

def spec(t):
 v=isinstance(t,p.PCB_VIA)
 return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else g.b.GetLayerName(t.GetLayer()),a=[t.GetStart().x/1e6,t.GetStart().y/1e6],b=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
(D/'strategy2.json').write_text(json.dumps({'status':'MODEL_ONLY','removed':[],'parent_sha':'5ed5f0ad90f5f15830f50479e0ecc48fe0685ffaff1819ff642a300f9550a1e9','records':report,'complete_all':len(report)==9 and all(r['complete']for r in report),'parts':{k:[spec(t)for t in ts]for k,ts in parts.items()}},indent=2)+'\n')
