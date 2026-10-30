from pathlib import Path
import os,json,hashlib,shutil,sys
os.environ['XDG_CONFIG_HOME']='/tmp/pen-restore2014-config'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';BASE=D.parent/'dvp_mechanical_clearance_successor_1957/native';PLAN=R/'docs/electronics/copper_recovery_plan_2005/recovery_plan.json';N=Path(sys.argv[2]).resolve()if len(sys.argv)==3 and sys.argv[1]=='--replay-dir'else D/'native'
if N.exists():raise RuntimeError('REFUSE OVERWRITE')
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
if sha(S)!='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038'or sha(BASE/'mainboard_revD.kicad_pcb')!='f92c7517b40466208d907d30b076ccd80d40bb3c298c162b40891f86b5070f19':raise RuntimeError('SOURCE HASH')
r=json.loads(PLAN.read_text());nets=set(r['whole_track_net_candidates']);ids={o['uuid']for o in r['objects']if o['net']in nets}
if len(nets)!=19 or nets&{'3V3_AON','GND','CAM_3V3_SW'}:raise RuntimeError('SCOPE')
shutil.copytree(BASE,N,ignore=shutil.ignore_patterns('*.kicad_prl'));b=p.LoadBoard(str(N/'mainboard_revD.kicad_pcb'));a=p.LoadBoard(str(S));existing={t.m_Uuid.AsString()for t in b.GetTracks()};added=[]
for t in a.GetTracks():
 if t.m_Uuid.AsString()not in ids:continue
 if t.m_Uuid.AsString()in existing:raise RuntimeError('UUID COLLISION')
 c=p.Cast_to_PCB_VIA(p.Cast_to_BOARD_ITEM(t.Clone()))if isinstance(t,p.PCB_VIA)else p.Cast_to_PCB_TRACK(p.Cast_to_BOARD_ITEM(t.Clone()));c.SetParent(b);c.SetNetCode(b.GetNetcodeFromNetname(t.GetNetname()));b.Add(c)
 if c.m_Uuid.AsString()!=t.m_Uuid.AsString():raise RuntimeError('UUID DRIFT')
 added.append({'uuid':c.m_Uuid.AsString(),'net':c.GetNetname()})
if len(added)!=len(ids):raise RuntimeError('MISSING OBJECTS')
b.BuildConnectivity();p.SaveBoard(str(N/'mainboard_revD.kicad_pcb'),b)
out={'status':'NOFAB_NINETEEN_TRACK_NETS_ONLY_NO_POWER_OR_PLANES','source_sha':sha(S),'base_sha':sha(BASE/'mainboard_revD.kicad_pcb'),'pcb_sha':sha(N/'mainboard_revD.kicad_pcb'),'restored_nets':sorted(nets),'added_objects':added}
if N==D/'native':(D/'restoration.json').write_text(json.dumps(out,indent=2)+'\n')
else:
 if sha(N/'mainboard_revD.kicad_pcb')!=sha(D/'native/mainboard_revD.kicad_pcb'):raise RuntimeError('REPLAY HASH')
print(json.dumps({'pcb_sha':out['pcb_sha'],'restored_nets':len(nets),'objects':len(added)},indent=2))
