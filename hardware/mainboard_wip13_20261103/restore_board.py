"""Restore the exact reviewed PCB from small Git transport parts. Standard library only."""
from pathlib import Path
import base64,gzip,hashlib,json
P=Path(__file__).resolve().parent
M=json.loads((P/'board_transport/manifest.json').read_text())
parts=[]
for row in M['parts']:
 b=(P/'board_transport'/row['name']).read_bytes()
 if hashlib.sha256(b).hexdigest()!=row['sha256']:raise SystemExit('Transport part mismatch: '+row['name'])
 parts.append(b)
b=gzip.decompress(base64.b64decode(b''.join(parts),validate=True))
if len(b)!=M['native_bytes'] or hashlib.sha256(b).hexdigest()!=M['native_sha256']:raise SystemExit('Restored PCB hash/size mismatch')
out=P/'candidate/mainboard_revD.kicad_pcb'
if out.exists() and out.read_bytes()!=b:raise SystemExit('Refusing to overwrite a different local board; preserve your edits first.')
if not out.exists():out.write_bytes(b)
print('Exact reviewed PCB ready:',out.name,hashlib.sha256(b).hexdigest())
