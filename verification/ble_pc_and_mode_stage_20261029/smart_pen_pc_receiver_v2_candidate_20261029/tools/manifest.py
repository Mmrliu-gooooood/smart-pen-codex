"""Freeze/verify this small deliverable, excluding caches and manifest itself."""
import argparse
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
manifest_path=root/'verification/MANIFEST.json'
def collect():
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and p!=manifest_path
            and '__pycache__' not in p.parts and p.suffix!='.pyc'}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write',action='store_true',help='explicitly freeze current reviewed candidate content')
args=parser.parse_args()
if args.write:
    manifest_path.write_text(json.dumps({'format':1,'candidate':'pc-ble-receiver-v2-20261029','files':collect()},indent=2)+'\n')
else:
    expected=json.loads(manifest_path.read_text())['files']
    actual=collect()
    if actual!=expected:
        changed=sorted(set(actual)^set(expected) | {p for p in set(actual)&set(expected) if actual[p]!=expected[p]})
        raise SystemExit('manifest mismatch: '+', '.join(changed))
print('MANIFEST PASS',hashlib.sha256(manifest_path.read_bytes()).hexdigest())
