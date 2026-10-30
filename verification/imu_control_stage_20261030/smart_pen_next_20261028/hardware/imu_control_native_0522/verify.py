from pathlib import Path
import os,json,hashlib,math,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"translator_domain_candidate_0130"))
os.environ['XDG_CONFIG_HOME']='/tmp/sens-verify0158'
import pcbnew as p
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/pressure_joint_native_0433/native/mainboard_revD.kicad_pcb';F=Path(os.environ.get('TRANSLATOR_VERIFY_PCB',str(D/'native/mainboard_revD.kicad_pcb')));m=json.loads((D/'materialization.json').read_text());a=p.LoadBoard(str(B));b=p.LoadBoard(str(F));uid=lambda x:x.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,msg):
 if not c:raise RuntimeError(msg)
def ts(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};req(set(at)-set(bt)==set(m['removed']),'removed exact');req(set(bt)-set(at)==set(m['added']),'added exact');req(all(ts(t)==ts(bt[u])for u,t in at.items()if u not in m['removed']),'retained objects');req(len(bt)==983,'new total')
af={f.GetReference():f for f in a.GetFootprints()};bf={f.GetReference():f for f in b.GetFootprints()};req(set(af)==set(bf),'refs');poses=[]
for ref,f in af.items():
 g=bf[ref];req(f.GetValue()==g.GetValue()and str(f.GetFPID().GetLibItemName())==str(g.GetFPID().GetLibItemName())and f.GetOrientationDegrees()==g.GetOrientationDegrees()and f.GetLayer()==g.GetLayer(),'FP contract')
 changed=f.GetPosition()!=g.GetPosition();req(not changed,'no poses changed'); expected={'J107':(5.2,84)}
 if changed:req((g.GetPosition().x/1e6,g.GetPosition().y/1e6)==expected[ref],'exact moved pose')
 if changed:poses.append(dict(ref=ref,before=[f.GetPosition().x/1e6,f.GetPosition().y/1e6],after=[g.GetPosition().x/1e6,g.GetPosition().y/1e6]))
 aa={uid(q):q for q in f.Pads()};bb={uid(q):q for q in g.Pads()};req(set(aa)==set(bb),'pad UUIDs')
 for u,q in aa.items():
  z=bb[u];req(q.GetNetname()==z.GetNetname()and q.GetNumber()==z.GetNumber()and q.GetLayerSet().FmtHex()==z.GetLayerSet().FmtHex()and q.GetSize()==z.GetSize()and q.GetOrientationDegrees()==z.GetOrientationDegrees(),'pad source/layer')
  if not changed:req(q.GetPosition()==z.GetPosition(),'otherpadposition')
for ext in ['kicad_pro','kicad_dru','kicad_sch']:
 req((B.parent/('mainboard_revD.'+ext)).read_bytes()==(F.parent/('mainboard_revD.'+ext)).read_bytes(),'source/rules '+ext)
import xml.etree.ElementTree as ET
xml=ET.parse(D/'checks/candidate/netlist.xml');nib=next(n for n in xml.findall('.//nets/net')if n.get('name')=='NIB_CONTACT_N')
req(any(n.get('ref')=='U101'and n.get('pin')=='7'and n.get('pinfunction')=='GPIO2'for n in nib.findall('node')),'actual source GPIO2')
req(bf['R503'].GetValue()=='47k 1%'and bf['R503'].GetFieldByName('MPN').GetText()=='RC0603FR-0747KL','source R50347kMPN')
e=json.loads((D/'checks/candidate/erc.json').read_text());ev=[x for sh in e['sheets']for x in sh['violations']];req([(v['severity'],v['type'])for v in ev]==[('warning','global_label_dangling')],'ERC0error1existingwarning')
an=build(a);bn=build(b)
def reach(nodes,start,omit=set()):
 nodes=[n for n in nodes if n[0]not in omit];lookup={n[0]:n for n in nodes};req(start in lookup,'start');seen={start};todo=[start]
 while todo:
  _,_,x=lookup[todo.pop()]
  for name,_,y in nodes:
   if name in seen:continue
   for l in x.keys()&y.keys():
    if not x[l].BBox().Intersects(y[l].BBox()):continue
    z=p.SHAPE_POLY_SET();z.BooleanIntersection(x[l],y[l])
    if z.Area()>1:seen.add(name);todo.append(name);break
 return seen
prior={}
for n,ns in an.items():
 before=components(ns);after=components(bn[n]);req(all(any(set(c)<=set(d)for d in after)for c in before),'prior pad component '+n);prior[n]=[len(before),len(after)]
core={}
for n,st in [('3V3_AON','J106.2'),('GND','J106.3'),('SENS_VIO_1V8','J202.23')]:
 x=reach(an[n],st);y=reach(bn[n],st);bp=sorted(z for z,isp,_ in an[n]if isp and z in x);ap=sorted(z for z,isp,_ in bn[n]if isp and z in y);req(set(bp)<=set(ap),'core pad lost');core[n]=dict(before=bp,after=ap,total=sum(isp for _,isp,_ in bn[n]));
pairs=[];neg=[]
req([len(core[n]['before'])for n in ['3V3_AON','GND','SENS_VIO_1V8']]==[36,70,12],'base core counts')
req([len(core[n]['after'])for n in ['3V3_AON','GND','SENS_VIO_1V8']]==[38,70,12],'new core counts')
req({'R501.1','R502.1','R503.1'}<=set(core['3V3_AON']['after']),'pressure and two IMU pullup AON')
req({'C504.2','J103.2'}<=set(core['GND']['after']),'pressure ground')
req(components(bn['NIB_CONTACT_N'])==[['C504.1','R503.2','R504.1','U101.7']],'pressure signal all four')
req(components(bn['CONTACT'])==[['J103.1','R504.2']],'contact two')
req(components(bn['STRAP_GPIO3'])==[['R103.1','U101.8']],'strap complete')
req('J202.18'in reach(bn['SENS_EXTCLK'],'U203.13'),'clock full retained')
# All three control nets include physical MCU/IMU/pullup endpoints.
for net,expected in {'AON_I2C_SCL':['R501.2','U101.10','U501.1'],'AON_I2C_SDA':['R502.2','U101.11','U501.4'],'PICKUP_INT_N':['U101.6','U501.12']}.items():req(components(bn[net])==[sorted(expected)],'complete control '+net)
req(len(m['added'])==137 and len(m['removed'])==3,'exact model object counts')
for row in m['mapping']:
 t=bt[row['uuid']];req(t.GetNetname()==row['net'],'new net')
 req(t.GetStart()==p.VECTOR2I(*(round(v*1e6)for v in row['a']))and t.GetEnd()==p.VECTOR2I(*(round(v*1e6)for v in row['b'])),'exact proposed coordinate')
 req((t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())==round(row['width']*1e6),'exact proposed width')
 if isinstance(t,p.PCB_VIA):req(t.GetDrillValue()==round(row['drill']*1e6),'exact drill')
 else:req(b.GetLayerName(t.GetLayer())==row['layer'],'exact layer')
# Entire source tree and project resources remain byte-identical, not merely root schematic.
for src in B.parent.rglob('*'):
 if src.is_file()and src.suffix!='.kicad_pcb':req(src.read_bytes()==(F.parent/src.relative_to(B.parent)).read_bytes(),'source tree '+str(src))
# Every new through annulus must avoid ALL physical pad copper on ALL actual layers, even same-net.
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
    if v.Area()>1:via_overlaps.append(dict(via=u,pad=f.GetReference()+'.'+q.GetNumber(),net=q.GetNetname(),layer=b.GetLayerName(l)))
req(not via_overlaps,'new via overlaps any physical pad')
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
# Actual reference changes are reported, never silently waived as timing qualified.
drc=json.loads((D/'checks/candidate/drc.json').read_text());counts=[len(drc[k])for k in['violations','unconnected_items','schematic_parity']];req(counts[0]==0 and counts[2]==0 and counts[1]==106,'counts')
print(json.dumps(dict(status='NOFAB_NOPOWER_IMU_CONTROL_NATIVE_CANDIDATE',pcb_sha=sha(F),base_sha=sha(B),native_DRC=counts,objects=len(bt),removed=m['removed'],added=len(m['added']),preserved_copper=len(at)-len(m['removed']),poses=poses,all_prior_pad_components_preserved=prior,core=core,local_supply_cap_pairs=pairs,negative=neg,new_vias=via_count,new_via_all_pad_overlap=via_overlaps,plane_delta=planes,old_signal_additional_reference_losses=proj,limits=['Actual IRQ source defaults active HIGH/nonlatched; net suffix does not configure it; firmware provider absent, no wake function claimed','Native control routing has53sub0.1mmsegments; no production elegance/DFM qualification','Pressure source remains conditional 47k/1k/1n; AON>=3V and contact force/life, debounce, ESD and firmware GPIO2 wake unqualified','R504 is connector-local, not MCU-local; NIB planar copper length 53.27mm requires noise/parasitic validation','J103 GND via under U203 PW body: assembly tenting and process DFM unresolved; no exposed-pad or via-in-pad waiver','Unchanged MCU EP via and IMU mechanical/clock/J107 and camera/charging fabrication gates apply; JP301 OPEN','Native B52 versus virtual B70.5 mechanical placement remains unresolved']),indent=2))
