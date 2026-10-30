"""Post-decode geometry oracle extracted from pinned upstream synthetic renderer metadata."""
from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parents[1];src=p.parent/'smart_pen_continuous_roi_candidate_20261028/tests/fixtures/continuous/manifest.json';source=json.loads(src.read_text());m=json.loads((p/'fixtures/manifest.json').read_text());rows=[]
for f in m['fixtures']:
 if f['expected_status']:continue
 r=next(r for r in source['fixtures'] if r['file']==f['file']);assert r['image_sha256']==f['pixel_sha256'];pitch=60/r['fov_mm'];x,y=f['x'],f['y']
 directions=[r['directions'][yy-r['cell_top']][xx-r['cell_left']] for yy in range(y,y+6) for xx in range(x,x+6)]
 centers=[[pitch*(xx-r['ox_cells'])-.5,pitch*(yy-r['oy_cells'])-.5] for yy in range(y,y+6) for xx in range(x,x+6)]
 rows.append(dict(file=f['file'],paper_window=[x,y],upstream_directions=directions,independent_grid_centers_frame=centers,tolerance_px=.1*pitch,render_metadata={k:r[k] for k in ['fov_mm','ox_cells','oy_cells','phase']}))
(p/'fixtures/independent_geometry.json').write_text(json.dumps(dict(source_manifest_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),upstream_commit=source['provenance']['upstream_commit'],provenance=source['provenance'],note='Synthetic upstream encoded paper only. Centers use p*(paper-origin)-0.5, NOT output fitted transform. Post-decode oracle never enters C.',fixtures=rows),indent=2)+'\n')
