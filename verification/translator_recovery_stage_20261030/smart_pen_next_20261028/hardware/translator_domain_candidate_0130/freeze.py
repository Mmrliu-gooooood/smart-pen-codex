from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/mcu_power_ground_clearance_0109'
def entry(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
base=B/'native/mainboard_revD.kicad_pcb'
if hashlib.sha256(base.read_bytes()).hexdigest()!='77537f15c2beff27ec3098c0ccd9d3dd5cd10ac335b74c4909954f2fedcf4a24':raise RuntimeError('baseline changed')
deps=[B/'manifest.json']+[p for p in(B/'native').rglob('*')if p.is_file()and p.suffix!='.kicad_prl']
(D/'dependencies.json').write_text(json.dumps([entry(p,R)for p in sorted(deps)],indent=2)+'\n')
(D/'EXCLUSIONS.json').write_text(json.dumps(dict(excluded=['**/__pycache__/**','**/*.kicad_prl','replay/native/** (duplicate exact replay)','native_negative/*/native/** (script-reproducible counterfactual source copies)','counterfactual_restore_parent/native/** (exact parent source copy)'],status='NOFAB_NOPOWER_LOCAL_DOMAINS_ONLY',note='Root planning models and rejected logs explicitly retained as nonnative planning/tool failure evidence, not successful routes. No SENS external-input connection claimed.'),indent=2)+'\n')
files=[p for p in D.iterdir()if p.is_file()and p.name!='manifest.json'and p.suffix in['.py','.json','.md','.log','.exit','.png','.txt']]
files += [p for p in(D/'native').rglob('*')if p.is_file()and p.suffix!='.kicad_prl']
for sub in ['native_negative','counterfactual_restore_parent']:
 files += [p for p in(D/sub).rglob('drc.*')if p.is_file()]
files += [D/'replay/materialization.json']
rows=[entry(p,D)for p in sorted(set(files))]
(D/'manifest.json').write_text(json.dumps(dict(status='NOFAB_NOPOWER_RESEARCH_LOCAL_TRANSLATOR_DOMAINS_SENSOR_INPUT_ISOLATED',files=rows),indent=2)+'\n')
for row in rows:
 p=D/row['path']
 if entry(p,D)!=row:raise RuntimeError('manifest mismatch')
print(len(rows),hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest())
