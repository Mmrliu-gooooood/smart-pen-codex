from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/translator-verify0130'
import pcbnew as p
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/mcu_power_ground_clearance_0109/native/mainboard_revD.kicad_pcb';F=Path(os.environ.get('TRANSLATOR_VERIFY_PCB',str(D/'native/mainboard_revD.kicad_pcb')));m=json.loads((D/'materialization.json').read_text());plan=json.loads((D/'plan_v2.json').read_text());a=p.LoadBoard(str(B));b=p.LoadBoard(str(F));uid=lambda x:x.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,msg):
 if not c:raise RuntimeError(msg)
def ts(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};req(set(at)-set(bt)==set(m['removed']),'removed exact');req(set(bt)-set(at)==set(m['added']),'added exact');req(all(ts(t)==ts(bt[u])for u,t in at.items()if u not in m['removed']),'retained objects');req(len(bt)==736,'new total')
af={f.GetReference():f for f in a.GetFootprints()};bf={f.GetReference():f for f in b.GetFootprints()};req(set(af)==set(bf),'refs');poses=[]
for ref,f in af.items():
 g=bf[ref];req(f.GetValue()==g.GetValue()and str(f.GetFPID().GetLibItemName())==str(g.GetFPID().GetLibItemName())and f.GetOrientationDegrees()==g.GetOrientationDegrees()and f.GetLayer()==g.GetLayer(),'FP contract')
 changed=f.GetPosition()!=g.GetPosition();req(changed==(ref in ['C207','C208']),'only two poses')
 if changed:poses.append(dict(ref=ref,before=[f.GetPosition().x/1e6,f.GetPosition().y/1e6],after=[g.GetPosition().x/1e6,g.GetPosition().y/1e6]))
 aa={uid(q):q for q in f.Pads()};bb={uid(q):q for q in g.Pads()};req(set(aa)==set(bb),'pad UUIDs')
 for u,q in aa.items():
  z=bb[u];req(q.GetNetname()==z.GetNetname()and q.GetNumber()==z.GetNumber()and q.GetLayerSet().FmtHex()==z.GetLayerSet().FmtHex()and q.GetSize()==z.GetSize()and q.GetOrientationDegrees()==z.GetOrientationDegrees(),'pad source/layer')
  if not changed:req(q.GetPosition()==z.GetPosition(),'otherpadposition')
for ext in ['kicad_pro','kicad_dru','kicad_sch']:
 req((B.parent/('mainboard_revD.'+ext)).read_bytes()==(F.parent/('mainboard_revD.'+ext)).read_bytes(),'source/rules '+ext)
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
# Local cap-to-supply and grounds, irrespective of external SENS readiness.
pairs=[('3V3_AON','U201.1','C201.1'),('SENS_VIO_1V8','U201.24','C202.1'),('SENS_VIO_1V8','U201.23','C202.1'),('3V3_AON','U202.1','C203.1'),('SENS_VIO_1V8','U202.16','C204.1'),('3V3_AON','U203.1','C205.1'),('SENS_VIO_1V8','U203.16','C206.1'),('3V3_AON','U204.8','C207.1'),('SENS_VIO_1V8','U204.1','C208.1')]
for n,st,en in pairs:req(en in reach(bn[n],st),'localpair '+st)
required_gnd=['U201.2','U201.11','U201.12','U201.13','U202.2','U202.3','U202.8','U202.9','U203.8','U203.9','U204.4']+['C20'+str(i)+'.2'for i in range(1,9)]
req(set(required_gnd)<=set(core['GND']['after']),'local GND core')
req({'U201.1','U202.1','U203.1','U203.2','U203.3','U204.8','C201.1','C203.1','C205.1','C207.1'}<=set(core['3V3_AON']['after']),'local AONcore')
req(len(core['SENS_VIO_1V8']['after'])==1,'do not claim SENS input complete')
# Whole-domain deletion is a negative causal check, local independently powered branches are not conflated.
neg=[]
for n in ['3V3_AON','GND','SENS_VIO_1V8']:
 rem={u for u in m['added']if bt[u].GetNetname()==n};st='J106.2'if n=='3V3_AON'else'J106.3'if n=='GND'else'U204.1';y=reach(bn[n],st,rem)
 expected=['U201.1','U202.1','U203.1','U204.8']if n=='3V3_AON'else['U201.12','U201.13','U202.8','U202.9','U203.8','U203.9','U204.4']if n=='GND'else['C208.1'];req(not set(expected)&y,'negative '+n);neg.append(dict(net=n,removed=len(rem),expected_disconnected=expected))
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
for u,t in at.items():
 if u in m['removed']or isinstance(t,p.PCB_VIA)or t.GetNetname()in['GND','3V3_AON','CAM_3V3_SW']:continue
 ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;x=p.SHAPE_POLY_SET();x.BooleanIntersection(shape(t,t.GetLayer()),ga[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(shape(t,t.GetLayer()),gb[ref]);x.BooleanSubtract(y)
 if x.Area()/1e12>1e-8:proj.append(dict(uuid=u,net=t.GetNetname(),loss_mm2=x.Area()/1e12))
req(not proj,'old signal reference newly lost')
drc=json.loads((D/'drc.json').read_text());counts=[len(drc[k])for k in['violations','unconnected_items','schematic_parity']];req(counts==[0,149,0],'counts')
print(json.dumps(dict(status='NOFAB_LOCAL_DOMAINS_ONLY_NOT_SENSOR_INPUT_OR_COMPLETE_POWER',pcb_sha=sha(F),base_sha=sha(B),native_DRC=counts,objects=len(bt),removed=m['removed'],added=len(m['added']),preserved_copper=len(at)-len(m['removed']),poses=poses,all_prior_pad_components_preserved=prior,core=core,local_supply_cap_pairs=pairs,negative=neg,new_vias=via_count,new_via_all_pad_overlap=via_overlaps,plane_delta=planes,old_signal_additional_reference_losses=proj,limits=['SENS external J202.23 remains isolated; local SENS cap ties are NOT powered rail qualification','Local0.3/.254 trace widths are design choices, no vendor width/current rating is claimed','Unchanged MCU EP via fabrication limits still apply','Nominal via-pad nonoverlap does not establish solder-mask/assembly/thermal tolerance','TCA cap placement improved but current loops/decoupling frequency performance not measured']),indent=2))
