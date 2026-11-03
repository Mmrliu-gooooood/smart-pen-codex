from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
M=json.loads((Path(__file__).with_name('sources.json')).read_text())
for name,h in M.items():
 p=ROOT/name
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:
  raise SystemExit('Source mismatch: '+name)
d=json.loads((Path(__file__).with_name('drc.json')).read_text())
if len(d.get('violations',[]))!=0 or len(d.get('unconnected_items',[]))!=13:
 raise SystemExit('DRC snapshot count mismatch')
print('Source integrity and bound historical DRC snapshot validated; not a fresh DRC/MCAD run.')
