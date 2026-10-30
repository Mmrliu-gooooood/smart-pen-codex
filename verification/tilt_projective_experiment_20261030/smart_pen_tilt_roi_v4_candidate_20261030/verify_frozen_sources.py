"""Check original V3 snapshot and unchanged legacy files copied into this experiment."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;original=P.parent/'smart_pen_continuous_roi_v3_candidate_20261029'
m=json.loads((original/'verification/V3_SNAPSHOT.json').read_text())
for row in m['files']:
 for root in (original,P/'source'):
  assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],str(root/row['path'])
print(f'PASS {len(m["files"])} original frozen files and copied legacy files unchanged')
