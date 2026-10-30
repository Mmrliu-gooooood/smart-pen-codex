from pathlib import Path
import os,json,hashlib,collections
os.environ['XDG_CONFIG_HOME']='/tmp/pen-restore2014-config'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/j202_low_speed_reference_candidate/native';BASE=D.parent/'dvp_mechanical_clearance_successor_1957/native';N=D/'native';b=p.LoadBoard(str(N/'mainboard_revD.kicad_pcb'));old=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(BASE/'mainboard_revD.kicad_pcb'));info=json.loads((D/'restoration.json').read_text());nets=set(info['restored_nets']);add={x['uuid']for x in info['added_objects']}
def req(x,m):
 if not x:raise ValueError(m)
def uid(t):return t.m_Uuid.AsString()
def xy(v):return(v.x,v.y)
def tr(t):return(t.GetNetname(),t.GetLayer(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
a={uid(t):tr(t)for t in old.GetTracks()};z={uid(t):tr(t)for t in base.GetTracks()};c={uid(t):tr(t)for t in b.GetTracks()}
req(len(c)==468 and len(add)==392 and len(z)==76,'COUNTS');req(set(c)==set(z)|add and not(set(z)&add),'SET');req(all(c[k]==z[k]for k in z),'12ROUTES CHANGED');req(all(c[k]==a[k]and c[k][0]in nets for k in add),'OLD EXACT UUID COPPER');req(not nets&{'GND','3V3_AON','CAM_3V3_SW'},'POWER SCOPE')
def fp(f):return(f.GetReference(),f.GetValue(),f.GetFPID().GetLibNickname(),f.GetFPID().GetLibItemName(),xy(f.GetPosition()),f.GetLayer(),f.GetOrientationDegrees(),sorted((uid(q),q.GetNumber(),q.GetNetname(),xy(q.GetPosition()),xy(q.GetSize()),q.GetLayerSet().FmtHex(),q.GetOrientationDegrees())for q in f.Pads()))
req(sorted(map(fp,b.GetFootprints()))==sorted(map(fp,base.GetFootprints())),'FOOTPRINT DRIFT')
for path in BASE.rglob('*'):
 if path.is_file()and path.name not in ['mainboard_revD.kicad_pcb','mainboard_revD.kicad_prl']:req(path.read_bytes()==(N/path.relative_to(BASE)).read_bytes(),'SOURCE BYTES')
# Deleting track/via text blocks from both files must leave all remaining native text byte-identical.
def withouttracks(path):
 lines=path.read_text().splitlines(keepends=True);out=[];i=0
 while i<len(lines):
  if lines[i].startswith('\t(segment\n')or lines[i].startswith('\t(via\n')or lines[i].startswith('\t(arc\n'):
   i+=1
   while i<len(lines)and lines[i]!='\t)\n':i+=1
   i+=1
  else:out.append(lines[i]);i+=1
 return ''.join(out)
req(withouttracks(N/'mainboard_revD.kicad_pcb')==withouttracks(BASE/'mainboard_revD.kicad_pcb'),'ZONE/OTHER NATIVE CHANGED')
for q in list(b.Zones()):
 if not q.GetIsRuleArea():
  for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
   if q.IsOnLayer(l):req(not q.GetFilledPolysList(l).OutlineCount(),'UNEXPECTED FILL')
 # Keep the verified empty zone definitions; no conductive fill exists.
b.BuildConnectivity();cn=b.GetConnectivity();ts={uid(t):t for t in b.GetTracks()};graph=collections.defaultdict(set);pads={uid(q):q for f in b.GetFootprints()for q in f.Pads()}
def edge(x,y):graph[x].add(y);graph[y].add(x)
for k,t in ts.items():
 for q in cn.GetConnectedTracks(t):
  if q.GetNetname()==t.GetNetname():edge(k,uid(q))
 for q in cn.GetConnectedPads(t):edge(k,uid(q))
def reaches(start,omit=None):
 seen={start};todo=[start]
 while todo:
  v=todo.pop()
  for q in graph[v]:
   if q!=omit and q not in seen:seen.add(q);todo.append(q)
 return seen
results=[];neg=[]
for n in sorted(nets):
 pp=[k for k,q in pads.items()if q.GetNetname()==n];req(len(pp)>=2,'NETTERMS')
 req(set(pp)<=reaches(pp[0]),'NET OPEN '+n)
 critical=None
 for k,t in ts.items():
  if t.GetNetname()!=n:continue
  if not set(pp)<=reaches(pp[0],k):critical=k;break
 req(critical is not None,'NO SINGLE OBJECT NEGATIVE '+n)
 results.append({'net':n,'pads':[{'uuid':k,'terminal':pads[k].GetParentFootprint().GetReference()+'.'+pads[k].GetNumber()}for k in pp],'all_actual_pads_one_component':True});neg.append({'net':n,'removed_uuid':critical,'expected_disconnected':True})
rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows'];chain=[]
for row in rows:
 source=row['translator_pin'];head='J202.'+row['J202_pin'];sp=[k for k,q in pads.items()if q.GetParentFootprint().GetReference()+'.'+q.GetNumber()==source];hp=[k for k,q in pads.items()if q.GetParentFootprint().GetReference()+'.'+q.GetNumber()==head];req(len(sp)==len(hp)==1and hp[0]in reaches(sp[0]),'12CHAIN '+row['net']);chain.append(row['net'])
rpt=json.loads((D/'drc.json').read_text());req(not rpt['violations']and not rpt['schematic_parity']and len(rpt['unconnected_items'])==233,'DRC')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
req(sha(BASE/'mainboard_revD.kicad_pcb')=='f92c7517b40466208d907d30b076ccd80d40bb3c298c162b40891f86b5070f19','BASE HASH');req(sha(S/'mainboard_revD.kicad_pcb')=='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038','SOURCE HASH')
print(json.dumps({'status':'NOFAB_NINETEEN_COMPLETE_TRACK_NETS_ONLY','pcb_sha256':sha(N/'mainboard_revD.kicad_pcb'),'exact_original_objects_restored':len(add),'previous_76_copper_and_all_102_footprints_unchanged':True,'other_native_text_source_and_zone_fill_unchanged':True,'strict_drc':[0,233,0],'nineteen_net_pad_connectivity':results,'nineteen_single_object_removal_negatives':neg,'previous_12_chain_connectivity':chain,'no_power_ground_or_zone_restoration':True},indent=2))
