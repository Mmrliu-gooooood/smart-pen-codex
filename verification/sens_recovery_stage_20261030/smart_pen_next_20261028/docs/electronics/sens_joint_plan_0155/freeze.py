from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
def row(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
files=[R/'hardware/translator_domain_candidate_0130/manifest.json',R/'hardware/translator_domain_candidate_0130/native/mainboard_revD.kicad_pcb',R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb']
(D/'dependencies.json').write_text(json.dumps([row(p,R)for p in files],indent=2)+'\n')
files=[p for p in D.iterdir()if p.is_file()and p.name!='manifest.json']
(D/'manifest.json').write_text(json.dumps(dict(status='ONE_READ_ONLY_TREE_GEOMETRY_PASS_NATIVE_PENDING_NOFAB',excluded=['__pycache__/**'],files=[row(p,D)for p in sorted(files)]),indent=2)+'\n')
print(len(files),hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest())
