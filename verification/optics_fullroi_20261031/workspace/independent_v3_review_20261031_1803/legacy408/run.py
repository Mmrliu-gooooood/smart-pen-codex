"""Unchanged archived V3 C, exact frozen340+68 image-hash replay; no oracle into C."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,ctypes as C,time
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]/'publication_20261031/target_repo'
V3=ROOT/'verification/continuous_v3_experiments_20261029/smart_pen_continuous_roi_v3_candidate_20261029'
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(V3/'tools'),str(V3/'tests')]
import numpy as np
from continuous_roi_sweep import render,evaluate,ContinuousROI
from roi_opt_fixture import Render,render as isolated_render
DP=ROOT/'verification/continuous_roi_experiments_20261029/smart_pen_viewport_audit_20261028/upstream_directions.npy'
D=np.load(DP)
sources=list((V3/'firmware').rglob('*'))+list((V3/'tools').glob('*.py'))+list((V3/'tests').glob('*.*'))+[DP,V3/'verification/continuous/results.json',V3/'verification/v3_adversarial/results.json']
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.is_file()}
(OUT/'input_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
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
rows=[];ContinuousROI.setUpClass();ws=(C.c_double*((ContinuousROI.ws_size+7)//8))()
try:
 for dataset in ['continuous','v3_adversarial']:
  old=json.loads((V3/f'verification/{dataset}/results.json').read_text())
  for i,s in enumerate(old):
   im=generate(s);sha=hashlib.sha256(im.tobytes()).hexdigest()
   if sha!=s['sha256']:raise RuntimeError(f'image drift {dataset} {i}')
   result=evaluate(ContinuousROI.lib,ws,im,s,D)
   result.update(dataset=dataset,index=i,baseline_status=s['status'],status_equal_baseline=result['status']==s['status'],pixel_hash_verified=True)
   rows.append(result)
   print(len(rows),dataset,i,result['status'],result.get('correct'),flush=True)
   (OUT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
finally:ContinuousROI.tearDownClass()
for f,h in hashes.items():
 if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise RuntimeError('source changed '+f)
summary={'cases':len(rows),'accepted':sum(r['status']==0 for r in rows),'correct_accepts':sum(r['status']==0 and r.get('correct',False) for r in rows),'wrong_or_quality_violating_accepts':sum(r['status']==0 and not r.get('correct',False) for r in rows),'must_reject_accepts':sum(r['status']==0 and r.get('must_reject',False) for r in rows),'rejected':sum(r['status']!=0 for r in rows),'status_changes':sum(not r['status_equal_baseline'] for r in rows),'all_image_hashes_match':True,'workspace_bytes':ContinuousROI.ws_size,'source_changed':False,'oracle':'unchanged archivedV3 evaluate; support is center-based historicalcontract, not upgraded whole-dot oracle','groups':{g:dict(Counter(r['status'] for r in rows if r['group']==g)) for g in sorted(set(r['group'] for r in rows))}}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
sys.exit(int(summary['wrong_or_quality_violating_accepts']>0 or summary['status_changes']>0 or len(rows)!=408))
