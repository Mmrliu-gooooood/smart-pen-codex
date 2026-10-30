from pathlib import Path
import os,json,hashlib,shutil,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/pen-gndnegative2305';os.environ['XDG_CACHE_HOME']='/tmp/pen-gndnegative2305-cache';os.environ['XDG_DATA_HOME']='/tmp/pen-gndnegative2305-data'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/aon_entry_bridge_candidate_2156/native';N=Path('/tmp/pen-gndnegative2305-native');shutil.copytree(D/'native',N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';ids=set(json.loads((D/'materialization.json').read_text())['added_uuids']);lines=f.read_text().splitlines(keepends=True);out=[];i=0;removed=0
while i<len(lines):
 if lines[i]in['\t(segment\n','\t(via\n','\t(arc\n']:
  z=[]
  while lines[i]!='\t)\n':z.append(lines[i]);i+=1
  z.append(lines[i]);s=''.join(z)
  if any(u in s for u in ids):removed+=1
  else:out+=z
 else:out.append(lines[i])
 i+=1
if removed!=96:raise RuntimeError('delete')
f.write_text(''.join(out));b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if f.read_bytes()!=(B/f.name).read_bytes():raise RuntimeError('not exact base')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(D/'negative_drc.json'),str(f)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(D/'negative_drc.log').write_text(r.stdout);j=json.loads((D/'negative_drc.json').read_text());c=[len(j[k])for k in ['violations','unconnected_items','schematic_parity']]
if c!=[0,231,0]or r.returncode!=5:raise RuntimeError('CLI')
print(json.dumps(dict(actual_native_removed_96_and_refilled=True,exact_base_sha=hashlib.sha256(f.read_bytes()).hexdigest(),full_drc=c,exit_code=r.returncode),indent=2))
