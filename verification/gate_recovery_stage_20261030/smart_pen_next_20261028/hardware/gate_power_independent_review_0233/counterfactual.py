from pathlib import Path
import os,json,hashlib,re,shutil,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/sens-counter0158'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];N=D/'native';B=R/'hardware/sens_tree_candidate_0158/native';m=json.loads((D/'materialization.json').read_text());patt=r'\t\((?:segment|via)\n.*?\n\t\)\n';out=D/'counterfactual_restore_parent';shutil.copytree(N,out,dirs_exist_ok=True);f=out/'mainboard_revD.kicad_pcb';s=f.read_text();found=[]
def cut(x):
 q=x.group(0)
 for u in m['added']:
  if u in q:found.append(u);return ''
 return q
s=re.sub(patt,cut,s,flags=re.S)
if set(found)!=set(m['added']):raise RuntimeError('added removal')
blocks=[];f.write_text(s);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
if sha(f)!=sha(B/f.name):raise RuntimeError('restore parent SHA differs '+sha(f))
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(f)],capture_output=True,text=True);(out/'drc.log').write_text(r.stdout+r.stderr);j=json.loads((out/'drc.json').read_text());counts=[len(j[k])for k in ['violations','unconnected_items','schematic_parity']]
if counts!=[0,143,0]or r.returncode!=5:raise RuntimeError('counterfactualDRC')
print(json.dumps(dict(status='RESTORED_ALL_OLD_OBJECTS_AND_POSES_EXACTLY',removed_added=len(found),restored_original=len(blocks),counterfactual_sha=sha(f),parent_sha=sha(B/f.name),native_DRC=counts,exit=r.returncode),indent=2))
