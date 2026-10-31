from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
m=json.loads((r/'DEPENDENCIES.json').read_text())
bad=[]
for rel,expected in m['sha256'].items():
 p=r.parent/rel
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:bad.append(rel)
if bad:raise SystemExit('DEPENDENCY MISMATCH: '+repr(bad))
print(f"PASS {len(m['sha256'])} exact external dependency hashes")
