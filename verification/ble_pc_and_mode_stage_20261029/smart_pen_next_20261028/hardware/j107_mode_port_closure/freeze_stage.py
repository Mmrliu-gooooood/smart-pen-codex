from pathlib import Path
import json,hashlib,shutil
D=Path(__file__).resolve().parent
if(D/'manifest.json').exists():raise RuntimeError('Already frozen')
for a,z in [('audit_normal.json','audit_optimized.json'),('j107_audit.json','j107_audit_optimized.json'),('ground_tail_counterfactual.json','ground_tail_counterfactual_optimized.json'),('local_plane_corridors.json','local_plane_corridors_optimized.json')]:
 if json.loads((D/a).read_text())!=json.loads((D/z).read_text()):raise RuntimeError('Mode mismatch '+a)
for n in ['negative_j107.json','source_refill.json','replay_audit.json','drc_delta.json']:json.loads((D/n).read_text())
if(D/'preflight.exit').read_text().strip()!='5':raise RuntimeError('Expected unresolved full DRC exit5')
if(D/'guard_boards').exists():shutil.rmtree(D/'guard_boards')
for p in D.rglob('*.kicad_prl'):p.unlink()
files={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(D.rglob('*'))if p.is_file()and p.name!='manifest.json'}
m={'status':'J107_THREE_MODE_PORT_PADS_CLOSED_NOFAB_PENDING_INDEPENDENT_REVIEW','input_pcb_sha256':'1c4907d04a2bf2dea3a53f89266bc49c0cb96a0683b4898b58cd36b6525ec16d','pcb_sha256':hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'fresh_xml_sha256':hashlib.sha256((D/'fresh.xml').read_bytes()).hexdigest(),'excluded':'Generated guard/replay/mutation fixtures and PRL; dependencies referenced by hash','files':files};(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
for n,h in files.items():
 if hashlib.sha256((D/n).read_bytes()).hexdigest()!=h:raise RuntimeError('Concurrent change '+n)
print(json.dumps({'files':len(files),'manifest_sha256':hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest(),'pcb_sha256':m['pcb_sha256'],'fresh_xml_sha256':m['fresh_xml_sha256']},indent=2))
