"""Post-hoc oracle geometry diagnostic ONLY; no values enter decoder."""
import json, numpy as np, math, sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
sys.path[:0]=[str(P/'source/tools'),str(P/'source/tests')]
from continuous_roi_sweep import project
D=np.load(P.parent/'smart_pen_viewport_audit_20261028/upstream_directions.npy')
rows=[]
for s in json.loads((P/'baseline_eight.json').read_text()):
 side=80 if s['camera_tilt_deg']==30 and s['phase']==17 else 96;lo=(200-side)/2;hi=lo+side
 cx=s['ox']+10;cy=s['oy']+10;q=[];p=[]
 for yy in range(math.floor(cy)-20,math.ceil(cy)+20):
  for xx in range(math.floor(cx)-20,math.ceil(cx)+20):
   dx,dy=((0,-1),(-1,0),(1,0),(0,1))[D[yy,xx]];x=xx+dx/6;y=yy+dy/6
   corners=[project(x+rx,y+ry,s) for rx in (-1/6,1/6) for ry in (-1/6,1/6)]
   if all(lo+1<u<hi-1 and lo+1<v<hi-1 for u,v in corners):q.append((x-cx,y-cy,1));p.append(project(x,y,s))
 q=np.array(q);p=np.array(p);aff=np.linalg.lstsq(q,p,rcond=None)[0];err=np.linalg.norm(q@aff-p,axis=1)
 # General affine lower-bound on squared geometric error, broader than orthogonal V3.
 rows.append(dict(tilt=s['camera_tilt_deg'],phase=s['phase'],side=side,ideal_dots=len(q),general_affine_rms_px=float(np.sqrt(np.mean(err**2))),general_affine_max_px=float(max(err)),note='Oracle-labelled ideal centers; not detector centroids or an algorithm initializer.'))
(P/'model_diagnostics.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
