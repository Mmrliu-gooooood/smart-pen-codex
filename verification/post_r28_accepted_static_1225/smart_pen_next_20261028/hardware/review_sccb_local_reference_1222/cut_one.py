from pathlib import Path
import os,sys,json,shutil,subprocess,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/sccb1131negative'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from finite_copper import build,components
m=json.loads((D/'materialization.json').read_text());target=sys.argv[1]
def req(c,s):
 if not c:raise RuntimeError(s)
if target in ['CAM_SCL','CAM_SDA','BOTH']:
 nets=['CAM_SCL','CAM_SDA']if target=='BOTH'else[target];ids=[r['uuid']for r in m['mapping']if r['net']in nets]
else:
 xy={'MAIN_AON_VIA':[12.05,64.875],'BIAS_AON_VIA':[10.325,69.475],'C207_GND_VIA':[12,65.775]}[target];rows=[r for r in m['mapping']if r['type']=='via'and r['a']==xy];req(len(rows)==1,'exact selected via');nets=[rows[0]['net']];ids=[rows[0]['uuid']]
N=D/'negative_cuts'/target;shutil.copytree(D/'native',N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));before={n:components(v)for n,v in build(b).items()};tracks=list(b.GetTracks())
for t in tracks:
 if t.m_Uuid.AsString()in ids:b.Remove(t)
filler=p.ZONE_FILLER(b);filler.Fill(b.Zones());p.SaveBoard(str(f),b);b2=p.LoadBoard(str(f));after={n:components(v)for n,v in build(b2).items()};delta=sum(len(after[n])-len(before[n])for n in nets)
req(delta>0,'real pad-core disconnection required');req(all(before[n]==after[n]for n in before if n not in nets),'unrelated nets unchanged')
for n in nets:
 req(all(any(set(c)<=set(old)for old in before[n])for c in after[n]),'only splitting not merging')
if target in ['CAM_SCL','CAM_SDA','BOTH']:req(delta==len(nets),'one branch split per SCCB net')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(N/'drc.json'),str(f)],capture_output=True,text=True);(N/'drc.log').write_text(r.stdout+r.stderr);dr=json.loads((N/'drc.json').read_text());counts=[len(dr[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts[1:]==[67+delta,0],'airwires match independent finite partition delta');req(all(v['type']in ['track_dangling','via_dangling']for v in dr['violations']),'no unrelated DRC type')
(N/'result.json').write_text(json.dumps({'test_specimen_only':True,'target':target,'removed_uuids':ids,'affected_nets':nets,'before':{n:before[n]for n in nets},'after':{n:after[n]for n in nets},'partition_increase':delta,'unrelated_nets_unchanged':True,'DRC_unconnected_parity':counts,'pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest()},indent=2)+'\n')
print(target,counts)
