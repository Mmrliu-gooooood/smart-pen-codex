from pathlib import Path
import os,json,sys,shutil,subprocess,re,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));os.environ['XDG_CONFIG_HOME']='/tmp/imu-neg0405'
import pcbnew as p
from finite_copper import build,components
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
m=json.loads((D/'materialization.json').read_text());base=R/'hardware/pressure_pullup_revision_0318/native/mainboard_revD.kicad_pcb'
cases={'aon_access':([8],'3V3_AON','J106.2',['U501.2','U501.3','U501.9','U501.10','C501.1','C502.1','C503.1']),'ground_access':([15],'GND','J106.3',['U501.5','U501.6','U501.7','U501.8','C501.2','C502.2','C503.2']),'clock_middle':([30],'SENS_EXTCLK','U203.13',['J202.18']),'rollback':(list(range(33)),'GND','J106.3',[])}
def req(c,s):
 if not c:raise RuntimeError(s)
if not os.environ.get('IMU_NEG_CASE'):
 rows=[]
 for case in cases:
  r=subprocess.run([sys.executable]+(['-O']if sys.flags.optimize else[])+[__file__],env={**os.environ,'IMU_NEG_CASE':case},capture_output=True,text=True);(D/f'negative_{case}{"_O"if sys.flags.optimize else""}.log').write_text(r.stderr);req(r.returncode==0,'case '+case+' '+r.stderr);rows.append(json.loads(r.stdout))
 print(json.dumps(rows,indent=2));sys.exit()
tag=os.environ['IMU_NEG_CASE'];inds,net,st,targets=cases[tag];n=D/'native_negative'/tag;shutil.copytree(D/'native',n,dirs_exist_ok=True);f=n/base.name;s=f.read_text();removed={m['added'][i]for i in inds};cuts=[]
for a,b,blk in children(s):
 if blk.startswith(('(segment','(via'))and any(u in blk for u in removed):cuts.append((a,b))
req(len(cuts)==len(removed),'exactcuts')
for a,b in reversed(cuts):s=s[:a]+s[b:]
if tag=='rollback':
 old=next(blk for a,b,blk in children(base.read_text())if blk.startswith('(segment')and m['removed'][0]in blk)
 s=s[:s.rfind(')')]+'\t'+old+'\n'+s[s.rfind(')'):]
 for a,b,blk in children(s):
  if blk.startswith('(footprint ')and '(property "Reference" "J107"'in blk:s=s[:a]+blk.replace('(at 5.2 84 180)','(at 3.2 84 180)',1)+s[b:];break
f.write_text(s);board=p.LoadBoard(str(f));p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board)
# Reload from disk after fill before independent finite check.
actual=p.LoadBoard(str(f));core=next(c for c in components(build(actual)[net])if st in c);req(not set(targets)&set(core),'negative targets disconnected')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(n/'drc.json'),str(f)],capture_output=True,text=True);(n/'drc.log').write_text(r.stdout+r.stderr);j=json.loads((n/'drc.json').read_text());counts=[len(j[k])for k in['violations','unconnected_items','schematic_parity']];req(r.returncode==5 and counts[2]==0,'CLI/parity');req([v['type']for v in j['violations']]==(['via_dangling','via_dangling']if tag=='clock_middle'else ['track_dangling']if tag=='ground_access'else []),'unexpected negative violation');req(counts[1]>120,'negative unconnected increase')
if tag=='rollback':req(counts==[0,134,0],'rollbackcounts')
print(json.dumps({'tag':tag,'removed':sorted(removed),'disconnected':targets,'counts':counts,'violations':[v['type']for v in j['violations']],'core':core,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'restored_parent_byte_exact':f.read_bytes()==base.read_bytes()if tag=='rollback'else None},indent=2))
