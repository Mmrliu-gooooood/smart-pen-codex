"""Rebuild exact reviewed relative paths without duplicating stored evidence.
Usage: python reconstruct.py /absolute/new/writable/directory
Does not execute any recovered code or download data.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
here=Path(__file__).resolve().parent
repo=here.parents[1]
manifest=json.loads((here/'SOURCE_MAP.json').read_text())
def safe(root,rel):
 p=Path(rel)
 if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe path')
 return root/p
out=Path(sys.argv[1]).resolve()
if out.exists() and any(out.iterdir()):raise SystemExit('Choose a new empty destination')
out.mkdir(parents=True,exist_ok=True)
for e in manifest['files']:
 p=safe(repo,e['repository_path']);b=p.read_bytes() if p.is_file() else b''
 if hashlib.sha256(b).hexdigest()!=e['sha256'] and e['source']=='existing_f929':
  b=subprocess.check_output(['git','-C',str(repo),'show',manifest['base_commit']+':'+e['repository_path']])
 if len(b)!=e['bytes'] or hashlib.sha256(b).hexdigest()!=e['sha256']:raise RuntimeError('hash mismatch: '+e['original_path'])
 q=safe(out,e['original_path']);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
print('Verified and reconstructed',len(manifest['files']),'files; research only, NOFAB / NOPOWER')
