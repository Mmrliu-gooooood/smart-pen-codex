from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if (D/'check.json').read_bytes()!=(D/'check_optimized.json').read_bytes():raise RuntimeError('optimized')
base=R/'hardware/gate_power_candidate_0228/native/mainboard_revD.kicad_pcb'
if sha(base)!='66d5343409eaf0cf58458759f033e9eea74865e1ea85b83ecc0c3068d2032141':raise RuntimeError('base')
deps=[]
for f in sorted(base.parent.rglob('*')):
 if f.is_file()and f.suffix!='.kicad_prl':deps.append(dict(path=str(f.relative_to(R)),sha256=sha(f),bytes=f.stat().st_size))
(D/'dependencies.json').write_text(json.dumps(deps,indent=2)+'\n')
files=[dict(path=f.name,sha256=sha(f),bytes=f.stat().st_size)for f in sorted(D.iterdir())if f.is_file()and f.name!='manifest.json'];(D/'manifest.json').write_text(json.dumps(dict(status='READ_ONLY_TWO_REJECTED_HYPOTHESES_NO_NATIVE_CHANGES',files=files),indent=2)+'\n');print(len(files),sha(D/'manifest.json'))
