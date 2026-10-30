"""Replay this review's fresh C results against generator grids, not fitted-matrix replay."""
from pathlib import Path
import os,json,math,hashlib
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get('PEN_BENCH_SOURCE',str(HERE.parent/'smart_pen_continuous_v3_target_benchmark_20261029'))).resolve()
actual=json.loads((HERE/'host_functional.json').read_text())['records'];raw=(SRC/'fixtures/independent_geometry.json').read_bytes();oracles=json.loads(raw);results=[]
for f in oracles['fixtures']:
 r=next(x for x in actual if x['fixture']==f['file'] and x['decoder']=='continuous_v3');assert r['status']==0 and r['directions']==f['upstream_directions'];assert [r['x'],r['y']]==f['paper_window']
 a=r['paper_to_frame'];b=r['frame_to_paper'];errs=[]
 for k,(u,v) in enumerate(f['independent_grid_centers_frame']):
  x=r['x']+k%6;y=r['y']+k//6;pu=a[0]*x+a[1]*y+a[2];pv=a[3]*x+a[4]*y+a[5]
  errs.append(math.hypot(pu-u,pv-v));assert errs[-1]<=f['tolerance_px']
  assert math.hypot(b[0]*pu+b[1]*pv+b[2]-x,b[3]*pu+b[4]*pv+b[5]-y)<1e-7
 results.append({'file':f['file'],'points':36,'max_synthetic_grid_error_pixels':max(errs),'tolerance_pixels':f['tolerance_px']})
assert len(results)==5
print(json.dumps({'generator_geometry_sha256':hashlib.sha256(raw).hexdigest(),'points':180,'results':results,'physical_accuracy':False},indent=2))
