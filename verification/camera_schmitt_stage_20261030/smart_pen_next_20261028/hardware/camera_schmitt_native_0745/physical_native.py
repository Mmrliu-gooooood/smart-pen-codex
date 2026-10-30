from pathlib import Path
import sys,json,math,hashlib
import geometry_native as g
p=g.p;D=g.D;R=g.R;sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,shape
from native_polygon import native_fractured_once
m=json.loads((D/'materialization.json').read_text());ts={t.m_Uuid.AsString():t for t in g.old};new=[ts[u]for u in m['added']];g.old=[t for u,t in ts.items()if u not in m['added']];errors=g.errors(new)
def req(c,m):
 if not c:raise RuntimeError(m)
req(not errors,'all native finite clear')
ns=build(g.b)['GND'];lookup={n:s for n,_,s in ns};seen={'J106.3'};todo=['J106.3']
while todo:
 x=lookup[todo.pop()]
 for name,y in lookup.items():
  if name in seen:continue
  for l in x.keys()&y.keys():
   if not x[l].BBox().Intersects(y[l].BBox()):continue
   q=p.SHAPE_POLY_SET();q.BooleanIntersection(x[l],y[l])
   if q.Area()>1:seen.add(name);todo.append(name);break
groundvias=[t for u,t in ts.items()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND'and u in seen];req(groundvias,'actual core ground vias')
planes={};holes={}
for z in g.b.Zones():
 if z.GetIsRuleArea():continue
 l=z.GetLayer();key=(z.GetNetname(),l);planes.setdefault(key,p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(l)))
for key,pol in planes.items():
 hs=[]
 for oi in range(pol.OutlineCount()):
  for hi in range(pol.HoleCount(oi)):
   h=p.SHAPE_POLY_SET();h.AddOutline(pol.Hole(oi,hi));hs.append(h)
 holes[key]=hs
for f in g.b.GetFootprints():f.BuildCourtyardCaches()
via_rows=[];courtyards=[]
for u in m['added']:
 t=ts[u]
 if not isinstance(t,p.PCB_VIA):continue
 xy=g.xy(t);near=min(groundvias,key=lambda q:math.dist(xy,g.xy(q)));dist=math.dist(xy,g.xy(near));hole_rows=[]
 for (net,l),hs in holes.items():
  if l not in[p.In1_Cu,p.In2_Cu,p.In4_Cu]:continue
  matches=[]
  for h in hs:
   if not h.Contains(t.GetPosition()):continue
   bb=h.BBox();contained=[{'uuid':uid,'net':q.GetNetname(),'xy':g.xy(q)}for uid,q in ts.items()if isinstance(q,p.PCB_VIA)and h.Contains(q.GetPosition())];matches.append({'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetWidth()/1e6,bb.GetHeight()/1e6],'area_mm2':h.Area()/1e12,'containing_via_centers':contained,'merged_multiple_via_centers':len(contained)>1})
  hole_rows.append({'plane_net':net,'layer':g.b.GetLayerName(l),'center_in_filled_polygon':planes[(net,l)].Contains(t.GetPosition()),'native_holes_containing_center':matches})
 via_rows.append({'uuid':u,'net':t.GetNetname(),'xy':xy,'diameter_mm':t.GetWidth(p.F_Cu)/1e6,'drill_mm':t.GetDrillValue()/1e6,'nearest_actual_core_GND_via':{'uuid':near.m_Uuid.AsString(),'xy':g.xy(near),'center_distance_mm':dist,'copper_annulus_edge_distance_mm':dist-(t.GetWidth(p.F_Cu)+near.GetWidth(p.F_Cu))/2e6},'native_plane_holes':hole_rows})
 for f in g.b.GetFootprints():
  for l in[p.F_CrtYd,p.B_CrtYd]:
   sh=g.shape(t,p.F_Cu);sh.BooleanIntersection(f.GetCourtyard(l))
   if sh.Area()>1:courtyards.append({'via':u,'ref':f.GetReference(),'courtyard_layer':g.b.GetLayerName(l),'area_mm2':sh.Area()/1e12})
req(len(via_rows)==4,'4 actual new vias')
lengths={}
for net in ['CAM_ISO_OE_N','CAM_IO_EN','IO_ENABLE_LINK','SENS_EXTCLK']:
 tr=[t for t in ts.values()if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)];v=[t for t in ts.values()if t.GetNetname()==net and isinstance(t,p.PCB_VIA)];lengths[net]={'planar_length_mm':sum(t.GetLength()/1e6 for t in tr),'segments':len(tr),'vias':len(v),'segments_under_0_1mm':sum(t.GetLength()<100000 for t in tr)}
provider=R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c'
print(json.dumps({'status':'ACTUAL_NATIVE_PHYSICAL_AND_HOLE_REPORT_NO_SI_APPROVAL','pcb_sha':hashlib.sha256(g.S.read_bytes()).hexdigest(),'finite_geometry_errors':errors,'new_vias_all_layers_and_same_net_pads_checked':4,'new_vias':via_rows,'courtyard_overlaps_open_DFM_gate':courtyards,'actual_native_lengths':lengths,'firmware_provider':{'sha256':hashlib.sha256(provider.read_bytes()).hexdigest(),'returns_NULL':'return 0;'in provider.read_text()},'limits':['Nearest ground via is geometric information only; not a certified high-frequency return path or timing/EMI result','Actual holes are native normalized contours; merged holes explicitly listed instead of ideal isolated circles','JP201/JP202/JP301 remain OPEN; source GPIO42 gate logic does not mean firmware implementation','No PCB fabrication, charging, camera power or functionality release']},indent=2))
