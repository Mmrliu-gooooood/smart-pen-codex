from pathlib import Path
from itertools import product
from collections import Counter
import csv,json
from model import screen
O=Path(__file__).resolve().parent
ranges={'pitch_mm':[.15,.3,.6,1.,2.,3.527778], 'dot_ratio':[.12,.2,.3,.4], 'offset_ratio':[.10,1/6,.25,.30,.35], 'distance_mm':[5.,10.,20.,40.], 'focal_px':[250.,500.,1000.], 'tilt_deg':[0.,15.,30.,45.,60.]}
rows=[]
for values in product(*ranges.values()):
 pars=dict(zip(ranges,values))
 try:r=screen(**pars)
 except ValueError:r={**pars,'status':'INVALID_DEPTH','screen_reasons':['plane_crosses_camera'],'engineering_proxy_rejects':[]}
 rows.append(r)
counts=Counter(r['status'] for r in rows);reasons=Counter(x for r in rows for x in r['screen_reasons']);proxies=Counter(x for r in rows for x in r['engineering_proxy_rejects'])
with (O/'sweep.csv').open('w') as f:
 fields=list(dict.fromkeys(k for r in rows for k in r));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:';'.join(v) if isinstance(v,list) else v for k,v in r.items()} for r in rows)
ret=[r for r in rows if r['status']=='MODEL_RETAIN_NOT_QUALIFIED']
examples=[]
for p in ranges['pitch_mm']:
 candidates=[r for r in ret if r['pitch_mm']==p and r['offset_ratio']==1/6 and r['dot_ratio']==.2]
 if candidates:examples.append(max(candidates,key=lambda r:(r['tilt_deg'],-abs(r['spacing_x_min_px']-16))))
summary={'synthetic_only':True,'ranges':ranges,'fixed':{'roi_px':256,'speed_mm_s':100,'exposure_us':100,'blur_limit_px':1},'counts':dict(counts),'screen_reasons':dict(reasons),'proxy_reasons':dict(proxies),'examples':examples,'retained_by_tilt':dict(Counter(r['tilt_deg'] for r in ret))}
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
