"""One-time source extraction; normal replay uses the included frozen geometry."""
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1];src=p.parent/'smart_pen_continuous_roi_v3_candidate_20261029/tests/fixtures/continuous';base=json.loads((src/'manifest.json').read_text());extended=json.loads((src/'extended_manifest.json').read_text());m=json.loads((p/'fixtures/manifest.json').read_text());rows=[]
for f in m['fixtures']:
 if f['expected_status']:continue
 if f['file'].startswith('fov'):
  r=next(r for r in base['fixtures'] if r['file']==f['file']);pitch=60/r['fov_mm'];x,y=f['x'],f['y'];directions=[r['directions'][yy-r['cell_top']][xx-r['cell_left']] for yy in range(y,y+6) for xx in range(x,x+6)];centers=[[pitch*(xx-r['ox_cells'])-.5,pitch*(yy-r['oy_cells'])-.5] for yy in range(y,y+6) for xx in range(x,x+6)];tol=.1*pitch
 else:
  r=next(r for r in extended if r['fixture']==f['file']);assert [r['x'],r['y']]==[f['x'],f['y']];directions=r['directions'];centers=r['grid_centers_frame'];tol=.1*60/r['fov']
 assert directions==f['directions'];rows.append(dict(file=f['file'],paper_window=[f['x'],f['y']],upstream_directions=directions,independent_grid_centers_frame=centers,tolerance_px=tol))
(p/'fixtures/independent_geometry.json').write_text(json.dumps(dict(upstream_commit=base['provenance']['upstream_commit'],note='Post-return upstream direction and rendering-grid oracle, never decoder input; extended rotation/scale positions come from independent renderer project().',source_hashes={x:hashlib.sha256((src/x).read_bytes()).hexdigest() for x in ['manifest.json','extended_manifest.json']},fixtures=rows),indent=2)+'\n')
