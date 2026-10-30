"""Materialize three missing no-fit regression images without rerunning sweeps."""
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent
ns={'__file__':str(p/'boundary_diagnostic.py')};exec((p/'boundary_diagnostic.py').read_text().split('for old in original:')[0],ns)
a=json.loads((p/'results.json').read_text());b=json.loads((p/'boundary_results.json').read_text());fixtures=[]
for r in a:
 if 'fixture' in r:fixtures.append(dict(r,preprocessing='none'))
for r in json.loads((p/'boundary_fixture_oracles.json').read_text()):fixtures.append(dict(r,preprocessing='diagnostic_border_components_removed'))
for group,fov,size,phase,filtered in ((a,7,96,26,False),(b,7,96,5,True),(b,5,80,1,True)):
 r=next(r for r in group if (r['fov_mm'],r['size'],r['phase'])==(fov,size,phase));full=ns['render'](fov,r['ox_cells'],r['oy_cells']);start=(200-size)//2;im=full[start:start+size,start:start+size]
 if filtered:im,_=ns['edge_filter'](im)
 assert hashlib.sha256(im.tobytes()).hexdigest()==r['image_sha256']
 name=f'{"edge_filtered_" if filtered else ""}fov{fov}_roi{size}_phase{phase}.pgm';(p/name).write_bytes(f'P5\n{size} {size}\n255\n'.encode()+im.tobytes());fixtures.append(dict(r,fixture=name,preprocessing='diagnostic_border_components_removed' if filtered else 'none'))
(p/'regression_manifest.json').write_text(json.dumps({'decoder_commit':'685d7bdbf8d62ca9ff30e87740e9d9a0e4ce4d00','paper_config':[710,1000,10,2],'note':'Frozen current-decoder status oracle, not desired fixed-decoder coverage. A repair may intentionally improve rejection statuses; never permit incorrect OK. Synthetic only.','fixtures':fixtures},indent=2))
