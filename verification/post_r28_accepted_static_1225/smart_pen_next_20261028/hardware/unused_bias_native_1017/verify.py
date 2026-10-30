from pathlib import Path
import os,sys,json,hashlib,xml.etree.ElementTree as ET
os.environ.update(XDG_CONFIG_HOME='/tmp/unusedverify/config',XDG_CACHE_HOME='/tmp/unusedverify/cache',XDG_DATA_HOME='/tmp/unusedverify/data')
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];A=D.parent/'ground_pair_native_1007/native';B=D/'native';a=p.LoadBoard(str(A/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());model=json.loads((D/'selected_final.json').read_text());uid=lambda q:q.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,s):
 if not c:raise RuntimeError(s)
def ts(t):return[t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};req(set(bt)-set(at)==set(m['added'])and not set(at)-set(bt),'exact object additions');req(all(ts(t)==ts(bt[u])for u,t in at.items()),'all old copper unchanged');req(len(m['added'])==15,'15 additions');req(sum(isinstance(bt[u],p.PCB_VIA)for u in m['added'])==1,'one via')
for u in m['added']:req(bt[u].GetNetname()in model['targets'],'new two-input nets only')
af={f.GetReference():f for f in a.GetFootprints()};bf={f.GetReference():f for f in b.GetFootprints()};req(set(af)==set(bf),'footprints')
for ref,f in af.items():
 z=bf[ref];req(z.GetPosition()==f.GetPosition()and f.GetValue()==z.GetValue()and f.GetOrientationDegrees()==z.GetOrientationDegrees()and f.GetLayer()==z.GetLayer()and f.GetFPIDAsString()==z.GetFPIDAsString(),'unchanged FP '+ref);aa={uid(q):q for q in f.Pads()};bb={uid(q):q for q in z.Pads()};req(set(aa)==set(bb),'same pads')
 for u,q in aa.items():
  v=bb[u];req(q.GetNetname()==v.GetNetname()and v.GetPosition()==q.GetPosition()and q.GetSize()==v.GetSize()and q.GetOrientationDegrees()==v.GetOrientationDegrees()and q.GetLayerSet().FmtHex()==v.GetLayerSet().FmtHex(),'same physical pad '+ref)
for src in A.rglob('*'):
 if src.is_file()and src.suffix!='.kicad_pcb':req(src.read_bytes()==(B/src.relative_to(A)).read_bytes(),'same native source '+str(src))
outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);bb=outline.BBox();bounds=[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6];req(bounds==[0,-6.5,14,93.3],'actual99.8 outline')
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components,shape
from native_polygon import native_fractured_once
an=build(a);bn=build(b);graph={}
for n,nd in an.items():
 before=components(nd);after=components(bn[n]);expected=[sorted(model['targets'][n])]if n in model['targets']else before;req(after==expected,'exact physical components '+n);graph[n]={'before':before,'after':after}
core={n:next(c for c in components(bn[n])if anchor in c)for n,anchor in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};req([len(core[n])for n in ['GND','3V3_AON','SENS_VIO_1V8']]==[94,41,12],'all supply cores unchanged');req({'R206.2','R207.2'}<=set(core['GND']),'both pulldown ground terminals core')
# Frozen source function/direction inventory; NC outputs must remain copper-free.
xml=ET.parse(D/'checks/candidate/netlist.xml').getroot();pinmap={(node.get('ref')+'.'+node.get('pin')):{'net':net.get('name'),'function':node.get('pinfunction')}for net in xml.findall('./nets/net')for node in net.findall('node')}
expected={'U202.10':('UNUSED_B_INPUT','2B2'),'U203.7':('UNUSED_A_INPUT','2A2'),'U202.3':('GND','2DIR'),'U203.3':('3V3_AON','2DIR'),'U202.7':('unconnected-(U202-2A2-Pad7)','2A2'),'U203.10':('unconnected-(U203-2B2-Pad10)','2B2')}
for pin,(net,fn)in expected.items():req(pinmap[pin]=={'net':net,'function':fn},'source function '+pin)
for ref in ['R206','R207']:req(bf[ref].GetValue()=='10k 1%','existing bias value')
for pin in ['U202.7','U203.10']:
 net=pinmap[pin]['net'];req(components(bn[net])==[[pin]]and not any(t.GetNetname()==net for t in b.GetTracks()),'NC output untouched '+pin)
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
pa,pb=planes(a),planes(b);loss=[];refs={p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]};projection_count=0
# ALL retained nets, including power and GND, not signal-only exemption.
for u,t in at.items():
 if isinstance(t,p.PCB_VIA):continue
 for ref in refs.get(t.GetLayer(),[]):
  projection_count+=1;s=shape(t,t.GetLayer());x=p.SHAPE_POLY_SET();x.BooleanIntersection(s,pa[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(s,pb[ref]);x.BooleanSubtract(y)
  if x.Area()/1e12>1e-8:loss.append({'uuid':u,'net':t.GetNetname(),'reference':b.GetLayerName(ref),'loss_mm2':x.Area()/1e12})
newrefs=[]
for net in model['targets']:
 for layer,rl in refs.items():
  sh=p.SHAPE_POLY_SET()
  for u in m['added']:
   t=bt[u]
   if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)and t.GetLayer()==layer:sh.BooleanAdd(shape(t,layer))
  if not sh.OutlineCount():continue
  for ref in rl:
   q=p.SHAPE_POLY_SET();q.BooleanSubtract(sh,pb[ref]);newrefs.append({'net':net,'layer':b.GetLayerName(layer),'reference':b.GetLayerName(ref),'total_projection_mm2':sh.Area()/1e12,'uncovered_mm2':q.Area()/1e12})
(D/'reference_diagnostic.json').write_text(json.dumps({'all_retained_net_projection_count':projection_count,'added_loss':loss,'new_input_net_reference_unions':newrefs},indent=2)+'\n');req(not loss,'zero additional old ALL-NET reference loss')
for stem,expectedcounts in [('base',[0,73,0]),('candidate',[0,71,0])]:
 dr=json.loads((D/f'checks/{stem}/drc.json').read_text());req([len(dr[k])for k in ['violations','unconnected_items','schematic_parity']]==expectedcounts,'real DRC '+stem)
e=json.loads((D/'checks/candidate/erc.json').read_text());ev=[v for s in e['sheets']for v in s['violations']];req([(v['severity'],v['type'])for v in ev]==[('warning','global_label_dangling')],'ERC')
lengths={}
for net in model['targets']:
 tr=[bt[u]for u in m['added']if bt[u].GetNetname()==net and not isinstance(bt[u],p.PCB_VIA)];lengths[net]={'tracks':len(tr),'vias':sum(bt[u].GetNetname()==net and isinstance(bt[u],p.PCB_VIA)for u in m['added']),'total_planar_length_mm':sum(t.GetLength()/1e6 for t in tr),'short_segments_under_0_1mm':[uid(t)for t in tr if t.GetLength()<100000]}
print(json.dumps({'status':'UNUSED_INPUT_BIAS_ROUTING_ONLY_NOFAB_NOPOWER','pcb_sha256':sha(B/'mainboard_revD.kicad_pcb'),'parent_sha256':sha(A/'mainboard_revD.kicad_pcb'),'outline_bounds_mm':bounds,'DRC_unconnected_parity':[0,71,0],'all_nets_physical_components':graph,'core':core,'source_pin_roles':{pin:pinmap[pin]for pin in expected},'all_retained_net_reference_projection_count':projection_count,'all_retained_net_additional_reference_loss':loss,'new_input_net_reference_unions':newrefs,'new_net_lengths':lengths,'new_copper_objects':len(m['added']),'limits':['Routing fixed existing10k pulldowns, not transistor leakage or input-level verification','2DIR grounded/AON topology retained; actual powered/isolated/brownout behavior unqualified','New bias lengths/coupling/process require review; no sensor attached or NC output connected','All camera/FPC/power/dynamicOE/VOH/clock/firmware/battery/thermal/process gates remain']},indent=2))
