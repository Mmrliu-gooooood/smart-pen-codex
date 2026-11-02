"""Fail closed if any pinned public source differs, also under Python -O."""
import hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
manifest=json.loads((root/'SOURCE.json').read_text())
for item in manifest['files']:
 raw=(root/'source'/item['path']).read_bytes()
 git=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 if git!=item['git_blob'] or hashlib.sha256(raw).hexdigest()!=item['sha256'] or len(raw)!=item['bytes']:
  raise SystemExit('Source mismatch: '+item['path'])
print(json.dumps({'commit':manifest['commit'],'exact_git_blobs':len(manifest['files']),'status':'PASS'}))
