from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent; R=D.parents[1]
def row(p,base):
 b=p.read_bytes();return dict(path=str(p.relative_to(base)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
deps=[]
for rel in ['hardware/aon_entry_bridge_candidate_2156/native','hardware/j202_low_speed_reference_candidate/native','hardware/head_power_joint_native_candidate_2141/native','hardware/gnd_fixed_branch_candidate_2159/native']:
 for p in sorted((R/rel).rglob('*')):
  if p.is_file()and p.suffix not in ['.kicad_prl','.pyc']:deps.append(row(p,R))
for rel in ['hardware/aon_entry_bridge_candidate_2156/analysis.json','hardware/aon_entry_bridge_candidate_2156/manifest.json','hardware/j202_low_speed_reference_candidate/manifest.json','hardware/head_power_joint_native_candidate_2141/verify_normal.json','hardware/gnd_fixed_branch_candidate_2159/plan.json','hardware/gnd_fixed_branch_candidate_2159/neck.json']:
 deps.append(row(R/rel,R))
(D/'dependencies.json').write_text(json.dumps(dict(root='smart_pen_next_20261028',note='Exact files for full replay and comparative studies; rejected 2159 native is only for comparison, never promoted.',files=deps),indent=2)+'\n')
(D/'EXCLUSIONS.json').write_text(json.dumps(dict(exclude=['**/__pycache__/**','**/*.pyc','**/*.kicad_prl','manifest.json'],note='Rejected diagnostic text/JSON are explicitly retained and named; no firmware or executable binary included.'),indent=2)+'\n')
files=[row(p,D)for p in sorted(D.rglob('*'))if p.is_file()and p.name!='manifest.json'and '__pycache__'not in p.parts and p.suffix not in ['.pyc','.kicad_prl']]
(D/'manifest.json').write_text(json.dumps(dict(status='FROZEN_LIMITED_CONSERVATIVE_GND_RESEARCH_NOFAB_PENDING_INDEPENDENT_REVIEW',files=files),indent=2)+'\n')
for x in files:
 p=D/x['path'];assert p.stat().st_size==x['size']and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
print(json.dumps(dict(files=len(files),manifest_sha256=hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),pcb_sha256=hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),dependencies=len(deps)),indent=2))
