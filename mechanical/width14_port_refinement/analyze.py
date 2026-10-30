import json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'width14_gate';D=json.loads((S/'input.json').read_text());O=json.loads((S/'options.json').read_text());refs=[v['ref'] for v in O['lateral_adjustment_screen']['violators']]
def boxes(delta,jx):
 out=[]
 for p in D['parts']:
  if p['dnp']:continue
  a,b,c,d=p['bounds']
  if p['ref'] in refs:a+=delta;c+=delta
  if p['ref']=='J109':a,b,c,d=jx-.9,18.1,jx+.9,25.1
  out.append(dict(p,bounds=[a,b,c,d]))
 return out
def overlap_pairs(parts):
 pairs=set()
 for i,p in enumerate(parts):
  a,b,c,d=p['bounds']
  for q in parts[i+1:]:
   if p['side']!=q['side']:continue
   aa,bb,cc,dd=q['bounds']
   if min(c,cc)-max(a,aa)>1e-8 and min(d,dd)-max(b,bb)>1e-8:pairs.add(tuple(sorted([p['ref'],q['ref']])))
 return pairs
def evaluate(y,parts):
 py=y-5.9;cs=[(math.hypot(7,py),'power'),(math.hypot(7,py+4.15),'power')]
 cs.extend((math.hypot(7,v),'outline') for v in [y,y+.93])
 for p in parts:
  a,b,c,d=p['bounds'];h=p['height_total'];ys=[y-h,y] if p['side']=='B' else [y+.93,y+.93+h]
  cs.extend((math.hypot(x-7,v),p['ref']) for x in [a,c] for v in ys)
 rad,lim=max(cs);return dict(main_B_y=y,main_F_y=y+.93,power_bottom_y=py,radius=rad,limiting=lim,OD19_worst_radial_remainder=8-rad,worst_interboard_remainder=.1,passes0p1_screen=rad<=7.9+1e-10)
basepairs=overlap_pairs(boxes(0,13));rows=[]
for delta in [.25,.30,.35,.40]:
 for jx in [12.5,12.25,12.0]:
  parts=boxes(delta,jx);best=None
  for i in range(1501):
   v=evaluate(1.5+i*.001,parts)
   if best is None or v['radius']<best['radius']:best=v
  rows.append(dict(left_column_shift=delta,J109_center_x=jx,J109_wire_XY=[1.8,2.2],fixed_B2p24=evaluate(2.24,parts),optimized=best,new_same_side_envelope_intersections=[list(p) for p in sorted(overlap_pairs(parts)-basepairs)]))
curves=[]
for y in [2.24,2.74]:
 for h in [.8,1.,1.2,1.5,2.,2.5]:
  top=y+.93+h;v=math.sqrt(max(0,7.9**2-top**2));curves.append(dict(Bdatum=y,height_above_F_including_solder=h,absolute_X_edge_limit=v,source_right_outer_edge_limit=7+v,J109_center_limit_for1p8wide=7+v-.9,assumption='Only radial envelope bound; not lowered-height qualification, no left-extension'))
result=dict(status='NOFAB geometry-only prelayout refinements; nativePCBunchanged',source_sha256=D['sha256'],fixed_global_X_offset=7,optional_left_RF_extension=False,left_refs=refs,left_refs_count=len(refs),residual_screen=.1,wire_basis='2mm height retained; XY1.8x2.2 hypothetical wire+solder/bend envelope supplied by USB worker, not measured. Prior gate used1.4wide copper bounds only.',rows=rows,curves=curves)
(R/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
