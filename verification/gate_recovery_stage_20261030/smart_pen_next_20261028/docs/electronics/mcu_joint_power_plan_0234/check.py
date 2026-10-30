import contextlib,io,json,math
with contextlib.redirect_stdout(io.StringIO()):import plan as z
q=z.q;p=q.p
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
base=build(q.b);out=[]
for attempt,n in zip(z.results,z.models):
 model={net:[r for r in rows if r[0]not in z.removed]for net,rows in base.items()};planes=[];court=[];ground_old={};ground_new={}
 for zone in q.b.Zones():
  if zone.GetIsRuleArea():continue
  l=zone.GetLayer();a=native_fractured_once(zone.GetFilledPolysList(l));b=p.SHAPE_POLY_SET(a)
  for t in n:
   if t.IsOnLayer(l)and t.GetNetname()!=zone.GetNetname():b.BooleanSubtract(q.shape(t,l,150000))
  model[zone.GetNetname()]=[r for r in model[zone.GetNetname()]if not r[0].startswith(q.uid(zone)+'/')]+[(q.uid(zone)+'/model',False,{l:b})]
  
  if zone.GetNetname()=='GND':ground_old.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(a);ground_new.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(b)
  loss=p.SHAPE_POLY_SET();loss.BooleanSubtract(a,b);er=p.SHAPE_POLY_SET(b);er.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);planes.append(dict(net=zone.GetNetname(),layer=q.b.GetLayerName(l),nominal_removed_mm2=loss.Area()/1e12,eroded_components=er.OutlineCount()))
 for t in n:model.setdefault(t.GetNetname(),[]).append((q.uid(t),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
 preserved={}
 for net,rows in base.items():
  a=components(rows);b=components(model[net]);preserved[net]=all(any(set(x)<=set(y)for y in b)for x in a)
 loops={}
 for net,pads in [('CHIP_EN',[r[0]for r in base['CHIP_EN']if r[1]]),('BOOT_N',[r[0]for r in base['BOOT_N']if r[1]]),('3V3_AON',['U101.2','U101.3','C103.1','J106.2']),('GND',['C103.2','J106.3'])]:
  cs=components(model[net]);loops[net]=dict(pads=pads,single_component=any(set(pads)<=set(c)for c in cs))
 for i,t in enumerate(n):
  if not isinstance(t,p.PCB_VIA):continue
  for f in q.b.GetFootprints():
   f.BuildCourtyardCaches()
   for side in [p.F_CrtYd,p.B_CrtYd]:
    a=p.SHAPE_POLY_SET();a.BooleanIntersection(q.shape(t,p.F_Cu),f.GetCourtyard(side))
    if a.Area()>1:court.append(dict(object=i,ref=f.GetReference(),side=q.b.GetLayerName(side),overlap_mm2=a.Area()/1e12))
 projection=[]
 for t in z.old:
  if isinstance(t,p.PCB_VIA)or t.GetLayer()not in [p.F_Cu,p.B_Cu]or t.GetNetname()in ['GND','3V3_AON']:continue
  ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;x=p.SHAPE_POLY_SET();x.BooleanIntersection(shape(t,t.GetLayer()),ground_old[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(shape(t,t.GetLayer()),ground_new[ref]);x.BooleanSubtract(y)
  if x.Area()>1:projection.append(dict(uuid=q.uid(t),net=t.GetNetname(),loss_mm2=x.Area()/1e12,removed_or_rerouted=q.uid(t)in z.removed))
 mapping={q.uid(t):i for i,t in enumerate(n)};errors=[]
 for e in attempt['errors']:
  e=dict(e)
  if e.get('other')in mapping:e['other_model_index']=mapping[e['other']]
  errors.append(e)
 out.append(dict(name=attempt['name'],errors=errors,all_old_pad_components_preserved=all(preserved.values()),failed_old_nets=[k for k,v in preserved.items()if not v],complete_loops=loops,courtyard_overlap=court,nominal_plane_exclusion=planes,old_signal_reference_projection_losses=projection,total_AON_model_trace_mm=sum(math.hypot(t.GetEnd().x-t.GetStart().x,t.GetEnd().y-t.GetStart().y)/1e6 for t in n if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON'),status='REJECTED_GEOMETRY_NOT_NATIVEABLE'))
print(json.dumps(out,indent=2))
