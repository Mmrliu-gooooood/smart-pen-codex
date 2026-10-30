from pathlib import Path
import os,json,sys,shutil,subprocess,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];os.environ['XDG_CONFIG_HOME']='/tmp/schmitt-negative0745';sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));import pcbnew as p
from finite_copper import build,components
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
m=json.loads((D/'materialization.json').read_text());prev=json.loads((R/'hardware/camera_isolation_control_native_0628/materialization.json').read_text());board=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));ts={t.m_Uuid.AsString():t for t in board.GetTracks()}
def req(c,msg):
 if not c:raise RuntimeError(msg)
cases={}
for name,group,net,start,targets in[
 ('r203_supply','r203_supply','3V3_AON','J106.2',['R203.2']),
 ('oe_pair202','oe_u202_pair','CAM_ISO_OE_N','U205.4',['U202.15']),
 ('oe_pair203','oe_u203_pair','CAM_ISO_OE_N','U205.4',['U203.14']),
 ('oe_upper','oe_u201_to_u202','CAM_ISO_OE_N','U205.4',['U201.22']),
 ('oe_middle','oe_u202_to_u203','CAM_ISO_OE_N','U205.4',['U202.14','U202.15','U201.22']),
 ('oe_lower','oe_u203_to_r203','CAM_ISO_OE_N','U205.4',['U203.14','U203.15']),
 ('io_mcu','io_mcu_pull','CAM_IO_EN','R107.1',['U101.48']),
 ('io_long','io_long','CAM_IO_EN','U101.48',['JP201.1']),
 ('io_link','io_link','IO_ENABLE_LINK','JP201.2',['R201.1'])]:cases[name]=([r['uuid']for r in prev['mapping']if r['tag']==group and r['uuid']in ts],net,start,targets)
for name,net,xy,start,targets,via in[
 ('new_oe','CAM_ISO_OE_N',(4.1,69.65),'U205.4',['R203.1','U201.22'],False),
 ('new_input','ISO_GATE',(1.3,70.9),'U205.2',['R201.2','R202.1'],True),
 ('new_supply','3V3_AON',(2.2,66.8),'J106.2',['U205.5','C209.1'],True),
 ('new_driver_ground','GND',(1.9,70.35),'J106.3',['U205.3'],True),
 ('new_cap_ground','GND',(4.9,69.0),'J106.3',['C209.2'],True)]:
 selected=[u for u in m['added']if ts[u].GetNetname()==net and isinstance(ts[u],p.PCB_VIA)==via and ts[u].GetStart()==p.VECTOR2I(*(round(z*1e6)for z in xy))];req(len(selected)==1,'exact cut '+name);cases[name]=(selected,net,start,targets)
if not os.environ.get('SCHMITT_NEG_CASE'):
 out=[]
 for name in cases:
  r=subprocess.run([sys.executable]+(['-O']if sys.flags.optimize else[])+[__file__],env={**os.environ,'SCHMITT_NEG_CASE':name},capture_output=True,text=True);(D/f'negative_{name}{"_O"if sys.flags.optimize else""}.log').write_text(r.stderr);req(r.returncode==0,name+' '+r.stderr);out.append(json.loads(r.stdout))
 print(json.dumps(out,indent=2));sys.exit()
name=os.environ['SCHMITT_NEG_CASE'];selected,net,start,targets=cases[name];req(selected,'nonempty cut');n=D/'native_negative'/name;shutil.copytree(D/'native',n,dirs_exist_ok=True);f=n/'mainboard_revD.kicad_pcb';s=f.read_text();edits=[]
for a,z,blk in children(s):
 if blk.startswith(('(segment','(via'))and any(u in blk for u in selected):edits.append((a,z))
req(len(edits)==len(selected),'exactcut')
for a,z in reversed(edits):s=s[:a]+s[z:]
f.write_text(s);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);b=p.LoadBoard(str(f));nodes=build(b);core=next(c for c in components(nodes[net])if start in c);req(not set(targets)&set(core),'cut detects physical disconnection')
for sig,pins in {'NIB_CONTACT_N':['C504.1','R503.2','R504.1','U101.7'],'STRAP_GPIO3':['R103.1','U101.8'],'AON_I2C_SCL':['R501.2','U101.10','U501.1'],'AON_I2C_SDA':['R502.2','U101.11','U501.4'],'PICKUP_INT_N':['U101.6','U501.12']}.items():req(components(nodes[sig])==[sorted(pins)],'unrelated '+sig)
req('J202.18'in next(c for c in components(nodes['SENS_EXTCLK'])if'U203.13'in c),'clock retained')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(n/'drc.json'),str(f)],capture_output=True,text=True);(n/'drc.log').write_text(r.stdout+r.stderr);d=json.loads((n/'drc.json').read_text());counts=[len(d[k])for k in['violations','unconnected_items','schematic_parity']];req(r.returncode==5 and counts[2]==0 and counts[1]>96,'realCLI detects cut');req(all(v['type']in['track_dangling','via_dangling']for v in d['violations']),'unexpected DRC')
print(json.dumps({'case':name,'removed':sorted(selected),'net':net,'source':start,'disconnected_targets':targets,'actual_remaining_source_component':core,'actual_DRC_unconnected_parity':counts,'unrelated_pressure_STRAP_IMU_I2C_clock_preserved':True,'pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest()},indent=2))
