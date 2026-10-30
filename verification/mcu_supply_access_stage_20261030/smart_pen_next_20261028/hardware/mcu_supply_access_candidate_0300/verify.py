from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/sens-verify0158'
import pcbnew as p
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/gate_power_candidate_0228/native/mainboard_revD.kicad_pcb';F=Path(os.environ.get('TRANSLATOR_VERIFY_PCB',str(D/'native/mainboard_revD.kicad_pcb')));m=json.loads((D/'materialization.json').read_text());a=p.LoadBoard(str(B));b=p.LoadBoard(str(F));uid=lambda x:x.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,msg):
 if not c:raise RuntimeError(msg)
def ts(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};req(set(at)-set(bt)==set(m['removed']),'removed exact');req(set(bt)-set(at)==set(m['added']),'added exact');req(all(ts(t)==ts(bt[u])for u,t in at.items()if u not in m['removed']),'retained objects');req(len(bt)==789,'new total')
af={f.GetReference():f for f in a.GetFootprints()};bf={f.GetReference():f for f in b.GetFootprints()};req(set(af)==set(bf),'refs');poses=[]
for ref,f in af.items():
 g=bf[ref];req(f.GetValue()==g.GetValue()and str(f.GetFPID().GetLibItemName())==str(g.GetFPID().GetLibItemName())and f.GetOrientationDegrees()==g.GetOrientationDegrees()and f.GetLayer()==g.GetLayer(),'FP contract')
 changed=f.GetPosition()!=g.GetPosition();req(changed==(ref in ['C103','R503']),'only two poses'); expected={'C103':(.8,7.025),'R503':(2.5,11.5)}
 if changed:req((g.GetPosition().x/1e6,g.GetPosition().y/1e6)==expected[ref],'exact moved pose')
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
pairs=[('3V3_AON','U101.2','J106.2'),('3V3_AON','U101.3','J106.2'),('3V3_AON','C103.1','J106.2'),('GND','C103.2','J106.3')]
for n,st,en in pairs:req(en in reach(bn[n],st),'localpair '+st)
req([len(core[n]['after'])for n in ['3V3_AON','GND','SENS_VIO_1V8']]==[28,61,12],'core counts')
neg=[]
for net,inds,pads in [('3V3_AON',[0],['U101.2']),('3V3_AON',[1],['U101.3']),('3V3_AON',[5,8],['U101.2','U101.3','C103.1'])]:
 y=reach(bn[net],'J106.2',{m['added'][i]for i in inds});req(all(q not in y for q in pads),'negative');neg.append(dict(removed=inds,disconnected=pads,mode='finite copper omission only; independent native negatives separately'))
y=reach(bn['GND'],'J106.3',{m['added'][6]});req('C103.2' in y,'old ground overlap retained');neg.append(dict(removed=[6],still_connected=['C103.2'],reason='old ground stub overlaps shifted capacitor; new tail redundant'))
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
 if isinstance(t,p.PCB_VIA) or t.GetNetname() in ['GND','3V3_AON','SENS_VIO_1V8']:continue
 refs={p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}.get(t.GetLayer(),[])
 for ref in refs:
  x=p.SHAPE_POLY_SET();x.BooleanIntersection(shape(t,t.GetLayer()),allza[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(shape(t,t.GetLayer()),allzb[ref]);x.BooleanSubtract(y)
  if x.Area()/1e12>1e-8:proj.append(dict(uuid=u,net=t.GetNetname(),reference_layer=b.GetLayerName(ref),loss_mm2=x.Area()/1e12))
req(not proj,'old signal reference newly lost')
drc=json.loads((D/'drc.json').read_text());counts=[len(drc[k])for k in['violations','unconnected_items','schematic_parity']];req(counts==[0,134,0],'counts')
print(json.dumps(dict(status='NOFAB_NOPOWER_RESEARCH_MCU_ACCESS_COURTYARD_AND_SHORT_ESCAPE_UNQUALIFIED',pcb_sha=sha(F),base_sha=sha(B),native_DRC=counts,objects=len(bt),removed=m['removed'],added=len(m['added']),preserved_copper=len(at)-len(m['removed']),poses=poses,all_prior_pad_components_preserved=prior,core=core,local_supply_cap_pairs=pairs,negative=neg,new_vias=via_count,new_via_all_pad_overlap=via_overlaps,plane_delta=planes,old_signal_additional_reference_losses=proj,limits=['SENS physical tree is connected, but external supply/power sequence/back-power unqualified','MCU .25mm short escapes are below generic20mil; package/current qualification unresolved','Unchanged MCU EP via fabrication limits still apply','Nominal via-pad nonoverlap does not establish solder-mask/assembly/thermal tolerance','New vias overlap C103/U101 courtyard; mask/paste/underside/tolerance unresolved, not waived']),indent=2))
