"""Reconstruct byte-exact original aliases from a checkout plus optional draft overlay.
python reconstruct.py REPOSITORY NEW_EMPTY_DEST [PAYLOAD_OVERLAY]
Run checks only in the reconstruction, never frozen repository snapshots.
"""
from pathlib import Path
import json,hashlib,sys
here=Path(__file__).resolve().parent
repo=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve()
overlay=Path(sys.argv[3]).resolve() if len(sys.argv)>3 else None
if dest.exists():raise SystemExit('destination must not exist')
rows=json.loads((here/'SOURCE_MAP.json').read_text())
for r in rows:
 for key in ('original_path','repo_path'):
  p=Path(r[key])
  if p.is_absolute() or '..' in p.parts:raise SystemExit('unsafe path')
 p=repo/r['repo_path']
 if overlay and (overlay/r['repo_path']).is_file():p=overlay/r['repo_path']
 data=p.read_bytes()
 if len(data)!=r['bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256']:raise SystemExit('hash mismatch '+r['repo_path'])
 out=dest/r['original_path'];out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
print(json.dumps({'reconstructed':len(rows),'bytes':sum(r['bytes'] for r in rows),'all_sha256_verified':True}))
