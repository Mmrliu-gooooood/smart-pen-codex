from pathlib import Path
import os,json,hashlib,collections
os.environ.update(XDG_CONFIG_HOME='/tmp/restore-review2020-config',XDG_CACHE_HOME='/tmp/restore-review2020-cache',XDG_DATA_HOME='/tmp/restore-review2020-data')
import pcbnew as p
from finite_copper import build,components,L
D=Path(__file__).resolve().parent;R=D.parents[1];F=D/'native/mainboard_revD.kicad_pcb';base=R/'hardware/dvp_mechanical_clearance_successor_1957/native/mainboard_revD.kicad_pcb';old=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'
def req(v,m):
 if not v:raise RuntimeError(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
req(sha(F)=='4d7bd85ae460928a48967c00adae133c05df5ef259a6789470c04e986b856f8a','SHA')
b=p.LoadBoard(str(F));a=p.LoadBoard(str(old));z=p.LoadBoard(str(base));info=json.loads((D/'restoration.json').read_text()); nets=set(info['restored_nets']);nodes=build(b);results=[];neg=[];author=json.loads((D/'verify_normal.json').read_text())
for n in sorted(nets):
 ns=nodes[n];pads=[name for name,isp,ss in ns if isp];cc=components(ns);req(len(cc)==1 and set(cc[0])==set(pads),'WHOLE_NET '+n);results.append({'net':n,'actual_pad_terminals':pads,'components':cc})
 u=next(x['removed_uuid']for x in author['nineteen_single_object_removal_negatives']if x['net']==n);bad=components([q for q in ns if q[0]!=u]);req(len(bad)>1,'REMOVE_NEGATIVE '+n);neg.append({'net':n,'removed_uuid':u,'components_after':bad})
req(len(nets)==19 and sum(len(x['actual_pad_terminals'])for x in results)==48,'COUNT')
rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows'];chains=[]
for r in rows:
 cc=components(nodes[r['net']]);dst='J202.'+r['J202_pin'];req(any(r['translator_pin']in c and dst in c for c in cc),'DVP '+r['net']);chains.append(r['net'])
def uid(t):return t.m_Uuid.AsString()
def sig(t):return(t.GetClass(),t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
prev={uid(t):sig(t)for t in z.GetTracks()};orig={uid(t):sig(t)for t in a.GetTracks()};cur={uid(t):sig(t)for t in b.GetTracks()};added=cur.keys()-prev.keys();req(len(added)==392 and all(cur[k]==prev[k]for k in prev),'BASE COPPER');req(all(cur[k]==orig[k]and cur[k][1]in nets for k in added),'EXACT ORIGINAL COPPER');req(len(cur)==468,'NO OTHERS')
fill=[]
for q in b.Zones():
 if q.GetIsRuleArea():continue
 for l in L:
  if q.IsOnLayer(l)and q.GetFilledPolysList(l).OutlineCount():fill.append([q.GetNetname(),b.GetLayerName(l)])
req(not fill and not any(t.GetNetname()in ['GND','3V3_AON','CAM_3V3_SW']for t in b.GetTracks()),'POWER RETURN SCOPE')
report=json.loads((D/'fresh_drc.json').read_text());counts=[len(report[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[0,233,0],'FRESH DRC')
source=[]
for f in old.parent.rglob('*'):
 if f.is_file() and f.suffix in ['.kicad_sch','.kicad_sym','.kicad_pro','.kicad_dru']:
  q=F.parent/f.relative_to(old.parent);req(sha(f)==sha(q),'SOURCE '+str(f));source.append(str(f.relative_to(old.parent)))
out={'status':'NINETEEN_COMPLETE_TRACK_NETS_ONLY_NOFAB','source_equal_to_accepted':source,'exact_original_added_objects':392,'old_76_unchanged':True,'finite_copper_whole_net_results':results,'finite_copper_removal_negatives':neg,'twelve_DVP_chains':chains,'fresh_DRC':counts,'unconnected_reduction':262-counts[1],'pad_count_minus_net_count':48-19,'filled_planes':fill,'GND_AON_SW_tracks':0,'return_qualification':'Absent. RF/USB/CAM_ON inherited geometry does not imply qualified return, impedance, ground bounce or load behavior.'}
(D/'independent_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
