import geometry as g,json,sys
p=g.p;F=p.F_Cu;B=p.B_Cu
A='3V3_AON'
# Existing IMU AON via at (4.35,85.6) is current fixed source; connect right pullup without new via.
parts={'pullup_left':[g.track(A,F,(1.775,86.5),(.875,86.5),.2),g.via(A,(.875,86.5))], 'pullup_right':[g.track(A,F,(4.825,86.65),(4.35,86.175),.2),g.track(A,F,(4.35,86.175),(4.35,84.5),.2)]}
print({n:g.errors(ts)for n,ts in parts.items()},flush=True)
remove=['13079769-348d-5142-9cb4-1d44ec56a7b8','fb1700a3-5c27-5c36-9d84-b9492b46b711']
g.old=[t for t in g.old if t.m_Uuid.AsString()not in remove]
ps=[(2.65,79.9),(2.65,79.1),(5.72,79.1),(5.72,80.7)]
parts['aon_beam_reconnect']=[g.track(A,F,a,b,.25)for a,b in zip(ps,ps[1:])]
print('joint_aon',g.errors(sum(parts.values(),[])),flush=True)
g.objs.extend(sum(parts.values(),[]))
import router_core as c
c.D=g.D
for t in list(c.b.GetTracks()):
 if t.m_Uuid.AsString() in remove:c.b.Remove(t)
exec((g.D/'cpp_search.py').read_text(),c.__dict__)
# Add the two clear proposed AON branches in memory only, shared obstacles for whole trial.
for items in parts.values():
 for t in items:
  z=t.Duplicate();c.b.Add(z)

def compact(path):
 out=[path[0]]
 for a,b,d in zip(path,path[1:],path[2:]):
  if a[0]==b[0]==d[0]and(b[1]-a[1])*(d[2]-b[2])==(b[2]-a[2])*(d[1]-b[1]):continue
  out.append(b)
 out.append(path[-1]);return out
nets=[('PICKUP_INT_N',['U101.6','U501.12']),('AON_I2C_SCL',['U101.10','U501.1','R501.2']),('AON_I2C_SDA',['U101.11','U501.4','R502.2'])]
report={}
for net,labels in nets:
 report[net]=[]
 for target in labels[1:]:
  obs,vb=c.masks(net,.15)
  # Only actual same-net copper components. No disembodied endpoint anchors.
  groups=c.parts(net,labels); start=next(gr for gr in groups if labels[0] in gr[1]); dest=next(gr for gr in groups if target in gr[1]);ss=c.anchors(start,obs);gg=c.anchors(dest,obs)
  path,why=c.cpp_search(ss,gg,obs,vb,penalties=(0.,0.,1.));print(net,target,why,flush=True)
  if path is None:
   report[net].append({'target':target,'failure':why});break
  q=compact(path);new=[]
  for aa,zz in zip(q,q[1:]):
   k,x,y=aa;kk,u,v=zz;a=(x*c.STEP,y*c.STEP);z=(u*c.STEP,v*c.STEP)
   if k!=kk:
    t=g.via(net,a);t.SetWidth(F,450000);t.SetDrill(200000);new.append(t)
   else:new.append(g.track(net,c.layers[k],a,z,.15))
  err=g.errors(new);print('exact_errors',len(err),err[:4],flush=True)
  report[net].append({'target':target,'why':why,'path':[[c.b.GetLayerName(c.layers[k]),x*c.STEP,y*c.STEP]for k,x,y in q],'finite_errors':err})
  if err:break
  parts[net+'_'+target]=new;g.objs.extend(new);c.add(net,path,.15)
(g.D/'grid_joint_trial2.json').write_text(json.dumps(report,indent=2)+'\n')

(g.D/'trial2_parts.json').write_text(json.dumps({k:[dict(type='via'if isinstance(t,p.PCB_VIA)else'track',net=t.GetNetname(),layer='through'if isinstance(t,p.PCB_VIA)else g.b.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if isinstance(t,p.PCB_VIA)else None)for t in ts]for k,ts in parts.items()},indent=2)+'\n')
