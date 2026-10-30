from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;W=D.parents[2];Q=D.parents[1]/'docs/electronics/mcu_supply_access_study_0242'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def req(c,s):
 if not c:raise RuntimeError(s)
deps=json.loads((Q/'dependencies.json').read_text())
for d in deps:
 p=W/d['path'];req(p.stat().st_size==d['size']and sha(p)==d['sha256'],'dependency changed '+str(p))
for p in [Q/'manifest.json',Q/'two_vias.json',Q/'mechanics.json',Q/'check_model.json']:
 deps.append(dict(path=str(p.relative_to(W)),size=p.stat().st_size,sha256=sha(p)))
req(sha(Q/'manifest.json')=='596bc4a249bec1d935ebc66690e262c74ac3b250a8b9db690c942e6066e8b41a','frozen study manifest')
for d in json.loads((Q/'manifest.json').read_text())['files']:
 p=Q/d['path'];req(p.stat().st_size==d['size']and sha(p)==d['sha256'],'frozen study file changed '+str(p))
req((D/'native/mainboard_revD.kicad_pcb').read_bytes()==(D/'replay/native/mainboard_revD.kicad_pcb').read_bytes(),'replay exact')
req(sha(D/'native_negative/rollback/mainboard_revD.kicad_pcb')=='66d5343409eaf0cf58458759f033e9eea74865e1ea85b83ecc0c3068d2032141','rollback exact')
req((D/'verification.json').read_bytes()==(D/'verification_optimized.json').read_bytes(),'verification optimized')
req((D/'negative.json').read_bytes()==(D/'negative_optimized.json').read_bytes(),'negative optimized')
req((D/'mechanics_linked.json').read_bytes()==(Q/'mechanics.json').read_bytes(),'mechanical evidence exact')
(D/'dependencies.json').write_text(json.dumps(deps,indent=2)+'\n')
(D/'reproducibility.json').write_text(json.dumps(dict(replay_board_byte_exact=True,rollback_board_byte_exact=True,normal_optimized_verification_exact=True,normal_optimized_native_negatives_exact=True,original_dependencies_unchanged=True,original_mechanics_evidence_byte_exact=True,status='NOFAB_NOPOWER_RESEARCH_COURTYARD_AND_ESCAPE_GATES_OPEN'),indent=2)+'\n')
rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file()or '__pycache__'in p.parts or p.name=='manifest.json':continue
 rows.append(dict(path=str(p.relative_to(D)),size=p.stat().st_size,sha256=sha(p)))
(D/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows),sha(D/'manifest.json'))
