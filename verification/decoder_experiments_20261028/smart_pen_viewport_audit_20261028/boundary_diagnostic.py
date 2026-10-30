"""NONPRODUCTION pixel-only edge-component removal experiment, no geometry oracle.
Reuses upstream generation + compiled unmodified C functions from audit.py prefix.
"""
from pathlib import Path
exec((Path(__file__).parent/'audit.py').read_text().split('records=[]')[0])
original=json.loads((OUT/'results.json').read_text()); results=[]; histories={}
def edge_filter(im):
 out=im.copy(); threshold=(int(im.min())+int(im.max()))//2; mask=im<threshold; seen=np.zeros(im.shape,bool); h,w=im.shape; counts=Counter()
 for y,x in zip(*np.where(mask)):
  if seen[y,x]:continue
  seen[y,x]=True; todo=[(y,x)];component=[]
  while todo:
   yy,xx=todo.pop();component.append((yy,xx))
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     ny,nx=yy+dy,xx+dx
     if 0<=ny<h and 0<=nx<w and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;todo.append((ny,nx))
  edge=any(y==0 or x==0 or y==h-1 or x==w-1 for y,x in component)
  if edge:
   for y,x in component:out[y,x]=240
  if len(component)>=3:counts['edge' if edge else 'interior']+=1
 return out,dict(counts)
for old in original:
 fov,size=old['fov_mm'],old['size']; start=(200-size)//2; full=render(fov,old['ox_cells'],old['oy_cells']); im,components=edge_filter(full[start:start+size,start:start+size]); prior=Prior();cold,result=decode(im,prior)
 rec={k:old[k] for k in ('fov_mm','size','phase','ox_cells','oy_cells')};rec.update(cold=cold,components=components,image_sha256=hashlib.sha256(im.tobytes()).hexdigest())
 if cold['status']==0:
  x,y=cold['x'],cold['y'];p=60/fov;left=old['ox_cells']+start/p;top=old['oy_cells']+start/p
  rec['correct']=list(result.decoded.directions)==dirs[y:y+6,x:x+6].reshape(-1).tolist() and left-1/3<=x<=left+size/p-5+1/3 and top-1/3<=y<=top+size/p-5+1/3
 key=(fov,size);history=histories.setdefault(key,Prior());warm,wr=decode(im,history);rec['sequential_warm']=warm
 if warm['status']==0:
  x,y=warm['x'],warm['y'];p=60/fov;left=old['ox_cells']+start/p;top=old['oy_cells']+start/p
  warm['correct']=list(wr.decoded.directions)==dirs[y:y+6,x:x+6].reshape(-1).tolist() and left-1/3<=x<=left+size/p-5+1/3 and top-1/3<=y<=top+size/p-5+1/3
 results.append(rec)
 (OUT/'boundary_results.json').write_text(json.dumps(results,indent=2))
 print(f'{fov=} {size=} phase={old["phase"]} cold={cold["status"]} sequential={warm["status"]}',flush=True)
summary=[]
for fov in (5,6,7):
 for size in (200,96,80,64):
  group=[r for r in results if r['fov_mm']==fov and r['size']==size]
  summary.append({'fov_mm':fov,'roi':size,'n':len(group),'cold':dict(Counter(r['cold']['status'] for r in group)),'false_cold':sum(not r['correct'] for r in group if r['cold']['status']==0),'sequential_warm':dict(Counter(r['sequential_warm']['status'] for r in group)),'used_warm':sum(r['sequential_warm'].get('warm',False) for r in group),'false_warm':sum(not r['sequential_warm']['correct'] for r in group if r['sequential_warm']['status']==0),'interior_dot_range':[min(r['components'].get('interior',0) for r in group),max(r['components'].get('interior',0) for r in group)]})
(OUT/'boundary_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
