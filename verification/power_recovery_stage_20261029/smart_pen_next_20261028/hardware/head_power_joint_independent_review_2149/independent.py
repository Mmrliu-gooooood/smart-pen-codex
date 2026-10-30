from pathlib import Path
import os,json,hashlib,collections
os.environ['XDG_CONFIG_HOME']='/tmp/headpower-review2149'
import pcbnew as p
from finite_copper import build,components,L
D=Path(__file__).resolve().parent;R=D.parents[1];F=D/'native/mainboard_revD.kicad_pcb'
def req(v,m):
 if not v:raise RuntimeError(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
req(sha(F)=='7e639fa62f08ba04dd5507f383e38ce1134877c5108e2527b855eb9b00b39115','SHA')
b=p.LoadBoard(str(F));base=p.LoadBoard(str(R/'hardware/complete_net_restore_candidate_2014/native/mainboard_revD.kicad_pcb'));old=p.LoadBoard(str(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))
nodes=build(b);whole=[];chains=[];neg=[]
restored=json.loads((R/'hardware/complete_net_restore_candidate_2014/restoration.json').read_text())['restored_nets']
for n in sorted(restored):
 pads=sorted(x[0]for x in nodes[n]if x[1]);cc=components(nodes[n]);req(cc==[pads],'WHOLE '+n);whole.append(dict(net=n,pads=pads))
rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows']
pairs=[(x['net'],x['translator_pin'],'J202.'+x['J202_pin'])for x in rows]+[('CAM_3V3_SW','JP301.2','J301.1'),('GND','J106.3','J301.2')]
for net,a,z in pairs:
 ns=nodes[net];cc=components(ns);req(any(a in c and z in c for c in cc),'PAIR '+net)
 # Choose a cut independently in reverse UUID order rather than author's selected object.
 cut=None
 for name,isp,_ in sorted(ns,reverse=True,key=lambda x:x[0]):
  if isp:continue
  bad=components([x for x in ns if x[0]!=name])
  if not any(a in c and z in c for c in bad):cut=name;break
 req(cut is not None,'NO CUT '+net);neg.append(dict(net=net,start=a,end=z,uuid=cut));chains.append(dict(net=net,components=cc,start=a,end=z))
uid=lambda x:x.m_Uuid.AsString()
def sig(t):return(t.GetClass(),t.GetNetname(),t.GetLayerSet().FmtHex(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
a={uid(x):sig(x)for x in base.GetTracks()};c={uid(x):sig(x)for x in b.GetTracks()};o={uid(x):sig(x)for x in old.GetTracks()};kept=a.keys()&c.keys();removed=a.keys()-c.keys();added=c.keys()-a.keys()
req(len(kept)==392 and len(removed)==76 and len(added)==141 and len(c)==533,'COPPER SET');req(all(c[x]==a[x]for x in kept),'KEEP');req(all(a[x][1].startswith('SENS_')for x in removed),'REMOVED NET');swold=[x for x in added if x in o];req(len(swold)==47 and all(c[x]==o[x]and c[x][1]=='CAM_3V3_SW'for x in swold),'SW47')
for net,core in [('3V3_AON','J106.2'),('GND','J106.3')]:
 cc=components(nodes[net]);req(len(cc)>1,'FALSE FULL POWER '+net)
req(not any('JP301.1'in x and 'JP301.2'in x for x in components(nodes['CAM_3V3_SW'])),'JP BRIDGE')
pad_table=[]
for f in b.GetFootprints():
 for q in f.Pads():pad_table.append(dict(ref=f.GetReference(),pin=q.GetNumber(),net=q.GetNetname(),uuid=uid(q),layers=[b.GetLayerName(l)for l in L if q.IsOnLayer(l)],footprint_side=b.GetLayerName(f.GetLayer())))
req(len(pad_table)==366,'PAD COUNT');fill=[]
for q in b.Zones():
 if q.GetIsRuleArea():continue
 for l in L:
  if q.IsOnLayer(l)and q.GetFilledPolysList(l).OutlineCount():fill.append([q.GetNetname(),b.GetLayerName(l)])
req(not fill,'UNEXPECTED FILL')
dr=json.loads((D/'fresh_drc.json').read_text());counts=[len(dr[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[4,232,0],'FRESH DRC');req(collections.Counter(x['type']for x in dr['violations'])=={'via_dangling':2,'track_dangling':2},'VIOLATIONS');req(int((D/'fresh_drc.exit').read_text())==5,'EXIT')
out=dict(status='PARTIAL_HEAD_CHAINS_ONLY_NOFAB',whole_nets=whole,chains=chains,independently_chosen_cut_negatives=neg,counts=counts,kept392=True,removed76=True,added141=True,old_sw47_exact=True,planes_empty=True,actual_pad_layers=pad_table)
(D/'independent_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='actual_pad_layers'},indent=2))
