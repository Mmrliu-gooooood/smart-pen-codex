from pathlib import Path
import os,re,json,shutil,tempfile,hashlib,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;B=D.parent/'j107_mode_port_closure';delta=json.loads((D/'routing_delta.json').read_text());source=B/'native/mainboard_revD.kicad_pcb';candidate=D/'native/mainboard_revD.kicad_pcb';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if sha(source)!=delta['base_sha256']or sha(candidate)!=delta['candidate_sha256']:raise RuntimeError('Replay input changed')
def blocks(text,kind):
 out={}
 for q in re.findall(r'\n\t\('+kind+r'[^\n]*\n.*?\n\t\)',text,re.S):
  u=re.search(r'\(uuid "([^"\n]+)"\)',q)
  if u:out[u[1]]=q
 return out
raw=source.read_text();new=candidate.read_text();cu={**blocks(new,'segment'),**blocks(new,'via')};zones=blocks(new,'zone');removed=set(delta['removed']);modified=set(delta['modified'])
raw=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',lambda m:''if any(u in m[0]for u in removed)else next((cu[u]for u in modified if u in m[0]),m[0]),raw,flags=re.S)
rid=delta['changed_rule_uuid'];raw=re.sub(r'\n\t\(zone\n.*?\n\t\)',lambda m:zones[rid]if rid in m[0]else m[0],raw,flags=re.S);i=raw.rfind(')');raw=raw[:i]+''.join(cu[u]for u in delta['added'])+zones[delta['added_rule_uuid']]+'\n'+raw[i:]
results={}
with tempfile.TemporaryDirectory(prefix='irq-replay-')as td:
 for name,text in[('replay',raw),('refill',new)]:
  out=Path(td)/name;shutil.copytree(D/'native',out);f=out/'mainboard_revD.kicad_pcb';f.write_text(text);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);h=sha(f);results[name]={'pcb_sha256':h,'exact_candidate_sha_match':h==delta['candidate_sha256']}
  if h!=delta['candidate_sha256']:raise RuntimeError('Replay/refill identity mismatch '+name+' '+h)
  cmd=['/usr/bin/python3',str(D/'verify.py'),str(f)];r=subprocess.run(cmd,capture_output=True,text=True);results[name]['verify_exit']=r.returncode
  if r.returncode:raise RuntimeError('Replayed graph verification failed '+r.stderr[-1000:])
(D/'replay_and_refill.json').write_text(json.dumps(results,indent=2));print(results)
