import sys,json,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;C=P.parent/'smart_pen_tilt_v4_review_run_20261030';sys.path.insert(0,str(C))
from run_regression import generate,oracle
from binding import Decoder
old=json.loads((C/'source/verification/continuous/results.json').read_text());rows=[]
with Decoder() as dec:
 for i,s in enumerate(old):
  if s.get('damage')!='edge_stroke':continue
  im=generate(s);r=dec.decode(im);rows.append(dict(index=i,spec={k:s[k] for k in ('fov','damage','must_reject')},**r))
  if r['status']==0:
   rows[-1].update(oracle(s,r));clean=np.full_like(im,240);clean[60:140,60:140]=im[60:140,60:140]
   rr=dec.decode(clean);assert r==rr
   rows[-1]['outside80_replaced_identical_decoder_result']=True
   assert s['must_reject'] and rows[-1]['exact_symbols'] and rows[-1]['coordinate_correct'] and rows[-1]['orientation_correct'] and not rows[-1]['correct']
assert len(rows)==3 and all(r['status']==0 for r in rows)
(P/'negative_contract_review.json').write_text(json.dumps(rows,indent=2)+'\n')
print('REPRODUCED 3/3 forbidden edge_stroke accepts (not coordinate errors); changing every pixel outside80 leaves full decoder result unchanged. This is a RED quality gate, not pass.')
