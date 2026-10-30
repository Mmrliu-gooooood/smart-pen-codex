"""Compare actual host replay outputs with independent rendering geometry; no timing."""
from pathlib import Path
import json,math
p=Path(__file__).resolve().parents[1];actual=json.loads((p/'verification/host-functional.json').read_text())['records'];oracles=json.loads((p/'fixtures/independent_geometry.json').read_text());out=[]
for f in oracles['fixtures']:
 r=next(r for r in actual if r['fixture']==f['file'] and r['decoder']=='continuous_v3');assert r['directions']==f['upstream_directions'];assert [r['x'],r['y']]==f['paper_window'];a=r['paper_to_frame'];b=r['frame_to_paper'];x,y=f['paper_window'];errors=[];inverse=[]
 for i,(u,v) in enumerate(f['independent_grid_centers_frame']):
  xx=x+i%6;yy=y+i//6;pu=a[0]*xx+a[1]*yy+a[2];pv=a[3]*xx+a[4]*yy+a[5];errors.append(math.hypot(pu-u,pv-v));inverse.append(math.hypot(b[0]*pu+b[1]*pv+b[2]-xx,b[3]*pu+b[4]*pv+b[5]-yy))
 assert max(errors)<=f['tolerance_px'];assert max(inverse)<1e-7
 out.append(dict(fixture=f['file'],exact_36_upstream_symbols=True,max_grid_center_error_px=max(errors),limit_px=f['tolerance_px'],max_inverse_error_cells=max(inverse)))
print(json.dumps(dict(scope='Independent ideal synthetic geometry only; no physical accuracy claim',records=out),indent=2))
