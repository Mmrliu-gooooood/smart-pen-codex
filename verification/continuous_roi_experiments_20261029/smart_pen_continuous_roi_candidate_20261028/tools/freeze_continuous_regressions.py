"""Freeze supplemental pixel fixtures/oracles from explicit synthetic conditions.
This tool does not modify decoder code or select its runtime ROI policy.
"""
from pathlib import Path
import ctypes as C
import hashlib
import json
import numpy as np
from continuous_roi_sweep import ROOT,ContinuousROI,project,render,evaluate

def main():
 audit=ROOT.parent/'smart_pen_viewport_audit_20261028';out=ROOT/'tests/fixtures/continuous'
 old=json.loads((audit/'results.json').read_text());base=next(r for r in old if r['fov_mm']==6 and r['phase']==0 and r['size']==200)
 dirs=np.load(audit/'upstream_directions.npy');origin=dict(ox=base['ox_cells'],oy=base['oy_cells'],fov=6)
 cases=[dict(name='rot14',angle=14),dict(name='rot45',angle=45),dict(name='fov55',fov=5.5),dict(name='fov51',fov=5.1),
        dict(name='blur08',blur=.8),dict(name='blur16',fov=7,blur=1.6),dict(name='long_ink',damage='stroke',must_reject=True),
        dict(name='fake_dots',seed=0,must_reject=True),dict(name='shear35',shear=.35),dict(name='dense9',fov=9,must_reject=True)]
 ContinuousROI.setUpClass();ws=(C.c_double*((ContinuousROI.ws_size+7)//8))();manifest=[]
 try:
  for changes in cases:
   s={**origin,**changes};source=dirs
   if s['name']=='fake_dots':source=np.random.default_rng(s['seed']).integers(0,4,dirs.shape,dtype=np.uint8)
   im=render(source,s);record=evaluate(ContinuousROI.lib,ws,im,s,dirs)
   assert record['status']!=0 or record['correct'],record
   file='extended_'+s['name']+'.pgm';(out/file).write_bytes(b'P5\n200 200\n255\n'+im.tobytes())
   record['fixture']=file
   if record['status']==0:
    x,y=record['x'],record['y'];record['directions']=dirs[y:y+6,x:x+6].reshape(-1).tolist()
    record['grid_centers_frame']=[[u-.5,v-.5] for yy in range(y,y+6) for xx in range(x,x+6) for u,v in [project(xx,yy,s)]]
   manifest.append(record)
 finally:ContinuousROI.tearDownClass()
 (out/'extended_manifest.json').write_text(json.dumps(manifest,indent=2))
 print([(r['fixture'],r['status']) for r in manifest])
if __name__=='__main__':main()
