from pathlib import Path
import os,json,sys,shutil,subprocess,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];os.environ['XDG_CONFIG_HOME']='/tmp/imucontrol-negative0522';sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));import pcbnew as p
from finite_copper import build,components
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
m=json.loads((D/'materialization.json').read_text());base=R/'hardware/pressure_joint_native_0433/native/mainboard_revD.kicad_pcb'
cases={
'scl_long':('scl_long',None,'AON_I2C_SCL','U101.10',['U501.1','R501.2']),
'sda_long':('sda_long',None,'AON_I2C_SDA','U101.11',['U501.4','R502.2']),
'irq_long':('irq_long',None,'PICKUP_INT_N','U101.6',['U501.12']),
'irq_mcu_source':('irq_mcu',0,'PICKUP_INT_N','U101.6',['U501.12']),
'scl_pullup_signal':('scl_pullup',None,'AON_I2C_SCL','U101.10',['R501.2']),
'sda_pullup_signal':('sda_pullup',None,'AON_I2C_SDA','U101.11',['R502.2']),
'left_pullup_AON_via':('pullup_left',1,'3V3_AON','J106.2',['R501.1']),
'right_pullup_AON':('pullup_right',None,'3V3_AON','J106.2',['R502.1']),
'CS_SA0_AON_via':('aon_left_reconnect',0,'3V3_AON','J106.2',['U501.2','U501.3']),
'rollback':('*',None,'PICKUP_INT_N','U101.6',['U501.12'])}
def req(c,msg):
 if not c:raise RuntimeError(msg)
if not os.environ.get('IMU_NEG_CASE'):
 out=[]
 for tag in cases:
  cmd=[sys.executable]+(['-O']if sys.flags.optimize else[])+[__file__];r=subprocess.run(cmd,env={**os.environ,'IMU_NEG_CASE':tag},capture_output=True,text=True);(D/f'negative_{tag}{"_O"if sys.flags.optimize else""}.log').write_text(r.stderr);req(r.returncode==0,tag+' '+r.stderr);out.append(json.loads(r.stdout))
 print(json.dumps(out,indent=2));sys.exit()
tag=os.environ['IMU_NEG_CASE'];group,index,net,start,targets=cases[tag];selected={row['uuid']for row in m['mapping']if(group=='*'or row['tag']==group)and(index is None or row['index']==index)};req(selected,'nonemptycut');n=D/'native_negative'/tag;shutil.copytree(D/'native',n,dirs_exist_ok=True);f=n/base.name;s=f.read_text();edits=[]
for a,b,blk in children(s):
 if blk.startswith(('(segment','(via'))and any(u in blk for u in selected):edits.append((a,b))
req(len(edits)==len(selected),'exactcut')
for a,b in reversed(edits):s=s[:a]+s[b:]
if tag=='rollback':
 blocks=[blk for a,b,blk in children(base.read_text())if blk.startswith(('(segment','(via'))and any(u in blk for u in m['removed'])];req(len(blocks)==3,'restore3');j=s.rfind(')');s=s[:j]+'\n'.join(blocks)+'\n'+s[j:]
f.write_text(s);board=p.LoadBoard(str(f));board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board);board=p.LoadBoard(str(f));nodes=build(board);core=next(c for c in components(nodes[net])if start in c);req(not set(targets)&set(core),'negative targets actual disconnected')
req(components(nodes['NIB_CONTACT_N'])==[['C504.1','R503.2','R504.1','U101.7']],'pressure preserved');req(components(nodes['STRAP_GPIO3'])==[['R103.1','U101.8']],'strap preserved');clock=next(c for c in components(nodes['SENS_EXTCLK'])if'U203.13'in c);req('J202.18'in clock,'clock preserved')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(n/'drc.json'),str(f)],capture_output=True,text=True);(n/'drc.log').write_text(r.stdout+r.stderr);d=json.loads((n/'drc.json').read_text());counts=[len(d[k])for k in['violations','unconnected_items','schematic_parity']];req(r.returncode==5 and counts[2]==0 and counts[1]>106,'actual disconnected CLI');req(all(v['type']in['track_dangling','via_dangling']for v in d['violations']),'unexpected hard violations')
if tag=='rollback':req(counts==[0,113,0],'rollback actual nativecounts')
print(json.dumps({'case':tag,'removed':sorted(selected),'net':net,'source':start,'disconnected_targets':targets,'actual_remaining_source_component':core,'DRC_counts':counts,'violation_types':[v['type']for v in d['violations']],'pressure_STRAP_clock_preserved':True,'pcb_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'rollback_raw_parent_byte_equal':f.read_bytes()==base.read_bytes()if tag=='rollback'else None},indent=2))
