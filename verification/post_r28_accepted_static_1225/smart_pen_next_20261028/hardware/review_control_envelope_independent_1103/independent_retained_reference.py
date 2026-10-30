from pathlib import Path
import os,sys,json,hashlib,xml.etree.ElementTree as ET
os.environ.update(XDG_CONFIG_HOME='/tmp/unusedverify/config',XDG_CACHE_HOME='/tmp/unusedverify/cache',XDG_DATA_HOME='/tmp/unusedverify/data')
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];A=D.parent/'unused_bias_native_1017/native';B=D/'native';a=p.LoadBoard(str(A/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());model=json.loads((D/'selected_final.json').read_text());uid=lambda q:q.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,s):
 if not c:raise RuntimeError(s)
def ts(t):return[t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};req(set(bt)-set(at)==set(m['added'])and not set(at)-set(bt),'exact object additions');req(all(ts(t)==ts(bt[u])for u,t in at.items()),'all old copper unchanged');req(len(m['added'])==20,'20 additions');req(sum(isinstance(bt[u],p.PCB_VIA)for u in m['added'])==2,'two vias')
for u in m['added']:req(bt[u].GetNetname()in model['targets'],'new two-control nets only')
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
 before=components(nd);after=components(bn[n]);expected=sorted([c for c in before if not set(c)&set(model['targets'][n])]+[sorted(model['targets'][n])])if n in model['targets']else before;req(after==expected,'exact physical components '+n);graph[n]={'before':before,'after':after}
core={n:next(c for c in components(bn[n])if anchor in c)for n,anchor in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};req([len(core[n])for n in ['GND','3V3_AON','SENS_VIO_1V8']]==[94,41,12],'all supply cores unchanged');req({'R222.2','R223.2'}<=set(core['GND']),'both pulldown ground terminals core')
req({'U203.2','U203.3'}<=set(core['3V3_AON']),'both actual direction controls in AON core')
# Frozen source control roles; existing other branches remain unchanged.
xml=ET.parse(D/'checks/candidate/netlist.xml').getroot();pinmap={(node.get('ref')+'.'+node.get('pin')):{'net':net.get('name'),'function':node.get('pinfunction')}for net in xml.findall('./nets/net')for node in net.findall('node')}
expected={'U203.5':('CAM_RESET_UART_TX','1A2'),'U203.6':('CAM_PWDN_UART_RX','2A1'),'U203.2':('3V3_AON','1DIR'),'U203.3':('3V3_AON','2DIR')}
for pin,(net,fn)in expected.items():req(pinmap[pin]=={'net':net,'function':fn},'source function '+pin)
for ref in ['R222','R223']:req(bf[ref].GetValue()=='100k 1%','existing bias value')
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
  if x.Area()>0:loss.append({'uuid':u,'net':t.GetNetname(),'reference':b.GetLayerName(ref),'loss_mm2':x.Area()/1e12})

(D/'independent_all_positive_retained_losses.json').write_text(json.dumps({'projection_count':projection_count,'all_positive_loss_regions_including_subthreshold':loss},indent=2)+'\n')
