"""Frozen fixtures, exact 8-connected threshold component audit; no code oracle."""
import numpy as np,json,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent
out=[]
for p in sorted((ROOT.parent/'smart_pen_optical_sampling_audit_20261030').glob('tilt*.pgm')):
 a=np.frombuffer(p.read_bytes().split(b'\n',3)[3],np.uint8).reshape(200,200)
 for size in (96,80):
  c=a[(200-size)//2:(200+size)//2,(200-size)//2:(200+size)//2]; mask=c<(int(c.min())+int(c.max()))//2; seen=set(); comps=[]
  for y,x in zip(*np.where(mask)):
   y,x=int(y),int(x)
   if (y,x) in seen:continue
   q=[(y,x)];seen.add((y,x))
   for yy,xx in q:
    for dy in (-1,0,1):
     for dx in (-1,0,1):
      v,u=yy+dy,xx+dx
      if 0<=v<size and 0<=u<size and mask[v,u] and (v,u) not in seen:seen.add((v,u));q.append((v,u))
   ys,xs=zip(*q);bw=max(xs)-min(xs)+1;bh=max(ys)-min(ys)+1;edge=min(xs)==0 or min(ys)==0 or max(xs)==size-1 or max(ys)==size-1
   edge_bad=edge and (len(q)>24 or bw>6 or bh>6 or ((min(xs)==0 or max(xs)==size-1) and bw>4) or ((min(ys)==0 or max(ys)==size-1) and bh>4))
   reason=('edge_bad' if edge_bad else 'edge') if edge else ('speckle' if len(q)<3 else ('shape' if bw>2*bh or bh>2*bw or len(q)>100 else 'dot'))
   comps.append(dict(n=len(q),bw=bw,bh=bh,reason=reason,x=min(xs),y=min(ys)))
  r=dict(image=p.name,side=size,counts=dict(Counter(c['reason'] for c in comps)),components=comps);out.append(r);print(p.name,size,r['counts'])
(ROOT/'component_diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
