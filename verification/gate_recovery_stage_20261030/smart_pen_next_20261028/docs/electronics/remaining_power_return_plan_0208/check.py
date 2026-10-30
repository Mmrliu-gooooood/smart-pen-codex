from pathlib import Path
import contextlib,io,json,math,hashlib,copy
with contextlib.redirect_stdout(io.StringIO()):import plan as q
p=q.p;D=q.D;b=q.b;new=q.gate3
from finite_copper import build,shape,L,components
from native_polygon import native_fractured_once

def req(x,m):
 if not x:raise RuntimeError(m)
req(not q.errors(new),'joint geometry blocked')
base=build(b);model={n:[(nm,isp,dict(sh))for nm,isp,sh in rows]for n,rows in base.items()}
planes=[];ground_before={};ground_after={}
for z in b.Zones():
 if z.GetIsRuleArea():continue
 l=z.GetLayer();raw=z.GetFilledPolysList(l);v=native_fractured_once(raw);w=p.SHAPE_POLY_SET(v)
 for t in new:
  if isinstance(t,p.PCB_VIA)and t.GetNetname()!=z.GetNetname():w.BooleanSubtract(q.shape(t,l,150000))
 # This is a model exclusion, not a fresh KiCad fill. Keep actual holes and decoding guard.
 names=[nm for nm,isp,sh in model[z.GetNetname()]if nm.startswith(q.uid(z)+'/')]
 model[z.GetNetname()]=[r for r in model[z.GetNetname()]if r[0]not in names]+[(q.uid(z)+'/modeled/'+str(l),False,{l:w})]
 loss=p.SHAPE_POLY_SET();loss.BooleanSubtract(v,w);er=p.SHAPE_POLY_SET(w);er.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 planes.append(dict(uuid=q.uid(z),net=z.GetNetname(),layer=b.GetLayerName(l),modeled_removed_mm2=loss.Area()/1e12,guarded_025_eroded_components=er.OutlineCount(),note='nominal exclusion only, no thermal/fresh-fill/native DRC inference'))
 if z.GetNetname()=='GND':ground_before.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(v);ground_after.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(w)
for i,t in enumerate(new):model.setdefault(t.GetNetname(),[]).append(('model_'+str(i),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
def reach(ns,start,omit=set()):
 rows=[r for r in ns if r[0]not in omit];lookup={r[0]:r for r in rows};req(start in lookup,'start');seen={start};todo=[start]
 while todo:
  _,_,ss=lookup[todo.pop()]
  for nm,isp,tt in rows:
   if nm in seen:continue
   for l in ss.keys()&tt.keys():
    if not ss[l].BBox().Intersects(tt[l].BBox()):continue
    x=p.SHAPE_POLY_SET();x.BooleanIntersection(ss[l],tt[l])
    if x.Area()>1:seen.add(nm);todo.append(nm);break
 return seen
cores={}
for net,start in [('3V3_AON','J106.2'),('GND','J106.3'),('SENS_VIO_1V8','J202.23')]:
 x=reach(base[net],start);y=reach(model[net],start);a=sorted(n for n,isp,_ in base[net]if isp and n in x);c=sorted(n for n,isp,_ in model[net]if isp and n in y);req(set(a)<=set(c),'lostoldcore');cores[net]=dict(before=a,after=c,added=sorted(set(c)-set(a)))
req(set(cores['3V3_AON']['added'])=={'U301.1','C301.1'},'AON target');req(set(cores['GND']['added'])=={'U301.2','C302.2','C303.2','R301.2'},'GND target')
# Every existing physical pad component must remain coherent. No existing net is removed.
for n,ns in base.items():
 oldc=components(ns);newc=components(model[n]);req(all(any(set(a)<=set(c)for c in newc)for a in oldc),'lost existing padcomponent '+n)
negative=[]
for net,i,pad in [('GND',3,'U301.2'),('GND',4,'C302.2'),('GND',5,'C303.2'),('GND',6,'R301.2')]:
 st='J106.2'if net=='3V3_AON'else'J106.3';x=reach(model[net],st,{'model_'+str(i)});req(pad not in x,'negative did not disconnect '+pad);negative.append(dict(removed_model_object=i,pad=pad,core_disconnected=True))
x=reach(model['3V3_AON'],'J106.2',{'model_'+str(i)for i in range(2)});req('U301.1'not in x and'C301.1'not in x,'negative AON group');negative.append(dict(removed_model_objects=list(range(2)),pads=['U301.1','C301.1'],core_disconnected=True))
projection=[]
for t in q.old:
 if isinstance(t,p.PCB_VIA)or t.GetNetname()in['GND','3V3_AON','CAM_3V3_SW','SENS_VIO_1V8']:continue
 ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu
 a=p.SHAPE_POLY_SET();a.BooleanIntersection(shape(t,t.GetLayer()),ground_before[ref]);c=p.SHAPE_POLY_SET();c.BooleanIntersection(shape(t,t.GetLayer()),ground_after[ref]);a.BooleanSubtract(c)
 if a.Area()/1e12>1e-8:projection.append(dict(uuid=q.uid(t),net=t.GetNetname(),loss_mm2=a.Area()/1e12))
# Reuse existing source-connected ground accesses, not guessed vacant holes.
existing=[]
for at in [[7.6,74],[3.8875,66.875]]:
 ts=[t for t in q.old if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND'and q.xy(t)==at];req(len(ts)==1,'existing via missing');req(q.uid(ts[0])in reach(base['GND'],'J106.3'),'existingvia notcore');existing.append(dict(uuid=q.uid(ts[0]),at=at))
aonvia=[t for t in q.old if isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON'and q.xy(t)==[10.9,64.875]];req(len(aonvia)==1 and q.uid(aonvia[0])in reach(base['3V3_AON'],'J106.2'),'existing AON via not core')
# Complete local cap/switch loops; JP commissioning boundary is deliberately not traversed.
pairs=[]
for n,a,c in [('3V3_AON','U301.1','C301.1'),('GND','U301.2','C301.2'),('GND','U301.2','C302.2'),('GND','U301.2','C303.2'),('GND','U301.2','R301.2'),('CAM_3V3_PRELINK','U301.6','C302.1'),('CAM_CT','U301.4','C303.1'),('CAM_ON','U301.3','R301.1')]:
 req(c in reach(model[n],a),'local pair missing');pairs.append([n,a,c])
req(q.pm['JP301.1'].GetNetname()!=q.pm['JP301.2'].GetNetname(),'JP domains')
# New hole footprint exclusion is separately reported. Ordinary body polygons are not fabrication approvals.
courtyard=[]
for i,t in enumerate(new):
 if not isinstance(t,p.PCB_VIA):continue
 for f in b.GetFootprints():
  f.BuildCourtyardCaches()
  for side in [p.F_CrtYd,p.B_CrtYd]:
   poly=f.GetCourtyard(side)
   if not poly.OutlineCount():continue
   x=p.SHAPE_POLY_SET();x.BooleanIntersection(q.shape(t,p.F_Cu),poly)
   if x.Area()>1:courtyard.append(dict(object=i,ref=f.GetReference(),side=b.GetLayerName(side),intersection_mm2=x.Area()/1e12))
result=dict(status='READ_ONLY_COHERENT_GATE_SUPPLY_RETURN_MODEL_NOFAB',base_sha=q.hashlib.sha256(q.S.read_bytes()).hexdigest(),objects=[q.spec(t)for t in new],current_core=cores,local_pairs=pairs,negative=negative,existing_ground_accesses=existing,existing_shared_AON_access=dict(uuid=q.uid(aonvia[0]),at=[10.9,64.875]),plane_model=planes,signal_reference_projection_loss=projection,new_via_courtyard_overlap=courtyard,all_existing_pad_components_preserved=True,JP301_open_domain_boundary_preserved=True,limits=['NO native board saved, NO fresh fill or native DRC run','Plane exclusions are geometric estimates; thermal/clearance fill may differ','0.5mm VIN branch follows old gate geometry intent, not current/load/thermal qualification','New ground returns reuse vias shared with other circuitry; dynamic ground impedance unqualified','Nominal hole-pad and courtyard checks do not establish solder mask, filled-via or assembly clearance','Existing global .5mm feed and MCU DFM gates remain; not fullboard safe power'])
print(json.dumps(result,indent=2))
