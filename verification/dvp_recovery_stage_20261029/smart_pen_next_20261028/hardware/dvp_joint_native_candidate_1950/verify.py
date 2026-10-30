from pathlib import Path
import os,json,hashlib,collections,sys
for k,v in [('XDG_CONFIG_HOME','/tmp/pen-native1950-config'),('XDG_CACHE_HOME','/tmp/pen-native1950-cache'),('XDG_DATA_HOME','/tmp/pen-native1950-data')]:os.environ[k]=v
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];N=D/'native';S=R/'hardware/dvp_rotated_group_placement_1835/native';A=R/'hardware/j202_low_speed_reference_candidate/native';M=R/'docs/electronics/dvp_joint_feasibility_1942'
b=p.LoadBoard(str(N/'mainboard_revD.kicad_pcb'));s=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));a=p.LoadBoard(str(A/'mainboard_revD.kicad_pcb'));g=json.loads((M/'result.json').read_text())['geometry']; rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows'];delta=json.loads((M/'placement_delta.json').read_text());tracks=list(b.GetTracks());layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def need(x,msg):
 if not x:raise RuntimeError(msg)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def fps(board):return {f.GetReference():f for f in board.GetFootprints()}
def sig(f):return [f.GetValue(),[f.GetFPID().GetLibNickname(),f.GetFPID().GetLibItemName()],sorted((q.GetNumber(),q.GetNetname())for q in f.Pads())]
def pose(f):return {'xy':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],'angle':f.GetOrientationDegrees(),'layer':f.GetLayerName()}
f,z,orig=fps(b),fps(s),fps(a);need(set(f)==set(z)==set(orig)and len(f)==102,'REF SET')
for r in f:need(sig(f[r])==sig(z[r])==sig(orig[r]),'SOURCE '+r)
changed={r:{'before':pose(z[r]),'after':pose(f[r])} for r in f if pose(f[r])!=pose(z[r])};need(set(changed)==set(delta),'DELTAREFS')
for r,v in changed.items():need(v['after']=={k:delta[r]['after'][k] for k in ('xy','angle','layer')},'POSE '+r)
need(pose(f['J103'])==pose(orig['J103'])and pose(f['J106'])==pose(orig['J106']),'CRITICAL PORT')
for path in S.rglob('*'):
 if path.is_file() and path.name not in ('mainboard_revD.kicad_pcb','mainboard_revD.kicad_prl'):need((N/path.relative_to(S)).read_bytes()==path.read_bytes(),'BYTE SOURCE '+str(path))
def canon(t):return (t.GetNetname(),'via' if isinstance(t,p.PCB_VIA)else'track',tuple([t.GetStart().x,t.GetStart().y]),tuple([t.GetEnd().x,t.GetEnd().y]),'through'if isinstance(t,p.PCB_VIA)else b.GetLayerName(t.GetLayer()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
expected=[(x['net'],x['type'],tuple(round(v*1e6)for v in x['start']),tuple(round(v*1e6)for v in x['end']),x['layer'],round(x['width_mm']*1e6),200000 if x['type']=='via'else 0)for x in g];need(collections.Counter(map(canon,tracks))==collections.Counter(expected),'EXACT COPPER')
need(sum(isinstance(t,p.PCB_VIA)for t in tracks)==16 and len(tracks)==76,'COUNT')
for zz in b.Zones():
 if not zz.GetIsRuleArea():
  for l in layers:
   if zz.IsOnLayer(l):need(not zz.GetFilledPolysList(l).OutlineCount(),'UNEXPECTED FILL')
def point(v):return(v.x,v.y)
def endpoints(t,layer):return [(layer,*point(t.GetStart())),(layer,*point(t.GetEnd()))]
def pathcheck(ts,row):
 net=row['net'];graph={}
 def join(x,y):graph.setdefault(x,set()).add(y);graph.setdefault(y,set()).add(x)
 for t in ts:
  if t.GetNetname()!=net:continue
  if isinstance(t,p.PCB_VIA):
   pts=[(l,*point(t.GetPosition()))for l in layers]
   for v in pts[1:]:join(pts[0],v)
  else:join(*endpoints(t,t.GetLayer()))
 ref,pin=row['translator_pin'].split('.');sp=next(q for q in f[ref].Pads()if q.GetNumber()==pin);hp=next(q for q in f['J202'].Pads()if q.GetNumber()==row['J202_pin']);need(sp.GetNetname()==hp.GetNetname()==net,'END NET')
 starts=[(l,*point(sp.GetPosition()))for l in layers if sp.IsOnLayer(l)];targets={(l,*point(hp.GetPosition()))for l in layers if hp.IsOnLayer(l)};seen=set(starts);todo=list(starts)
 while todo:
  v=todo.pop()
  for w in graph.get(v,[]):
   if w not in seen:seen.add(w);todo.append(w)
 return bool(seen&targets)
connected=[r['net']for r in rows if pathcheck(tracks,r)];need(len(connected)==12,'PATHS')
negative=[]
for row in rows:
 t=next(t for t in tracks if not isinstance(t,p.PCB_VIA)and t.GetNetname()==row['net']);need(not pathcheck([q for q in tracks if q!=t],row),'OPEN NEGATIVE '+row['net']);negative.append(row['net'])
rpt=json.loads((D/'drc.json').read_text());need(not rpt['violations']and not rpt['schematic_parity']and len(rpt['unconnected_items'])==262,'DRC')
allchanges={r:{'before':pose(orig[r]),'after':pose(f[r])}for r in f if pose(orig[r])!=pose(f[r])}
(D/'all_placement_changes_from_9a03.json').write_text(json.dumps(allchanges,indent=2)+'\n')
out={'status':'TWELVE_TRANSLATOR_TO_J202_CHAINS_ONLY_NOFAB','pcb_sha256':sha(N/'mainboard_revD.kicad_pcb'),'source_unchanged':sha(S/'mainboard_revD.kicad_pcb')=='7d197c4db87e936bd26fc9bb6052036aaf42c3a0e3e92032eac445e4909a6ff1','same_102_ref_value_footprint_padnets':True,'new_6_pose_changes':sorted(changed),'total_pose_changes_from_9a03':len(allchanges),'same_critical_ports':True,'tracks':60,'vias':16,'connected_chains':connected,'open_chain_negative_tests_rejected':negative,'strict_drc':[0,262,0],'remaining_unconnected_by_net':dict(collections.Counter(x['items'][0].get('description','').split('[')[-1].split(']')[0]for x in rpt['unconnected_items'])),'no_plane_fill_and_no_old_routing':True,'remaining':'Bias stubs, MCU-side wiring, supplies/grounds/decoupling, other interfaces, return planes and mechanical qualification remain open.'}
print(json.dumps(out,indent=2))
