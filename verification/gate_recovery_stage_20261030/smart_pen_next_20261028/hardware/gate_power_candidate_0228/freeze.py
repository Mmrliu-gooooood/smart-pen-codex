from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(x,m):
 if not x:raise RuntimeError(m)
m=json.loads((D/'materialization.json').read_text());req(sha(D/'native/mainboard_revD.kicad_pcb')==m['pcb_sha'],'native');req(sha(R/'hardware/sens_tree_candidate_0158/native/mainboard_revD.kicad_pcb')==m['base_sha'],'immutable parent');req((D/'native/mainboard_revD.kicad_pcb').read_bytes()==(D/'replay/native/mainboard_revD.kicad_pcb').read_bytes(),'replay');req((D/'verification.json').read_bytes()==(D/'verification_optimized.json').read_bytes(),'optimized');req(json.loads((D/'verification.json').read_text())['native_DRC']==[0,137,0],'drc');req(len(json.loads((D/'negative.json').read_text()))==5,'negative')
base=R/'hardware/sens_tree_candidate_0158/native';deps=[]
for f in sorted(base.rglob('*')):
 if f.is_file() and f.suffix!='.kicad_prl':
  if f.suffix!='.kicad_pcb':req(f.read_bytes()==(D/'native'/f.relative_to(base)).read_bytes(),'source unchanged')
  deps.append(dict(path=str(f.relative_to(R)),sha256=sha(f),bytes=f.stat().st_size))
for name in ['gate3.json','manifest.json','plan.py','finite_copper.py','native_polygon.py']:
 f=R/'docs/electronics/remaining_power_return_plan_0208'/name;deps.append(dict(path=str(f.relative_to(R)),sha256=sha(f),bytes=f.stat().st_size))
(D/'dependencies.json').write_text(json.dumps(deps,indent=2)+'\n')
allow=[];excluded=[]
for f in sorted(D.rglob('*')):
 if not f.is_file():continue
 rel=f.relative_to(D);s=str(rel)
 if s=='manifest.json':continue
 if '__pycache__'in s or f.suffix=='.kicad_prl' or (s.startswith('replay/')and s!='replay/materialization.json') or (s.startswith('native_negative/') and f.name not in ['mainboard_revD.kicad_pcb','drc.json','drc.log']):excluded.append(s);continue
 allow.append(dict(path=s,sha256=sha(f),bytes=f.stat().st_size))
out=dict(status='FROZEN_RESEARCH_ONLY_NOFAB_NOPOWER',pcb_sha=m['pcb_sha'],files=allow,excluded=excluded);(D/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(files=len(allow),manifest_sha=sha(D/'manifest.json'),pcb_sha=m['pcb_sha']),indent=2))
