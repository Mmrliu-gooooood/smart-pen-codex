"""Current-pixel corrupt-code/transform/contradictory-window probes; no priors."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ctypes as C
import json
import numpy as np
from continuous_roi_sweep import ROOT,ContinuousROI,render,evaluate
sys.path.insert(0,str(ROOT/'tests'))
from roi_opt_fixture import Render,render as isolated_render

def main():
 out=ROOT/'verification/v3_adversarial';out.mkdir(exist_ok=True)
 audit=ROOT.parent/'smart_pen_viewport_audit_20261028';dirs=np.load(audit/'upstream_directions.npy')
 old=json.loads((audit/'results.json').read_text());cases=[]
 for fov in (5,6,7):
  for phase in (0,17):
   base=next(x for x in old if x['fov_mm']==fov and x['phase']==phase and x['size']==200)
   for angle in (0,14):
    for kind in ('one_plus1','one_plus2','one_plus3','two_changed','block3x3'):
     cases.append(dict(group='corrupt_code',fov=fov,ox=base['ox_cells'],oy=base['oy_cells'],phase=phase,angle=angle,kind=kind))
  base=next(x for x in old if x['fov_mm']==fov and x['phase']==0 and x['size']==200)
  for kind in ('mirror','quarter_turn'):
   cases.append(dict(group='canonical_negative',fov=fov,ox=base['ox_cells'],oy=base['oy_cells'],kind=kind,must_reject=True))
 cases.extend([dict(group='two_windows',fov=7.5,ox=113.,oy=230.,kind='agree'),dict(group='two_windows',fov=7.5,ox=113.,oy=230.,kind='conflict',must_reject=True)])
 ContinuousROI.setUpClass();ws=(C.c_double*((ContinuousROI.ws_size+7)//8))();results=[]
 try:
  for i,s in enumerate(cases):
   if s['group']=='two_windows':
    d=dirs[240:246,120:132].copy()
    if s['kind']=='conflict':d[:,6:12]=dirs[500:506,300:306]
    im=np.frombuffer(isolated_render(d.reshape(-1).tolist(),Render(columns=12,pitch=8,tx=100,ty=100,radius=1/6,width=200,height=200)),dtype=np.uint8).reshape(200,200)
   else:
    source=dirs.copy();changes=[]
    if s['group']=='corrupt_code':
     p=60/s['fov'];cx=int(s['ox']+100/p);cy=int(s['oy']+100/p)
     if s['kind'].startswith('one'):changes=[(cx,cy,int(s['kind'][-1]))]
     elif s['kind']=='two_changed':changes=[(cx,cy,1),(cx+1,cy,2)]
     else:changes=[(cx+dx,cy+dy,1+(dx+dy)%3) for dx in (-1,0,1) for dy in (-1,0,1)]
     for x,y,delta in changes:source[y,x]=(int(source[y,x])+delta)%4
     s['changed_cells']=[list(x) for x in changes]
    im=render(source,s)
    if s['kind']=='mirror':im=np.ascontiguousarray(im[:,::-1])
    if s['kind']=='quarter_turn':im=np.ascontiguousarray(np.rot90(im))
   rec=evaluate(ContinuousROI.lib,ws,im,s,dirs);results.append(rec)
   if s['group']=='two_windows':
    expected=0 if s['kind']=='agree' else -4
    assert rec['status']==expected,(s,rec)
   if rec['status']==0:assert rec['correct'],rec
   if s['group']=='two_windows' or rec['status']==0 and s['group']=='corrupt_code':
    name=f'case_{i:03d}.pgm';(out/name).write_bytes(b'P5\n200 200\n255\n'+im.tobytes());rec['fixture']=name
   (out/'results.json').write_text(json.dumps(results,indent=2));print(i,s['group'],s['kind'],rec['status'],rec.get('correct'),flush=True)
 finally:ContinuousROI.tearDownClass()
 return 0
if __name__=='__main__':sys.exit(main())
