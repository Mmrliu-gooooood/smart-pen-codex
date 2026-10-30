from pathlib import Path
import json,hashlib,shutil
D=Path(__file__).resolve().parent
if (D/'manifest.json').exists():raise RuntimeError('Already frozen: refuse overwrite manifest')
for name in ['audit_normal.json','audit_optimized.json','maintenance_audit.json','maintenance_audit_optimized.json','maintenance_negatives.json','source_refill.json','replay_audit.json']:
 json.loads((D/name).read_text())
if json.loads((D/'audit_normal.json').read_text())!=json.loads((D/'audit_optimized.json').read_text()):raise RuntimeError('Audit modes differ')
if json.loads((D/'maintenance_audit.json').read_text())!=json.loads((D/'maintenance_audit_optimized.json').read_text()):raise RuntimeError('Maintenance modes differ')
if (D/'preflight.exit').read_text().strip()!='5':raise RuntimeError('Expected unresolved native exit5')
# Delete generated destructive/replay fixtures only; authoritative native untouched.
if(D/'guard_boards').exists():shutil.rmtree(D/'guard_boards')
for p in D.rglob('*.kicad_prl'):p.unlink()
files={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(D.rglob('*'))if p.is_file()and p.name!='manifest.json'}
m={'status':'CAM_ON_ONLY_PATH_MAINTENANCE_NOFAB_PENDING_INDEPENDENT_REVIEW','input':'508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35','pcb_sha256':hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'excluded':'Generated guard fixtures and PRL; immutable dependencies hash-bound separately','files':files};(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
for name,h in files.items():
 if hashlib.sha256((D/name).read_bytes()).hexdigest()!=h:raise RuntimeError('Concurrent file change '+name)
print(json.dumps({'files':len(files),'manifest_sha256':hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),'pcb_sha256':m['pcb_sha256']},indent=2))
