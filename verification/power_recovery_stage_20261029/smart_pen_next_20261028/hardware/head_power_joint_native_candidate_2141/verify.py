from pathlib import Path
import os,json,hashlib,collections
os.environ['XDG_CONFIG_HOME']='/tmp/pen-joint2141-verify'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];N=D/'native';B=R/'hardware/complete_net_restore_candidate_2014/native';b=p.LoadBoard(str(N/'mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));old=p.LoadBoard(str(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());plan=json.loads((R/'docs/electronics/head_power_joint_plan_2129/result.json').read_text());spec=plan['objects'];uid=lambda t:t.m_Uuid.AsString();xy=lambda v:(v.x,v.y);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(x,s):
 if not x:raise ValueError(s)
def sig(t):return(t.GetNetname(),'through'if isinstance(t,p.PCB_VIA)else b.GetLayerName(t.GetLayer()),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
def specs(o):return(o['net'],o['layer'],tuple(round(z*1e6)for z in o['start']),tuple(round(z*1e6)for z in o['end']),round(o['width']*1e6),round(o.get('drill',0)*1e6)if o['type']=='via'else 0)
ts={uid(t):t for t in b.GetTracks()};bs={uid(t):t for t in base.GetTracks()};ss={uid(t):t for t in old.GetTracks()};rm=set(m['removed_dvp_uuids']);keep=set(bs)-rm;add={x['uuid']for x in m['added']}
req(len(bs)==468 and len(rm)==76 and len(keep)==392 and len(ts)==533 and len(add)==141,'COUNTS');req(set(ts)==keep|add and not keep&add,'SET');req(all(sig(ts[u])==sig(bs[u])for u in keep),'392 changed');req(all(bs[u].GetNetname().startswith('SENS_')for u in rm),'removed other')
for x,o in zip(m['added'],spec):
 req(sig(ts[x['uuid']])==specs(o),'MODEL DIFFERENCE')
 if x['old']:req(x['uuid']in ss and sig(ts[x['uuid']])==sig(ss[x['uuid']]),'OLD47 DIFFERENCE')
req(sum(x['old']for x in m['added'])==47,'OLD47 count')
def fp(f):return(f.GetReference(),f.GetValue(),f.GetFPID().GetLibNickname(),f.GetFPID().GetLibItemName(),xy(f.GetPosition()),f.GetLayer(),f.GetOrientationDegrees(),sorted((uid(q),q.GetNumber(),q.GetNetname(),xy(q.GetPosition()),xy(q.GetSize()),q.GetLayerSet().FmtHex(),q.GetOrientationDegrees())for q in f.Pads()))
req(len(list(b.GetFootprints()))==102 and sorted(map(fp,b.GetFootprints()))==sorted(map(fp,base.GetFootprints())),'FP SOURCE')
for f in B.rglob('*'):
 if f.is_file()and f.name not in ['mainboard_revD.kicad_pcb','mainboard_revD.kicad_prl']:req(f.read_bytes()==(N/f.relative_to(B)).read_bytes(),'SOURCE FILE')
def withouttracks(f):
 lines=f.read_text().splitlines(keepends=True);out=[];i=0
 while i<len(lines):
  if lines[i].startswith('\t(segment\n')or lines[i].startswith('\t(via\n')or lines[i].startswith('\t(arc\n'):
   i+=1
   while lines[i]!='\t)\n':i+=1
   i+=1
  else:out.append(lines[i]);i+=1
 return ''.join(out)
req(withouttracks(N/'mainboard_revD.kicad_pcb')==withouttracks(B/'mainboard_revD.kicad_pcb'),'NONCOPPER TEXT')
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
  if z.IsOnLayer(l):req(not z.GetFilledPolysList(l).OutlineCount(),'FILL')
b.BuildConnectivity();cn=b.GetConnectivity();pads={uid(q):q for f in b.GetFootprints()for q in f.Pads()};names={q.GetParentFootprint().GetReference()+'.'+q.GetNumber():u for u,q in pads.items()};g=collections.defaultdict(set)
for u,t in ts.items():
 for q in list(cn.GetConnectedTracks(t))+list(cn.GetConnectedPads(t)):
  if q.GetNetname()==t.GetNetname():g[u].add(uid(q));g[uid(q)].add(u)
def reach(start,omit=None):
 seen={start};todo=[start]
 while todo:
  for x in g[todo.pop()]:
   if x!=omit and x not in seen:seen.add(x);todo.append(x)
 return seen
oldnets=json.loads((R/'hardware/complete_net_restore_candidate_2014/restoration.json').read_text())['restored_nets'];closed=[]
for net in oldnets:
 pp=[u for u,q in pads.items()if q.GetNetname()==net];req(set(pp)<=reach(pp[0]),'19 NET OPEN '+net);closed.append(dict(net=net,actual_pad_count=len(pp),all_pads_connected=True))
rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows'];pairs=[(r['net'],r['translator_pin'],'J202.'+r['J202_pin'])for r in rows]+[('CAM_3V3_SW','JP301.2','J301.1'),('GND','J106.3','J301.2')];neg=[];chains=[]
for net,a,c in pairs:
 start,end=names[a],names[c];req(end in reach(start),'PAIR OPEN '+net);cut=next((u for u,t in ts.items()if t.GetNetname()==net and end not in reach(start,u)),None);req(cut,'NO CUT '+net);neg.append(dict(net=net,start=a,end=c,removed_uuid=cut));chains.append(dict(net=net,start=a,end=c,connected=True))
req(pads[names['JP301.1']].GetNetname()=='CAM_3V3_PRELINK'and pads[names['JP301.2']].GetNetname()=='CAM_3V3_SW','JP SOURCE');req(names['JP301.1']not in reach(names['JP301.2']),'JP BRIDGED')
for net,core in [('3V3_AON','J106.2'),('GND','J106.3')]:req(not {u for u,q in pads.items()if q.GetNetname()==net}<=reach(names[core]),'UNEXPECTED FULL POWER')
r=json.loads((D/'drc.json').read_text());req([len(r[x])for x in ['violations','unconnected_items','schematic_parity']]==[4,232,0],'DRC FACT');req(collections.Counter(x['type']for x in r['violations'])=={'via_dangling':2,'track_dangling':2},'UNEXPECTED DRC VIOLATION')
req(sha(B/'mainboard_revD.kicad_pcb')=='4d7bd85ae460928a48967c00adae133c05df5ef259a6789470c04e986b856f8a','BASE MUTATED');req(sha(N/'mainboard_revD.kicad_pcb')==m['pcb_sha'],'OUTPUT MUTATED')
print(json.dumps(dict(status='NOFAB_FOUR_OPEN_END_WARNINGS_232_UNCONNECTED',pcb_sha=sha(N/'mainboard_revD.kicad_pcb'),preserved_392=True,model_objects=141,old_sw_exact_objects=47,all_102_FP_and_pad_layer_sets_unchanged=True,other_native_text_and_source_unchanged=True,strict_drc=[4,232,0],exit_code=int((D/'drc.exit').read_text()),nineteen_nets=closed,fourteen_pair_chains=chains,fourteen_single_object_negatives=neg,JP301_OPEN=True,planes_empty=True,full_AON_or_GND_not_restored=True),indent=2))
