from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
def row(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
paths=['hardware/sens_tree_candidate_0158/manifest.json','hardware/sens_tree_candidate_0158/native/mainboard_revD.kicad_pcb','hardware/sens_tree_candidate_0158/verification.json','hardware/sens_tree_candidate_0158/drc.json','hardware/translator_domain_candidate_0130/manifest.json','hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb','docs/electronics/MAINBOARD_RECOVERY_20261030_0203.md']
(D/'dependencies.json').write_text(json.dumps([row(R/p,R)for p in paths],indent=2)+'\n')
files=[p for p in D.iterdir()if p.is_file()and p.name!='manifest.json'];(D/'manifest.json').write_text(json.dumps(dict(status='READ_ONLY_RECOVERY_INDEX_143_UNCONNECTED_NOFAB_NOT_FORMAL_BASELINE',excluded=['__pycache__/**'],files=[row(p,D)for p in sorted(files)]),indent=2)+'\n');print(len(files),hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest())
