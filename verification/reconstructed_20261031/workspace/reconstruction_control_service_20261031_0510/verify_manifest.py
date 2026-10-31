from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;m=json.loads((D/'review_manifest.json').read_text());errors=[]
for q in m['files']:
 f=D/q['path']
 if not f.is_file()or f.stat().st_size!=q['bytes']or hashlib.sha256(f.read_bytes()).hexdigest()!=q['sha256']:errors.append(q['path'])
if errors:raise RuntimeError(errors)
print(len(m['files']),'allowlisted files exact;',m['status'])
