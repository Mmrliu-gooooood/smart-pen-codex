from pathlib import Path
import os,json,sys,shutil,subprocess,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));os.environ['XDG_CONFIG_HOME']='/tmp/pressure-neg0433'
import pcbnew as p
from finite_copper import build,components
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
m=json.loads((D/'materialization.json').read_text());base=R/'hardware/imu_j107_clock_native_0405/native/mainboard_revD.kicad_pcb'
cases={'strap_escape':([2],'STRAP_GPIO3','U101.8',['R103.1']),'nib_long':([25],'NIB_CONTACT_N','U101.7',['R504.1']),'cap_ground':([13],'GND','J106.3',['C504.2']),'contact':([16],'CONTACT','J103.1',['R504.2']),'aon_via':([12],'3V3_AON','J106.2',['R503.1']),'j103_ground':([18],'GND','J106.3',['J103.2']),'rollback':(list(range(32)),'NIB_CONTACT_N','U101.7',['R504.1','C504.1','R503.2'])}
def req(c,s):
 if not c:raise RuntimeError(s)
if not os.environ.get('PRESSURE_NEG_CASE'):
 rows=[]
 for case in cases:
  r=subprocess.run([sys.executable]+(['-O']if sys.flags.optimize else[])+[__file__],env={**os.environ,'PRESSURE_NEG_CASE':case},capture_output=True,text=True);(D/f'negative_{case}{"_O"if sys.flags.optimize else""}.log').write_text(r.stderr);req(r.returncode==0,'case '+case+' '+r.stderr);rows.append(json.loads(r.stdout))
 print(json.dumps(rows,indent=2));sys.exit()
tag=os.environ['PRESSURE_NEG_CASE'];inds,net,st,targets=cases[tag];n=D/'native_negative'/tag;shutil.copytree(D/'native',n,dirs_exist_ok=True);f=n/base.name;s=f.read_text();removed={m['added'][i]for i in inds};cuts=[]
for a,b,blk in children(s):
 if blk.startswith(('(segment','(via'))and any(u in blk for u in removed):cuts.append((a,b))
req(len(cuts)==len(removed),'exactcuts')
for a,b in reversed(cuts):s=s[:a]+s[b:]
if tag=='rollback':
 old=[blk for a,b,blk in children(base.read_text())if blk.startswith(('(segment','(via'))and any(u in blk for u in m['removed'])]
 req(len(old)==4,'restore4');s=s[:s.rfind(')')]+'\n'.join(old)+'\n'+s[s.rfind(')'):]
f.write_text(s);board=p.LoadBoard(str(f));p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board)
actual=p.LoadBoard(str(f));core=next(c for c in components(build(actual)[net])if st in c);req(not set(targets)&set(core),'negative targets disconnected')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(n/'drc.json'),str(f)],capture_output=True,text=True);(n/'drc.log').write_text(r.stdout+r.stderr);j=json.loads((n/'drc.json').read_text());counts=[len(j[k])for k in['violations','unconnected_items','schematic_parity']];req(r.returncode==5 and counts[2]==0 and counts[1]>113,'negative CLI disconnected');req(all(v['type']in['track_dangling','via_dangling']for v in j['violations']),'unexpected violations')
if tag=='rollback':req(counts==[0,120,0],'rollbackcounts')
print(json.dumps({'tag':tag,'removed':sorted(removed),'disconnected':targets,'counts':counts,'violations':[v['type']for v in j['violations']],'core':core,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'restored_parent_byte_exact_raw':f.read_bytes()==base.read_bytes()if tag=='rollback'else None},indent=2))
