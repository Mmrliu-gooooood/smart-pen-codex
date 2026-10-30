#!/usr/bin/env python3
"""Hash local public/frozen source only; never uploads or accesses a device."""
from pathlib import Path
import hashlib,json,sys
r=Path(__file__).resolve().parents[1]
manifest=r/'verification/source_manifest.json'
def files():
 for p in sorted(r.rglob('*')):
  if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts:continue
  rel=p.relative_to(r).as_posix()
  if rel.startswith('verification/') and rel not in {'verification/esp32-camera.patch','verification/frozen_headers.json','verification/RESULTS.zh-CN.md'}:continue
  yield rel,p
current={rel:hashlib.sha256(p.read_bytes()).hexdigest() for rel,p in files()}
if '--check' in sys.argv:
 expected=json.loads(manifest.read_text())['sha256']
 if current!=expected:
  changed=sorted(set(current)^set(expected)|{p for p in current.keys()&expected.keys() if current[p]!=expected[p]})
  raise SystemExit('manifest MISMATCH: '+repr(changed))
 print(f'PASS source manifest: {len(current)} files')
else:
 manifest.write_text(json.dumps({'candidate_revision':'v2','camera_upstream_commit':'f37e65608f709bd94846dee01d947f02ae07c0b0','idf_commit':'67c1de1eebe095d554d281952fde63c16ee2dca0','sha256':current},indent=2,ensure_ascii=False)+'\n')
 print(f'Wrote source manifest: {len(current)} files')
