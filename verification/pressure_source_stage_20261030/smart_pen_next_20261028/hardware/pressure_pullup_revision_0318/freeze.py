from pathlib import Path
import json,hashlib
from materialize import D,BASE,req
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
deps=[]
for folder in [BASE.parent,D.parents[1]/'docs/electronics/pressure_contract_audit_0312']:
 m=folder/'manifest.json';rows=json.loads(m.read_text());rows=rows['files'] if isinstance(rows,dict) else rows
 for x in rows:
  p=folder/x['path'];req(p.is_file() and sha(p)==x['sha256'] and p.stat().st_size==x['size'],'frozen dependency '+str(p))
 deps.append(dict(path=str(folder.relative_to(D.parents[1])),manifest_sha256=sha(m),files_verified=len(rows)))
(D/'dependencies.json').write_text(json.dumps(deps,indent=2)+'\n')
req((D/'BOM.csv').read_bytes()==(D/'checks/candidate/bom.csv').read_bytes(),'BOM copy')
rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p==D/'manifest.json':continue
 rows.append(dict(path=str(p.relative_to(D)),size=p.stat().st_size,sha256=sha(p)))
(D/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(dict(manifest_sha256=sha(D/'manifest.json'),files=len(rows),dependencies=deps),indent=2))
