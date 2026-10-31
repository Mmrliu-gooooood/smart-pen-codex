from pathlib import Path
import json,math
O=Path(__file__).resolve().parent;j=json.load(open(O/'results.json'));M=json.load(open(O/'proposed_full104.json'))['all_static_rectangles']
def pd(a,c,d):
 dx,dy=d[0]-c[0],d[1]-c[1];t=max(0,min(1,((a[0]-c[0])*dx+(a[1]-c[1])*dy)/(dx*dx+dy*dy)))if dx or dy else 0;return math.hypot(a[0]-c[0]-t*dx,a[1]-c[1]-t*dy)
def gap(a,z,pts,rad):return min(min(pd(a,c,d),pd(z,c,d),pd(c,a,z),pd(d,a,z))for c,d in zip(pts,pts[1:]+pts[:1]))-rad
rows=[]
for r in j['rows']:
 sides=['F.Cu','B.Cu']if r['type']=='via'else[r['layer']]if r['layer']in['F.Cu','B.Cu']else[]
 for e in M:
  if e['side']not in sides or any(h['entity']==e['entity']for h in r['body_hits']):continue
  x1,y1,x2,y2=e['xy_bounds'];d=gap(r['a'],r['b'],[(x1,y1),(x2,y1),(x2,y2),(x1,y2)],r['width_mm']/2)
  if d<-.000001:raise RuntimeError('unexpected unclassified full envelope proximity')
  rows.append({'uuid':r['uuid'],'kind':r['type'],'net':r['net'],'layer':r['layer'],'ref':e['ref'],'side':e['side'],'gap_mm':d})
(O/'finite_disjoint_margins.json').write_text(json.dumps({'scope':'All finite exterior segments and both via faces to every same-face disjoint full installation envelope; actual intersecting terminal targets listed separately in screen results','minimum':min(rows,key=lambda r:r['gap_mm']),'all_pairs':len(rows),'under_0p2_mm':[r for r in rows if r['gap_mm']<.2-1e-9]},indent=2)+'\n')
print(min(rows,key=lambda r:r['gap_mm']))
