from pathlib import Path
import os,json,hashlib,sys
os.environ['XDG_CONFIG_HOME']='/tmp/schmittverify0745'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'))
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
B=R/'hardware/camera_isolation_control_native_0628/native/mainboard_revD.kicad_pcb';F=D/'native/mainboard_revD.kicad_pcb';m=json.loads((D/'materialization.json').read_text());a=p.LoadBoard(str(B));b=p.LoadBoard(str(F));uid=lambda x:x.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,msg):
 if not c:raise RuntimeError(msg)
def ts(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};req(set(at)-set(bt)==set(m['removed']),'exact removals');req(set(bt)-set(at)==set(m['added']),'exact additions');req(all(ts(t)==ts(bt[u])for u,t in at.items()if u not in m['removed']),'unchanged old copper');req(len(m['removed'])==6 and len(m['added'])==15,'bounded copper delta')
af={f.GetReference():f for f in a.GetFootprints()};bf={f.GetReference():f for f in b.GetFootprints()};req(set(af)-set(bf)=={'Q201'}and set(bf)-set(af)=={'U205','C209'},'exact footprint delta')
for ref,f in af.items():
 if ref=='Q201':continue
 z=bf[ref];req(f.GetValue()==z.GetValue()if ref!='R202'else z.GetValue()=='10k 1%','value '+ref)
 req(f.GetPosition()==z.GetPosition()and f.GetOrientationDegrees()==z.GetOrientationDegrees()and f.GetLayer()==z.GetLayer()and f.GetFPIDAsString()==z.GetFPIDAsString(),'all retained footprint poses/source')
 aa={uid(q):q for q in f.Pads()};bb={uid(q):q for q in z.Pads()};req(set(aa)==set(bb),'pad UUID')
 for u,q in aa.items():
  v=bb[u];req(q.GetNetname()==v.GetNetname()and q.GetPosition()==v.GetPosition()and q.GetSize()==v.GetSize()and q.GetOrientationDegrees()==v.GetOrientationDegrees()and q.GetLayerSet().FmtHex()==v.GetLayerSet().FmtHex(),'retained pad')
for ext in ['kicad_pro','kicad_dru']:req((B.parent/('mainboard_revD.'+ext)).read_bytes()==(F.parent/('mainboard_revD.'+ext)).read_bytes(),'rules unchanged')
S=R/'hardware/camera_schmitt_source_0744/native'
for src in S.rglob('*'):
 if src.is_file():req(src.read_bytes()==(F.parent/src.relative_to(S)).read_bytes(),'source exactly frozen '+str(src))
for ref in ['JP201','JP202','JP301']:req(bf[ref].GetValue()=={'JP201':'DNP_IO_COMMISSION','JP202':'DNP_SCCB_COMMISSION','JP301':'OPEN / DO NOT BRIDGE'}[ref],'commissioning OPEN')
req(bf['R503'].GetValue()=='47k 1%'and bf['R503'].GetFieldByName('MPN').GetText()=='RC0603FR-0747KL','pressure source preserved')
req(bf['U205'].GetFPIDAsString()=='SmartPenIO:TI_DCK0005A_Schmitt_OfficialLand','official land')
for q in bf['U205'].Pads():req(q.GetSize()==p.VECTOR2I(950000,400000),'official pad size')
for ref in ['U205','C209']:
 h=json.loads((S.parent/'handoff.json').read_text())[ref];req(bf[ref].GetPath().AsString()==h['path'],'source UUID path')
# Complete physical components, with replacement functional pins mapped explicitly.
an=build(a);bn=build(b);mapping={'Q201.1':'U205.2','Q201.2':'U205.3','Q201.3':'U205.4'};prior={}
for net,nodes in an.items():
 before=components(nodes);after=components(bn[net]);req(all(any({mapping.get(x,x)for x in c}<=set(d)for d in after)for c in before),'prior component lost '+net);prior[net]=[len(before),len(after)]
core={}
for net,start in [('3V3_AON','J106.2'),('GND','J106.3'),('SENS_VIO_1V8','J202.23')]:
 before=next(c for c in components(an[net])if start in c);after=next(c for c in components(bn[net])if start in c);core[net]={'before':before,'after':after,'total_pads':sum(isp for _,isp,_ in bn[net])}
req([len(core[n]['after'])for n in ['3V3_AON','GND','SENS_VIO_1V8']]==[41,71,12],'core counts')
expected={'CAM_ISO_OE_N':['U205.4','R203.1','U201.22','U202.14','U202.15','U203.14','U203.15'],'ISO_GATE':['U205.2','R201.2','R202.1'],'CAM_IO_EN':['JP201.1','R107.1','U101.48'],'IO_ENABLE_LINK':['JP201.2','R201.1'],'NIB_CONTACT_N':['C504.1','R503.2','R504.1','U101.7'],'CONTACT':['J103.1','R504.2'],'STRAP_GPIO3':['R103.1','U101.8'],'AON_I2C_SCL':['R501.2','U101.10','U501.1'],'AON_I2C_SDA':['R502.2','U101.11','U501.4'],'PICKUP_INT_N':['U101.6','U501.12'],'unconnected-(U205-NC-Pad1)':['U205.1']}
for net,pins in expected.items():req(components(bn[net])==[sorted(pins)],'complete '+net)
req('J202.18'in next(c for c in components(bn['SENS_EXTCLK'])if'U203.13'in c),'full clock preserved')
req({'C209.1','U205.5'}<=set(core['3V3_AON']['after']),'new supply');req({'C209.2','U205.3'}<=set(core['GND']['after']),'new ground')
req(not any(t.GetNetname()=='unconnected-(U205-NC-Pad1)'for t in b.GetTracks()),'NC no copper')
# All actual new vias versus every pad/layer, INCLUDING SAME NET.
via_overlaps=[];via_count=0
for u in m['added']:
 t=bt[u]
 if not isinstance(t,p.PCB_VIA):continue
 via_count+=1
 for f in b.GetFootprints():
  for q in f.Pads():
   for l in L:
    if not q.IsOnLayer(l):continue
    v=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(v,l,0,50,p.ERROR_OUTSIDE);v.BooleanIntersection(shape(q,l))
    if v.Area()>1:via_overlaps.append({'via':u,'pad':f.GetReference()+'.'+q.GetNumber(),'layer':b.GetLayerName(l)})
req(via_count==4 and not via_overlaps,'all new through vias avoid all physical pads')
# Refilled reference deltas use guarded one-shot hole decoding, never raw fractured erosion.
za={uid(z):z for z in a.Zones()if not z.GetIsRuleArea()};zb={uid(z):z for z in b.Zones()if not z.GetIsRuleArea()};planes=[];ga={};gb={}
for u,z in za.items():
 l=z.GetLayer();x=native_fractured_once(z.GetFilledPolysList(l));y=native_fractured_once(zb[u].GetFilledPolysList(l));lo=p.SHAPE_POLY_SET();lo.BooleanSubtract(x,y);ad=p.SHAPE_POLY_SET();ad.BooleanSubtract(y,x);ye=p.SHAPE_POLY_SET(y);ye.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 planes.append(dict(uuid=u,net=z.GetNetname(),layer=b.GetLayerName(l),removed_mm2=lo.Area()/1e12,added_mm2=ad.Area()/1e12,normalized_025_eroded_components=ye.OutlineCount(),actual_holes=sum(y.HoleCount(i)for i in range(y.OutlineCount()))))
 if z.GetNetname()=='GND':ga.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(x);gb.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(y)
proj=[]
# All actual old signal reference associations, including inner signals.
allza={};allzb={}
for u,z in za.items():
 l=z.GetLayer();allza.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(l)));allzb.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(zb[u].GetFilledPolysList(l)))
for u,t in at.items():
 if u in m['removed'] or isinstance(t,p.PCB_VIA) or t.GetNetname() in ['GND','3V3_AON','SENS_VIO_1V8']:continue
 refs={p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}.get(t.GetLayer(),[])
 for ref in refs:
  x=p.SHAPE_POLY_SET();x.BooleanIntersection(shape(t,t.GetLayer()),allza[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(shape(t,t.GetLayer()),allzb[ref]);x.BooleanSubtract(y)
  if x.Area()/1e12>1e-8:proj.append(dict(uuid=u,net=t.GetNetname(),reference_layer=b.GetLayerName(ref),loss_mm2=x.Area()/1e12))
e=json.loads((D/'checks/candidate/erc.json').read_text());ev=[x for sh in e['sheets']for x in sh['violations']];req([(v['severity'],v['type'])for v in ev]==[('warning','global_label_dangling')],'ERC unchanged')
drc=json.loads((D/'checks/candidate/drc.json').read_text());counts=[len(drc[k])for k in['violations','unconnected_items','schematic_parity']];req(counts==[0,96,0],'real CLI')
print(json.dumps({'status':'STABLE_AON_EXPERIMENT_ONLY_NOFAB_NOPOWER','pcb_sha256':sha(F),'base_sha256':sha(B),'actual_DRC_unconnected_parity':counts,'all_retained_footprints_poses_and_pads_unchanged':True,'all_prior_components_preserved_with_explicit_Q_to_U_mapping':prior,'functional_pin_mapping':mapping,'core':core,'new_vias_all_layers_same_net_pad_overlap':via_overlaps,'plane_delta':planes,'old_signal_additional_reference_losses':proj,'copper_objects':len(bt),'new_copper':len(m['added']),'removed_copper':m['removed'],'limits':['Not autonomous safe power-up or power-down; stable AON controlled USB-JTAG experimental mode only','All 0719/0730 dynamic load/timing, leakage/loaded-GPIO VOH, power sequencing, temperature and commissioning gates remain','All 0628 inherited reference losses, merged holes, thermal/EP and mechanics/DFM gates remain; 96 unrouted gaps remain']},indent=2))
