from pathlib import Path
import argparse,os,re,shutil,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;H=D.parent;dep=json.loads((D/'dependencies.json').read_text());ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);out=Path(ap.parse_args().output).resolve();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if out.exists():raise RuntimeError('Output must be a new isolated directory')
for f,key in[(H/'j107_mode_port_closure/manifest.json','baseline_manifest_sha256'),(H/'mems_layered_rule_study/manifest.json','mems_rule_manifest_sha256'),(H/'mems_layered_independent_review/manifest.json','mems_review_manifest_sha256'),(D/'input_irq_all6.kicad_pcb','input_irq_sha256')]:
 if sha(f)!=dep[key]:raise RuntimeError('Frozen dependency mismatch '+str(f))
shutil.copytree(H/'j107_mode_port_closure/native',out);raw=(D/'input_irq_all6.kicad_pcb').read_text();mr=(H/'mems_layered_rule_study/native/mainboard_revD.kicad_pcb').read_text();ids=['2a715b0e-d7bf-49ab-b132-f7f180326c33','c59d76d7-4fe7-4475-8382-e1c75d7f8d6c'];blocks={u:next(q for q in re.findall(r'\n\t\(zone\n.*?\n\t\)',mr,re.S)if u in q)for u in ids}
raw=re.sub(r'\n\t\(zone\n.*?\n\t\)',lambda m:blocks[ids[0]]if ids[0]in m[0]else m[0],raw,flags=re.S);i=raw.rfind(')');raw=raw[:i]+blocks[ids[1]]+'\n'+raw[i:];f=out/'mainboard_revD.kicad_pcb';f.write_text(raw);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if sha(f)!=dep['candidate_sha256']:raise RuntimeError('Combined build hash mismatch '+sha(f))
print(json.dumps({'status':'EXACT_COMBINED_BUILD_REPRODUCED','pcb_sha256':sha(f),'output':str(f)},indent=2))
