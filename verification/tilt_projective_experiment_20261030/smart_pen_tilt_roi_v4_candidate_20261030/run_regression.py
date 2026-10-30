"""Replay all frozen340+68 synthetic models against NEW projective API.
No oracle values enter decoder; original upstream image hashes must match.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,math,time
from collections import Counter
import numpy as np
P=Path(__file__).resolve().parent
sys.path[:0]=[str(P/'source/tools'),str(P/'source/tests')]
from continuous_roi_sweep import render,project
from roi_opt_fixture import Render,render as isolated_render
sys.path.insert(0,str(P))
from binding import Decoder
from support_oracle import circle_support
D=np.load(P.parent/'smart_pen_viewport_audit_20261028/upstream_directions.npy')
KEYS=('group','fov','phase','ox','oy','angle','shear','perspective_x','perspective_y','ratio','blur','noise','seed','damage','section','must_reject','kind','omit','changed_cells')

def generate(s):
 source=D
 if s['group']=='fake_dots':source=np.random.default_rng(s['seed']).integers(0,4,D.shape,dtype=np.uint8)
 if s['group']=='two_windows':
  d=D[240:246,120:132].copy()
  if s['kind']=='conflict':d[:,6:12]=D[500:506,300:306]
  return np.frombuffer(isolated_render(d.reshape(-1).tolist(),Render(columns=12,pitch=8,tx=100,ty=100,radius=1/6,width=200,height=200)),dtype=np.uint8).reshape(200,200)
 if s['group']=='corrupt_code':
  source=D.copy()
  for x,y,delta in s['changed_cells']:source[y,x]=(int(source[y,x])+delta)%4
 im=render(source,s)
 if s.get('kind')=='mirror':im=np.ascontiguousarray(im[:,::-1])
 if s.get('kind')=='quarter_turn':im=np.ascontiguousarray(np.rot90(im))
 return im

def mapped(h,x,y):
 z=h[6]*x+h[7]*y+h[8];return np.array([(h[0]*x+h[1]*y+h[2])/z,(h[3]*x+h[4]*y+h[5])/z])

def oracle(s,r):
 x,y=r['x'],r['y'];h=r['H'];exact=list(r['directions'])==D[y:y+6,x:x+6].reshape(-1).tolist();support=True;errors=[];cosines=[];l,t,w,hh=r['roi'];omitted=set(map(tuple,s.get('omit',[])))
 for yy in range(y,y+6):
  for xx in range(x,x+6):
   true=np.array(project(xx,yy,s))-.5;pred=mapped(h,xx,yy);errors.append(float(np.linalg.norm(true-pred)))
   for dx,dy in ((.01,0),(0,.01)):
    a=mapped(h,xx+dx,yy+dy)-pred;b=np.array(project(xx+dx,yy+dy,s))-.5-true
    cosines.append(float(a@b/(np.linalg.norm(a)*np.linalg.norm(b))))
   dx,dy=((0,-1),(-1,0),(1,0),(0,1))[D[yy,xx]]
   for rx in (-1/6,1/6):
    for ry in (-1/6,1/6):
     px,py=np.array(project(xx+dx/6+rx,yy+dy/6+ry,s))-.5
     support &= bool(l-.5<=px<l+w-.5 and t-.5<=py<t+hh-.5 and (xx,yy) not in omitted)
 orientation=min(cosines)>math.cos(math.radians(5));coord=max(errors)<=.1*(60/s['fov']);allowed=not s.get('must_reject',False)
 circle=circle_support(s,r,D)
 return dict(correct=bool(exact and circle['circle_support'] and orientation and coord and allowed),exact_symbols=exact,square_support=support,complete_support=circle['circle_support'],orientation_correct=orientation,coordinate_correct=coord,max_grid_error_px=max(errors),min_basis_cosine=min(cosines),allowed=allowed,**circle)

def main():
 rows=[]
 provenance={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'source/firmware/vision/roi_projective.c',P/'source/firmware/vision/roi_projective.h',P/'source/firmware/vision/roi_opt.c',P/'source/firmware/codec/anoto.c',Path(__file__),P/'support_oracle.py')}
 (P/'regression_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 with Decoder() as dec:
  for sourcefile in ('continuous/results.json','v3_adversarial/results.json'):
   old=json.loads((P/'source/verification'/sourcefile).read_text())
   for i,baseline in enumerate(old):
    s={k:baseline[k] for k in KEYS if k in baseline};im=generate(s);sha=hashlib.sha256(im.tobytes()).hexdigest();assert sha==baseline['sha256'],(sourcefile,i,'renderer changed')
    start=time.perf_counter();r=dec.decode(im,(710,1000,*s.get('section',(10,2))));elapsed=time.perf_counter()-start
    if r['status']==0:r.update(oracle(s,r))
    r.update(spec=s,fixture_index=i,source=sourcefile,baseline_status=baseline['status'],image_sha256=sha,host_seconds=elapsed)
    rows.append(r)
    if r['status']==0 and not r['correct']:
     name=f'regression_false_{len(rows)-1:03d}.pgm';(P/name).write_bytes(b'P5\n200 200\n255\n'+im.tobytes());r['fixture']=name
     print('FALSE_ACCEPT',sourcefile,i,s,r,flush=True)
    print(len(rows),sourcefile,i,s['group'],r['status'],r.get('correct'),flush=True)
    (P/'regression_results.json').write_text(json.dumps(dict(workspace_bytes=dec.workspace_bytes,cases=rows),indent=2)+'\n')
 summary={}
 for source in sorted(set(r['source'] for r in rows)):
  rr=[r for r in rows if r['source']==source];accepted=[r for r in rr if r['status']==0]
  summary[source]=dict(n=len(rr),status=dict(Counter(r['status'] for r in rr)),correct=sum(r['correct'] for r in accepted),false_accepts=sum(not r['correct'] for r in accepted),forbidden_negative_accept=sum(not r['allowed'] for r in accepted),coordinate_or_symbol_wrong=sum(not r['coordinate_correct'] or not r['exact_symbols'] or not r['orientation_correct'] for r in accepted),square_support_failures=sum(not r['square_support'] for r in accepted),circle_support_failures=sum(not r['circle_support'] for r in accepted),lost_old_accept=sum(r['baseline_status']==0 and r['status']!=0 for r in rr),new_accept=sum(r['baseline_status']!=0 and r['status']==0 for r in rr))
 (P/'regression_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)
 return int(any(r['status']==0 and not r['correct'] for r in rows))
if __name__=='__main__':sys.exit(main())
