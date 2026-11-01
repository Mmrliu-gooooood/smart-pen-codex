import json,math
from pathlib import Path
O=Path(__file__).resolve().parent;P=O.parent/'optics_paper_screen_20261031_1752/decoder_probe';specs={r['pgm']:r['spec'] for name in ['results.json','controls_results.json'] for r in json.loads((P/name).read_text())};truth=json.loads((P/'summary.json').read_text())['truth'];out=[]
for gate in ['off','on']:
 f=O/f'regression/{gate}_results.json'
 if not f.exists():continue
 for r in json.loads(f.read_text()):
  if r['dataset']!='probe' or r['status']!=0:continue
  s=specs[r['key']];margin=1e99;c=math.cos(math.radians(s['angle']));si=math.sin(math.radians(s['angle']))
  for i,d in enumerate(truth['directions']):
   dx,dy=((0,-1),(-1,0),(1,0),(0,1))[d]
   for a in [-s['radius'],s['radius']]:
    for b in [-s['radius'],s['radius']]:
     x=i%6-2.5+dx*s['offset']+a;y=i//6-2.5+dy*s['offset']+b;z=1+s['perspective_x']*x+s['perspective_y']*y;xx=x+s['shear']*y;yy=y*s['scale_y'];u=s['tx']+s['pitch']*(c*xx-si*yy)/z;v=s['ty']+s['pitch']*(si*xx+c*yy)/z;margin=min(margin,u,v,200-u,200-v)
  if margin<0:raise RuntimeError('probe support violation')
  out.append({'gate':gate,'pgm':r['key'],'margin_px':margin})
(O/'verification/probe_support.json').write_text(json.dumps({'scope':'Independent post-return oracle, not claimed as author probe scoring','accepted_cases':len(out),'minimum_margin_px':min(r['margin_px'] for r in out),'rows':out},indent=2)+'\n');print(len(out))
