import sys,json,ctypes as C
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent; R=P/'source';sys.dont_write_bytecode=True
sys.path[:0]=[str(R/'tools'),str(R/'tests')]
import continuous_roi_sweep as s
D=np.load(P.parent/'smart_pen_viewport_audit_20261028/upstream_directions.npy')
old=json.loads((P.parent/'smart_pen_optical_sampling_audit_20261030/results.json').read_text())['cases']
s.ContinuousROI.setUpClass();ws=(C.c_double*((s.ContinuousROI.ws_size+7)//8))();rows=[]
try:
 for r in old:
  p=P.parent/'smart_pen_optical_sampling_audit_20261030'/f'tilt{r["camera_tilt_deg"]}_phase{r["phase"]}.pgm';im=np.frombuffer(p.read_bytes().split(b'\n',3)[3],np.uint8).reshape(200,200)
  spec={k:r[k] for k in ('fov','ox','oy','ratio','perspective_y','phase','camera_tilt_deg','Z_mm','focal_pixels')}
  z=s.evaluate(s.ContinuousROI.lib,ws,im,spec,D);z['frozen_status']=r['status'];rows.append(z);print(z['camera_tilt_deg'],z['phase'],z['status'],z.get('correct'),flush=True)
finally:s.ContinuousROI.tearDownClass()
(P/(sys.argv[1] if len(sys.argv)>1 else 'baseline_eight.json')).write_text(json.dumps(rows,indent=2)+'\n')
