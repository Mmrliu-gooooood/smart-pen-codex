import geometry as g,json,math,types
c=types.SimpleNamespace(g=g,__file__=str(g.D/'router_core.py'))
s=(g.D/'router_core.py').read_text();s=s.replace("b=p.LoadBoard(str(D.parents[2]/'hardware/pressure_joint_native_0433/native/mainboard_revD.kicad_pcb'))","b=g.b")
s=s.replace('for t in b.GetTracks():','for t in b.GetTracks():\n  if t.m_Uuid.AsString()in SKIP:continue')
c.SKIP={'13079769-348d-5142-9cb4-1d44ec56a7b8','fb1700a3-5c27-5c36-9d84-b9492b46b711'}
exec(s,c.__dict__)
kept=[]
from scipy.ndimage import label
p=g.p
remove={'13079769-348d-5142-9cb4-1d44ec56a7b8','fb1700a3-5c27-5c36-9d84-b9492b46b711'}
g.old=[t for t in g.old if t.m_Uuid.AsString()not in remove]
parts=json.loads((g.D/'trial2_parts.json').read_text());irq=[]
for key,ts in parts.items():
 for q in ts:
  if q['type']=='via':t=g.via(q['net'],q['start']);t.SetWidth(p.F_Cu,round(q['width']*1e6));t.SetDrill(round(q['drill']*1e6))
  else:t=g.track(q['net'],g.b.GetLayerID(q['layer']),q['start'],q['end'],q['width'])
  if q['net']=='PICKUP_INT_N':irq.append(t)
  else:
   z=t.Duplicate();kept.append(z);c.b.Add(z);g.objs.append(t)
rows=[]
for scenario in ['before_greedy_IRQ','after_greedy_IRQ']:
 if scenario.startswith('after'):
  for t in irq:
   z=t.Duplicate();kept.append(z);c.b.Add(z);g.objs.append(t)
 for net,mp,up in [('PICKUP_INT_N','U501.12','U101.6'),('AON_I2C_SCL','U501.1','U101.10'),('AON_I2C_SDA','U501.4','U101.11')]:
  obs,vb=c.masks(net,.15)
  for side,pad,box in [('MEMS',mp,(1,6,78,84)),('MCU',up,(.4,5.5,7.5,13.5))]:
   x,y=g.xy(g.pm[pad]);ix,iy=round(x/c.STEP),round(y/c.STEP);allowed=~obs[0].copy();xmin,xmax,ymin,ymax=[round(z/c.STEP)for z in box];allowed[:xmin,:]=False;allowed[xmax+1:,:]=False;allowed[:,:ymin]=False;allowed[:,ymax+1:]=False;lab,_=label(allowed);marker=lab[ix,iy];mask=lab==marker if marker else c.np.zeros_like(allowed);pts=c.np.argwhere(mask&~vb);ordered=sorted([(float(xx*c.STEP),float(yy*c.STEP))for xx,yy in pts],key=lambda z:math.dist(z,(x,y)));chosen=[]
   for a in ordered:
    if any(math.dist(a,z)<.65 for z in chosen):continue
    v=g.via(net,a);v.SetWidth(p.F_Cu,450000);v.SetDrill(200000)
    if g.errors([v]):continue
    chosen.append(a)
    if len(chosen)>=8:break
   exact_all=[]
   if side=='MEMS':
    for a in ordered:
     v=g.via(net,a);v.SetWidth(p.F_Cu,450000);v.SetDrill(200000)
     if not g.errors([v]):exact_all.append(a)
   diameter=max((math.dist(a,z)for a in exact_all for z in exact_all),default=0)
   row={'all_exact_clear_MEMS_grid_ports':exact_all,'MEMS_port_set_diameter_mm':diameter,'two_045_vias_other_net_min_center_spacing_mm':.6,'scenario':scenario,'side':side,'pad':pad,'net':net,'local_box_mm':box,'local_F_component_grid_points':int(mask.sum()),'grid_accessible_via_points':len(pts),'spaced_exact_clear_via_ports':chosen,'F_path_not_exact_native_verified':True};rows.append(row);print(scenario,pad,len(pts),chosen,flush=True)
(g.D/'local_domains.json').write_text(json.dumps({'scope':'local F connectivity within stated box; grid conservative; listed vias independently finite-checked, no complete simultaneous paths or long route claimed','rows':rows},indent=2)+'\n')
