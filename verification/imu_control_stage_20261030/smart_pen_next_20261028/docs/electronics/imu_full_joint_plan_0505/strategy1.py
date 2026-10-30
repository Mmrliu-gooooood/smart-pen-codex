import local_sources as local,types,json,sys
from pathlib import Path
g=local.g;p=g.p;D=local.D;F=p.F_Cu
c=types.SimpleNamespace(g=g,SKIP=set(local.base['removed']),__file__=str(D/'router_core.py'));exec((D/'router_core.py').read_text(),c.__dict__);c.D=D;exec((D/'cpp_search.py').read_text(),c.__dict__)
parts=local.parts;kept=[];g.objs.extend(sum(parts.values(),[]))
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
jobs=[('AON_I2C_SCL','scl_pullup',port((2.65,80.9)),pad('R501.2'),0,(.4,7.5,79.7,88)),('AON_I2C_SDA','sda_pullup',port((2.375,82.675)),pad('R502.2'),2,(.4,8,79.7,88)),('AON_I2C_SCL','scl_long',port((3.925,12.475)),port((2.65,80.9)),1,None),('AON_I2C_SDA','sda_long',port((2.575,13.1)),port((2.375,82.675)),2,None),('PICKUP_INT_N','irq_long',port((3.275,8.9)),port((4.7,80.125)),0,None)]
for args in jobs:
 if not run(*args):break

def spec(t):
 v=isinstance(t,p.PCB_VIA)
 return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else g.b.GetLayerName(t.GetLayer()),a=[t.GetStart().x/1e6,t.GetStart().y/1e6],b=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
(D/'strategy1.json').write_text(json.dumps({'status':'MODEL_ONLY','removed':local.base['removed'],'parent_sha':local.base['parent_sha'],'records':report,'complete_all':len(report)==5 and all(r['complete']for r in report),'parts':{k:[spec(t)for t in ts]for k,ts in parts.items()}},indent=2)+'\n')
