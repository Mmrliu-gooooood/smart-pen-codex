import sys,contextlib,io,json,math,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'))
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
with contextlib.redirect_stdout(io.StringIO()):import explore as z
q=z.g;p=q.p;new=z.items
baseboard=p.LoadBoard(str(q.S));base=build(baseboard);model=build(q.b)
def req(c,m):
 if not c:raise RuntimeError(m)
def area_inter(x,y):
 a=p.SHAPE_POLY_SET();a.BooleanIntersection(x,y);return a.Area()/1e12
moved=z.fps['J107'];oldfp=next(f for f in baseboard.GetFootprints()if f.GetReference()=='J107')
moved_errors=[]
for pad in moved.Pads():
 for t in q.old+[x for x in q.pads if x.GetParentFootprint().GetReference()!='J107']:
  if pad.GetNetname()==t.GetNetname():continue
  for l in L:
   if pad.IsOnLayer(l)and t.IsOnLayer(l)and area_inter(q.shape(pad,l,150000),q.shape(t,l))>1e-12:moved_errors.append({'pad':pad.GetNumber(),'other':q.desc(t),'net':t.GetNetname(),'layer':q.b.GetLayerName(l)})
plane=[];oldplanes={};newplanes={}
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
 model[zone.GetNetname()]=[r for r in model[zone.GetNetname()]if not r[0].startswith(q.desc(zone)+'/')]+[(q.desc(zone)+'/model',False,{l:b})]
 diff=p.SHAPE_POLY_SET();diff.BooleanSubtract(a,b);e=p.SHAPE_POLY_SET(b);e.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 plane.append({'net':zone.GetNetname(),'layer':q.b.GetLayerName(l),'nominal_loss_mm2':diff.Area()/1e12,'guarded_025_erosion_components':e.OutlineCount()})
for i,t in enumerate(new):model.setdefault(t.GetNetname(),[]).append(('new/'+str(i),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
comp={n:components(rows)for n,rows in model.items()};bcomp={n:components(rows)for n,rows in base.items()}
preserved={n:all(any(set(a)<=set(b)for b in comp[n])for a in rows)for n,rows in bcomp.items()}
cores={}
for net,start in [('3V3_AON','J106.2'),('GND','J106.3'),('SENS_VIO_1V8','J202.23')]:
 before=next(c for c in bcomp[net]if start in c);after=next(c for c in comp[net]if start in c);cores[net]={'before':before,'after':after,'total':sum(r[1]for r in model[net])};req(set(before)<=set(after),'core loss '+net)
imu={'3V3_AON':['U501.2','U501.3','U501.9','U501.10','C501.1','C502.1','C503.1'],'GND':['U501.5','U501.6','U501.7','U501.8','C501.2','C502.2','C503.2']}
for n,pads in imu.items():req(set(pads)<=set(cores[n]['after']),'IMU core '+n)
old_j={}
for pad in oldfp.Pads():
 name='J107.'+pad.GetNumber();old_j[name]={'net':pad.GetNetname(),'old':next(c for c in bcomp[pad.GetNetname()]if name in c),'new':next(c for c in comp[pad.GetNetname()]if name in c)}
neg=[]
for n,expected in imu.items():
 nodes=[r for r in model[n]if not (r[0].startswith('new/') and isinstance(new[int(r[0].split('/')[1])],p.PCB_VIA))]
 cc=next(c for c in components(nodes)if ('J106.2'if n=='3V3_AON'else'J106.3')in c)
 req(not set(expected)&set(cc),'negative expected all IMU offcore '+n);neg.append({'net':n,'deleted_new_access_via':True,'target_all_offcore':expected})
courts=[];fps=[]
for f in q.b.GetFootprints():f.BuildCourtyardCaches()
for i,t in enumerate(new):
 if isinstance(t,p.PCB_VIA):
  for f in q.b.GetFootprints():
   for side in [p.F_CrtYd,p.B_CrtYd]:
    ar=area_inter(q.shape(t,p.F_Cu),f.GetCourtyard(side))
    if ar>1e-12:courts.append({'object':i,'ref':f.GetReference(),'side':q.b.GetLayerName(side),'overlap_mm2':ar})
for other in q.b.GetFootprints():
 if other.GetReference()=='J107':continue
 ar=area_inter(moved.GetCourtyard(p.B_CrtYd),other.GetCourtyard(p.B_CrtYd))
 if ar>1e-12:fps.append({'ref':'J107','other':other.GetReference(),'overlap_mm2':ar})
projection=[]
for t in q.old:
 if isinstance(t,p.PCB_VIA)or t.GetNetname()in ['GND','3V3_AON','SENS_VIO_1V8']:continue
 for ref in {p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}.get(t.GetLayer(),[]):
  a=p.SHAPE_POLY_SET();a.BooleanIntersection(shape(t,t.GetLayer()),oldplanes[ref]);b=p.SHAPE_POLY_SET();b.BooleanIntersection(shape(t,t.GetLayer()),newplanes[ref]);a.BooleanSubtract(b)
  if a.Area()>1:projection.append({'uuid':q.desc(t),'net':t.GetNetname(),'reference_layer':q.b.GetLayerName(ref),'loss_mm2':a.Area()/1e12})
route_errors=q.errors(new)
spec=[]
for i,t in enumerate(new):
 v=isinstance(t,p.PCB_VIA);spec.append({'index':i,'type':'via'if v else'track','net':t.GetNetname(),'layer':'through'if v else q.b.GetLayerName(t.GetLayer()),'start':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'width':t.GetWidth(p.F_Cu)/1e6 if v else t.GetWidth()/1e6,'drill':t.GetDrillValue()/1e6 if v else None})
print(json.dumps({'status':'REJECTED_FIRST_PLACEMENT_GEOMETRY_ONLY_NO_NATIVE_NOFAB','accept':False,'source_sha256':hashlib.sha256(q.S.read_bytes()).hexdigest(),'move':{'ref':'J107','old':[3.2,84,180,'B.Cu'],'new':[3.2,88,180,'B.Cu']},'old_J107_components':old_j,'route_errors':route_errors,'moved_pad_errors':moved_errors,'all_old_pad_components_preserved':preserved,'core':cores,'IMU_required':imu,'negative':neg,'plane_nominal_only':plane,'new_via_courtyard_intersections':courts,'moved_FP_courtyard':fps,'old_signal_projection_losses':projection,'objects':spec,'limits':['no native save or freshfill/fullDRC','J107 old and new electrical pads were isolated but assembly and harness location change','nominal geometry not manufacturing/mask/stress approval','IMU firmware/IRQ/I2C outside this block']},indent=2))
