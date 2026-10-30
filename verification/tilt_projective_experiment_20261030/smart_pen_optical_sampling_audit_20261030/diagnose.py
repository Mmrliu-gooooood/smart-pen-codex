"""Read-only frozen-source diagnostic; ideal pinhole, not measured optics."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys, json, math, hashlib, ctypes as C
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE/'smart_pen_continuous_roi_v3_candidate_20261029'
sys.dont_write_bytecode=True
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
import continuous_roi_sweep as sweep
OUT=Path(__file__).resolve().parent
# P=.3mm; Z=12mm from pinhole to central paper intersection. fpx=400.
# Paper coords X,Y: camera coordinates (X,Y cos(theta),Z+Y sin(theta)).
# Hence pitch=fpx*P/Z=10; ratio=cos(theta); perspective_y=P*sin(theta)/Z.
# This is camera optical-axis tilt from paper normal, NOT pen-axis angle.
files={}
for root,manifest in [(ROOT,ROOT/'verification/V3_SNAPSHOT.json'),(BASE/'smart_pen_camera_capture_v2_candidate_20261029',BASE/'smart_pen_camera_capture_v2_candidate_20261029/verification/source_manifest.json')]:
    obj=json.loads(manifest.read_text()); expected={r['path']:r['sha256'] for r in obj['files']} if 'files' in obj else obj['sha256']
    for rel,h in expected.items():
        assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h,rel
    files[str(manifest.relative_to(BASE))]={'sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'verified_files':len(expected)}
dirs=np.load(BASE/'smart_pen_viewport_audit_20261028/upstream_directions.npy')
old=json.loads((BASE/'smart_pen_viewport_audit_20261028/results.json').read_text())
origins={r['phase']:r for r in old if r['size']==200 and r['fov_mm']==6}
sweep.ContinuousROI.setUpClass(); lib=sweep.ContinuousROI.lib;ws=(C.c_double*((sweep.ContinuousROI.ws_size+7)//8))()
results=[]
try:
 for theta in (0,30,45,60):
  for phase in (0,17):
   ref=origins[phase];s=dict(fov=6,ox=ref['ox_cells'],oy=ref['oy_cells'],ratio=math.cos(math.radians(theta)),perspective_y=.3*math.sin(math.radians(theta))/12,phase=phase,camera_tilt_deg=theta,Z_mm=12,focal_pixels=400)
   im=sweep.render(dirs,s);rec=sweep.evaluate(lib,ws,im,s,dirs);rec.pop('seconds',None)
   # Oracle-only count of complete 6x6 dot supports inside each centered crop,
   # with 4px guard; no truth goes into C. Project circumscribed squares.
   counts={}
   for side in (96,80):
    lo=(200-side)/2+4;hi=(200+side)/2-4;complete=0
    cx=s['ox']+10;cy=s['oy']+10
    for y in range(math.floor(cy)-15,math.ceil(cy)+15):
     for x in range(math.floor(cx)-15,math.ceil(cx)+15):
      good=True
      for yy in range(y,y+6):
       for xx in range(x,x+6):
        dx,dy=((0,-1),(-1,0),(1,0),(0,1))[dirs[yy,xx]]
        for rx,ry in ((-1/6,-1/6),(-1/6,1/6),(1/6,-1/6),(1/6,1/6)):
         u,v=sweep.project(xx+dx/6+rx,yy+dy/6+ry,s)
         if not(lo<=u<hi and lo<=v<hi):good=False;break
        if not good:break
       if not good:break
      complete+=good
    counts[str(side)]=complete
   rec['oracle_complete_windows_4px_guard']=counts;results.append(rec)
   (OUT/f'tilt{theta}_phase{phase}.pgm').write_bytes(b'P5\n200 200\n255\n'+im.tobytes())
   print(theta,phase,rec['status'],rec.get('correct'),rec.get('transform_max_error_px'),flush=True)
finally:sweep.ContinuousROI.tearDownClass()
files['renderer']={'path':str((ROOT/'tools/continuous_roi_sweep.py').relative_to(BASE)),'sha256':hashlib.sha256((ROOT/'tools/continuous_roi_sweep.py').read_bytes()).hexdigest()}
(OUT/'results.json').write_text(json.dumps({'synthetic_only':True,'manifest_verification':files,'cases':results},indent=2)+'\n')
