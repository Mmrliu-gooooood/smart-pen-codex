from pathlib import Path
import sys,json,hashlib,math
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'docs/electronics/imu_control_joint_plan_0444'));import geometry as g
p=g.p;sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
m=json.loads((D/'local_plan.json').read_text());req=lambda c,msg:None if c else (_ for _ in()).throw(RuntimeError(msg));req(hashlib.sha256(g.S.read_bytes()).hexdigest()==m['parent_sha'],'parent')
oldall=list(g.old);g.old=[t for t in g.old if t.m_Uuid.AsString()not in m['removed']];new=[];labels=[]
for tag,ts in m['parts'].items():
 for i,t in enumerate(ts):
  if t['type']=='via':q=g.via(t['net'],t['a']);q.SetWidth(p.F_Cu,round(t['width']*1e6));q.SetDrill(round(t['drill']*1e6))
  else:q=g.track(t['net'],g.b.GetLayerID(t['layer']),t['a'],t['b'],t['width'])
  new.append(q);labels.append(tag+'/'+str(i))
req(not g.errors(new),'joint finite exact')
before=build(g.b);after={n:[x for x in ns if x[0]not in m['removed']]for n,ns in before.items()}
# Conservative model only: subtract .15mm-clearance annulus envelope for each new different-net through via from existing normalized plane copper.
planes={z.m_Uuid.AsString():z for z in g.b.Zones()if not z.GetIsRuleArea()};plane_screen=[]
for net,ns in after.items():
 for i,(name,isp,shapes)in enumerate(ns):
  zu=name.split('/')[0]
  if zu not in planes:continue
  rebuilt={}
  for l,q in shapes.items():
   qq=native_fractured_once(q);area=qq.Area()
   for t in new:
    if isinstance(t,p.PCB_VIA)and t.GetNetname()!=net:qq.BooleanSubtract(g.shape(t,l,150000))
   rebuilt[l]=qq
   if area!=qq.Area():plane_screen.append({'zone':zu,'layer':g.b.GetLayerName(l),'removed_mm2':(area-qq.Area())/1e12})
  ns[i]=(name,isp,rebuilt)
for name,t in zip(labels,new):after.setdefault(t.GetNetname(),[]).append((name,False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
def reach(ns,start):
 dic={x[0]:x[2]for x in ns};req(start in dic,'start');seen={start};todo=[start]
 while todo:
  x=dic[todo.pop()]
  for name,y in dic.items():
   if name in seen:continue
   for l in x.keys()&y.keys():
    if not x[l].BBox().Intersects(y[l].BBox()):continue
    z=p.SHAPE_POLY_SET();z.BooleanIntersection(x[l],y[l])
    if z.Area()>1:seen.add(name);todo.append(name);break
 return seen
prior={}
for net,ns in before.items():
 a=components(ns);b=components(after[net]);req(all(any(set(c)<=set(d)for d in b)for c in a),'old component '+net);prior[net]=[len(a),len(b)]
core={}
for net,start in [('3V3_AON','J106.2'),('GND','J106.3'),('SENS_VIO_1V8','J202.23')]:
 seen=reach(after[net],start);bp=[n for n,isp,_ in before[net]if isp and n in reach(before[net],start)];ap=[n for n,isp,_ in after[net]if isp and n in seen];req(set(bp)<=set(ap),'core no lost');core[net]={'before':sorted(bp),'after':sorted(ap)}
requiredA=['U501.2','U501.3','U501.9','U501.10','C501.1','C502.1','C503.1'];requiredG=['U501.5','U501.6','U501.7','U501.8','C501.2','C502.2','C503.2'];req(set(requiredA)<=set(core['3V3_AON']['after']),'14 AON');req(set(requiredG)<=set(core['GND']['after']),'14 ground')
# Direct metal path, exclude planes so feed does not rely on hypothetical future refill.
metal=[n for n in after['3V3_AON']if '/'not in n[0]or n[0].startswith('aon_')];source='77f42497-a70c-5858-9af0-104c9889f62b';req({'U501.2','U501.3',source}<=reach(metal,'U501.2'),'direct source-via feed')
negative={}
for cut in ['aon_left_reconnect/0','aon_left_reconnect/1','aon_left_reconnect/2','aon_left_reconnect/3']:
 ns=[x for x in metal if x[0]!=cut];negative[cut]=source not in reach(ns,'U501.2');req(negative[cut],'feed negative '+cut)
ports={}
for net,pad,tag in [('AON_I2C_SCL','U501.1','scl_local'),('PICKUP_INT_N','U501.12','irq_local'),('AON_I2C_SDA','U501.4','sda_local')]:
 via_label=next(name for name,t in zip(labels,new)if name.startswith(tag)and isinstance(t,p.PCB_VIA));req(via_label in reach(after[net],pad),'pad-port');ts=[(name,t)for name,t in zip(labels,new)if name.startswith(tag)];tip=next(t for name,t in ts if name==via_label);probe=p.SHAPE_POLY_SET();probe.NewOutline();x,y=g.xy(tip)
 for a,b in [(x+.14,y-.015),(x+.16,y-.015),(x+.16,y+.015),(x+.14,y+.015)]:probe.Append(round(a*1e6),round(b*1e6))
 ns=after[net]+[('B_PORT_PROBE',False,{p.B_Cu:probe})];req('B_PORT_PROBE'in reach(ns,pad),'Bvia connection');cut=[q for q in ns if q[0]!=via_label];req('B_PORT_PROBE'not in reach(cut,pad),'via removal negative');ports[net]={'pad':pad,'xy':[x,y],'B_probe_connected':True,'remove_via_disconnects_B_probe':True}
# All new vias against all physical pads including same-net, already required by geometry.errors; courtyard reporting is separate DFM gate.
ct=[]
for f in g.b.GetFootprints():f.BuildCourtyardCaches()
for name,t in zip(labels,new):
 if not isinstance(t,p.PCB_VIA):continue
 for f in g.b.GetFootprints():
  for l in[p.F_CrtYd,p.B_CrtYd]:
   q=g.shape(t,p.F_Cu);q.BooleanIntersection(f.GetCourtyard(l))
   if q.Area()>1:ct.append({'new':name,'footprint':f.GetReference(),'courtyard_layer':g.b.GetLayerName(l),'overlap_mm2':q.Area()/1e12})
pts=[v['xy']for v in ports.values()];dist=[math.dist(a,b)for i,a in enumerate(pts)for b in pts[:i]];req(min(dist)>=.6,'independent ports')
# Project conservative new plane holes onto every retained old signal; native reference must still be rerun later.
loss={}
for net,ns in after.items():
 for name,isp,ss in ns:
  if name.split('/')[0]not in planes:continue
  original=next(sh for nm,ip,sh in before[net]if nm==name)
  for l,sh in ss.items():
   q=native_fractured_once(original[l]);q.BooleanSubtract(sh);loss.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(q)
reference_losses=[]
for t in g.old:
 if isinstance(t,p.PCB_VIA)or t.GetNetname()in['GND','3V3_AON','SENS_VIO_1V8']:continue
 refs={p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}.get(t.GetLayer(),[])
 for l in refs:
  q=shape(t,t.GetLayer());q.BooleanIntersection(loss[l])
  if q.Area()>1:reference_losses.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'reference':g.b.GetLayerName(l),'area_mm2':q.Area()/1e12})
print(json.dumps({'status':'LOCAL_JOINT_MODEL_ONLY_NO_NATIVE','parent_sha':m['parent_sha'],'joint_finite_errors':[],'new_objects':len(new),'removed_exact':m['removed'],'prior_physical_pad_components':prior,'core':core,'IMU14':{'AON':requiredA,'GND':requiredG},'direct_CS_SA0_feed_to_existing_core_via_without_planes':True,'feed_negative':negative,'ports':ports,'minimum_signal_via_center_separation_mm':min(dist),'new_via_courtyard_intersections':ct,'conservative_plane_antipad_screen':plane_screen,'old_signal_projection_losses_under_conservative_plane_screen':reference_losses,'limits':['No native fill/DRC/ERC qualification; conservative .15mm antipad subtraction is screen only','Long three-net routes and pullup attachments not completed','Same footprints/source, 10k values, I2C address straps and clock copper retained','MEMS outer-fanout stress/courtyard via DFM and all prior parent gates remain']},indent=2))
