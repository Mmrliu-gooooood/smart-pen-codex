from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
for x in json.loads((D/'dependencies.json').read_text()):
 b=(R/x['path']).read_bytes()
 if len(b)!=x['bytes']or hashlib.sha256(b).hexdigest()!=x['sha256']:raise RuntimeError('input changed '+x['path'])
if (D/'check.json').read_bytes()!=(D/'check_optimized.json').read_bytes():raise RuntimeError('normal/O mismatch')
files=['README.md','plan.py','check.py','finite_copper.py','native_polygon.py','first.json','alternatives.json','gate2.json','gate3.json','check.json','check_optimized.json','source_targets.json','dependencies.json','rejected_assumptions.json','draw.py','plan_view.png','freeze.py']
rows=[]
for f in files:
 b=(D/f).read_bytes();rows.append(dict(path=f,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(D/'manifest.json').write_text(json.dumps(dict(status='READ_ONLY_GATE_MODEL_NO_NATIVE_NOFAB',files=rows,excluded=['__pycache__','gate2_check_superseded.json']),indent=2)+'\n')
print(json.dumps(dict(files=len(rows),manifest_sha=hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),input_dependencies=len(json.loads((D/'dependencies.json').read_text())))))
