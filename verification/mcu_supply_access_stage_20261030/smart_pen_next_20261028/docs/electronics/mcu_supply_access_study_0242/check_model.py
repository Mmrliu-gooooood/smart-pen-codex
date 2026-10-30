import contextlib,io,json,math
import geometry as q
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
base=build(q.b)
with contextlib.redirect_stdout(io.StringIO()):import two_vias as z
p=q.p;new=z.n;model=build(q.b);plane=[]; oldplanes={};newplanes={}
for zone in q.b.Zones():
 if zone.GetIsRuleArea():continue
 l=zone.GetLayer();a=native_fractured_once(zone.GetFilledPolysList(l));b=p.SHAPE_POLY_SET(a)
 for t in new:
  if not t.IsOnLayer(l):continue
  if t.GetNetname()!=zone.GetNetname():b.BooleanSubtract(q.shape(t,l,150000))
  elif isinstance(t,p.PCB_VIA):
   h=p.SHAPE_POLY_SET();h.NewOutline();c=t.GetPosition();r=t.GetDrillValue()/2
   for i in range(256):h.Append(round(c.x+r*math.cos(i*2*math.pi/256)),round(c.y+r*math.sin(i*2*math.pi/256)))
   b.BooleanSubtract(h)
 oldplanes.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(a);newplanes.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(b)
 model[zone.GetNetname()]=[r for r in model[zone.GetNetname()]if not r[0].startswith(q.uid(zone)+'/')]+[(q.uid(zone)+'/model',False,{l:b})]
 diff=p.SHAPE_POLY_SET();diff.BooleanSubtract(a,b);e=p.SHAPE_POLY_SET(b);e.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 plane.append({'net':zone.GetNetname(),'layer':q.b.GetLayerName(l),'nominal_loss_mm2':diff.Area()/1e12,'eroded_components':e.OutlineCount()})
for i,t in enumerate(new):model.setdefault(t.GetNetname(),[]).append(('new/'+str(i),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
preserved={net:all(any(set(x)<=set(y)for y in components(model[net]))for x in components(rows))for net,rows in base.items()}
loops={}
for net,pads in [('3V3_AON',['U101.2','U101.3','C103.1','J106.2']),('GND',['C103.2','J106.3'])]:
 loops[net]={'pads':pads,'single_component':any(set(pads)<=set(c)for c in components(model[net]))}
courts=[]
for i,t in enumerate(new):
 if not isinstance(t,p.PCB_VIA):continue
 for f in q.b.GetFootprints():
  f.BuildCourtyardCaches()
  for side in [p.F_CrtYd,p.B_CrtYd]:
   a=p.SHAPE_POLY_SET();a.BooleanIntersection(q.shape(t,p.F_Cu),f.GetCourtyard(side))
   if a.Area()>1:courts.append({'object':i,'ref':f.GetReference(),'side':q.b.GetLayerName(side),'overlap_mm2':a.Area()/1e12})
fp_overlap=[]
for ref in ['C103','R503']:
 f=z.fps[ref];f.BuildCourtyardCaches();layer=p.F_CrtYd if f.GetLayer()==p.F_Cu else p.B_CrtYd
 for other in q.b.GetFootprints():
  if other.GetReference()==ref:continue
  other.BuildCourtyardCaches();a=p.SHAPE_POLY_SET();a.BooleanIntersection(f.GetCourtyard(layer),other.GetCourtyard(layer))
  if a.Area()>1:fp_overlap.append({'ref':ref,'other':other.GetReference(),'area_mm2':a.Area()/1e12})
projection=[]
for t in q.old:
 if isinstance(t,p.PCB_VIA)or t.GetNetname()in ['GND','3V3_AON','SENS_VIO_1V8']:continue
 refs={p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}.get(t.GetLayer(),[])
 for ref in refs:
  a=p.SHAPE_POLY_SET();a.BooleanIntersection(shape(t,t.GetLayer()),oldplanes[ref]);b=p.SHAPE_POLY_SET();b.BooleanIntersection(shape(t,t.GetLayer()),newplanes[ref]);a.BooleanSubtract(b)
  if a.Area()>1:projection.append({'uuid':q.uid(t),'net':t.GetNetname(),'reference_layer':q.b.GetLayerName(ref),'loss_mm2':a.Area()/1e12})
cores={}
for net,pad in [('3V3_AON','J106.2'),('GND','J106.3')]:
 cs=components(model[net]);cc=next(c for c in cs if pad in c);cores[net]={'core_pad_count':len(cc),'total_physical_pads':sum(r[1]for r in model[net])}
print(json.dumps({'source':'read-only two-via geometric model, no native/freshfill','route_errors':z.results[0]['route_errors'],'moved_pad_errors':z.results[0]['moved_pad_errors'],'all_old_components_preserved':all(preserved.values()),'failed_nets':[k for k,v in preserved.items()if not v],'loops':loops,'plane_nominal':plane,'via_courtyard':courts,'moved_fp_courtyard':fp_overlap,'old_signal_projection_losses':projection,'core_counts':cores},indent=2))
