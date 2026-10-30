"""Post-hoc independent component-to-true-cell support checks; never seeds C."""
import json,math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;OLD=P.parent/'smart_pen_continuous_independent_review_20261029'
source=json.loads((OLD/'results.json').read_text());replay=json.loads((P/'replay72.json').read_text());rows=[]
def components(im):
 threshold=(int(im.min())+int(im.max()))//2;seen=np.zeros(im.shape,bool);h,w=im.shape;found=[]
 for y,x in zip(*np.where(im<threshold)):
  if seen[y,x]:continue
  seen[y,x]=True;queue=[(int(y),int(x))];index=0
  while index<len(queue):
   yy,xx=queue[index];index+=1
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     ny,nx=yy+dy,xx+dx
     if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and im[ny,nx]<threshold:seen[ny,nx]=True;queue.append((ny,nx))
  found.append(queue)
 return found
for i,(s,r) in enumerate(zip(source,replay)):
 if s['kind']!='positive':continue
 im=np.frombuffer((OLD/s['fixture']).read_bytes().split(b'\n',3)[3],np.uint8).reshape(200,200)
 side=r['crop'][2] if not r['status'] else 96;left=(200-side)//2;crop=im[left:left+side,left:left+side].copy()
 for component in components(crop):
  if any(x==0 or y==0 or x==side-1 or y==side-1 for y,x in component):
   for y,x in component:crop[y,x]=int(im.max())
 p=60/s['fov'];angle=math.radians(s['angle']);co,si=math.cos(angle),math.sin(angle);cells=set()
 for component in components(crop):
  if len(component)<3:continue
  total=sx=sy=0
  for y,x in component:
   mass=int(crop.max())-int(crop[y,x]);total+=mass;sx+=mass*x;sy+=mass*y
  x,y=sx/total+left+.5,sy/total+left+.5;u=(x-100)/p;v=(y-100)/p;qx=co*u+si*v+s['cx'];qy=-si*u+co*v+s['cy'];cells.add((round(qx),round(qy)))
 complete=[(x,y) for x,y in cells if all((x+c,y+rr) in cells for rr in range(6) for c in range(6))]
 if not r['status']:assert (r['x'],r['y']) in complete
 else:assert not complete
 rows.append({'fixture':s['fixture'],'status':r['status'],'observed_true_cells':len(cells),'complete_observed_true_windows':len(complete),'decoded_window_observed':(r.get('x'),r.get('y')) in complete})
(P/'observed_support54.json').write_text(json.dumps(rows,indent=2));print('49 accepted windows fully observed; all5 remaining clean rejects have no complete observed true window.')
