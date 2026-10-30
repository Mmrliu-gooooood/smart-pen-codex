from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;O=D.parent/'mcu_power_ground_candidate_0043';R=D.parents[1]
def entry(p,root):return {'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
# First candidate is retained only as manufacturing-negative evidence.
old_names=['README.md','dependencies.json','materialize.py','materialization.json','materialize.log','verify.py','verification.json','verification_optimized.json','verify.log','verify_optimized.log','finite_copper.py','native_polygon.py','drc.json','drc.log','drc.exit','REJECTED_pointer_repr_verify.log','REJECTED_expected_ground_count.log','REJECTED_multi_load_api.log']
old_files=[O/n for n in old_names]+[p for p in (O/'native').rglob('*')if p.is_file()and p.suffix!='.kicad_prl']
(O/'EXCLUSIONS.json').write_text(json.dumps({'excluded':['native/*.kicad_prl','negative_native/**','negative*.json/log/scripts: incomplete exploratory API output, superseded by0109 exact counterfactuals','__pycache__/**'],'status':'REJECTED_C504_SAME_NET_DRILL_PAD_OVERLAP'},indent=2)+'\n');old_files.append(O/'EXCLUSIONS.json');oldrows=[entry(p,O)for p in sorted(set(old_files))];(O/'manifest.json').write_text(json.dumps({'status':'REJECTED_RESEARCH_INPUT_NOT_FAB','files':oldrows},indent=2)+'\n')
# Main successor: allowlisted root evidence, native sources, and counterfactual DRC only.
newfiles=[p for p in D.iterdir()if p.is_file()and p.name not in['manifest.json','EXCLUSIONS.json']and p.suffix in['.py','.json','.log','.md','.png','.exit']]
newfiles+=[p for p in (D/'native').rglob('*')if p.is_file()and p.suffix!='.kicad_prl']
newfiles+=[p for p in (D/'counterfactual_native').glob('*/drc.*')if p.is_file()]
(D/'EXCLUSIONS.json').write_text(json.dumps({'excluded':['native/*.kicad_prl','counterfactual_native/*/native source copies other than retainedDRC reports','replay/native/**','__pycache__/**'],'reason':'Duplicate native sources reproducible byscripts; no claimed completed product','authority':'READ_ONLY frozen research files; native0/181/0 remainsNOFAB'},indent=2)+'\n');newfiles.append(D/'EXCLUSIONS.json');rows=[entry(p,D)for p in sorted(set(newfiles))];(D/'manifest.json').write_text(json.dumps({'status':'NOFAB_RESEARCH_NOT_MANUFACTURING_RELEASE','files':rows},indent=2)+'\n')
for root in [O,D]:
 data=json.loads((root/'manifest.json').read_text())
 for x in data['files']:
  p=root/x['path']
  if p.stat().st_size!=x['bytes']or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:raise RuntimeError('freeze mismatch')
 print(root.name,len(data['files']),hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest())
