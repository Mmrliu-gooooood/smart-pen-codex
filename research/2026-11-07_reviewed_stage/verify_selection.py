#!/usr/bin/env python3
"""Verify selected publication bytes. No engineering execution or file writes."""
import hashlib
import json
from pathlib import Path, PurePosixPath

here = Path(__file__).resolve().parent
root = here.parents[1]
manifest = json.loads((here / 'PUBLICATION_MANIFEST.json').read_text())
seen = set()
for row in manifest['files']:
    rel = PurePosixPath(row['path'])
    if rel.is_absolute() or '..' in rel.parts or row['path'] in seen:
        raise SystemExit('Unsafe or repeated path')
    seen.add(row['path'])
    path = root / rel
    if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise SystemExit('Symlink path is not allowed: '+row['path'])
    if not path.is_file():
        raise SystemExit('Missing regular file: '+row['path'])
    data = path.read_bytes()
    if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
        raise SystemExit('Content identity mismatch: '+row['path'])
print(json.dumps({'status':'SELECTED_PUBLICATION_BYTES_PASS','files':len(seen),
 'base_commit':manifest['base_commit'],'writes':False,'engineering_rerun':False,
 'NOFAB':True,'NOPOWER':True,'commission':'OPEN','qualification':None,
 'current_rating_A':None,'effective_C':None},sort_keys=True))
