from pathlib import Path
import sys,json,hashlib
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
O=Path(__file__).resolve().parent;W=O.parent;rows=[]
def hit(a,b):
 x,y=a.BoundBox,b.BoundBox
 if any(min(getattr(x,k+'Max'),getattr(y,k+'Max'))-max(getattr(x,k+'Min'),getattr(y,k+'Min'))<1e-8 for k in 'XYZ'):return 0.
 return a.common(b).Volume
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 q=W/'assembly_outline_sync_20261030_1239/RevC_exact_outline_NOFAB.FCStd'if ctx=='RevC'else W/'assembly_support_tongue_variant_20261030_1251/corrected_connected'/f'{ctx}_support_proposal_NOFAB.FCStd'
 d=A.openDocument(str(q));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};A.closeDocument(d.Name);changed={}
 for ref,delta in [('R210',(9,0,-2)),('R217',(1.4,0,-7.19))]:
  keys=[k for k in S if k.startswith('INSTALL_'+ref+'_')]
  if len(keys)!=1:raise RuntimeError('body contract')
  k=keys[0];s=S[k].copy();s.translate(A.Vector(*delta));S[k]=s;changed[k]=s
 hits=[];near=[]
 for k,s in changed.items():
  for kk,t in S.items():
   if kk==k or kk.startswith('Native_outline'):continue
   v=hit(s,t)
   if v>1e-7:hits.append({'moved':k,'other':kk,'volume_mm3':v})
   near.append({'moved':k,'other':kk,'gap_mm':s.distToShape(t)[0]})
 r210=next(s for k,s in changed.items()if k.startswith('INSTALL_R210_'));neg=r210.copy();neg.translate(A.Vector(-3,0,0));r216=next(s for k,s in S.items()if k.startswith('INSTALL_R216_'));nv=hit(neg,r216)
 if nv<=0:raise RuntimeError('negative control')
 rows.append({'context':ctx,'source_cad_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'fullbody_count':sum(k.startswith('INSTALL_')for k in S),'hits':hits,'nearest':sorted(near,key=lambda r:r['gap_mm'])[:10],'negative_R210_left3_overlap_R216_mm3':nv})
(O/'placement_results.json').write_text(json.dumps(rows,indent=2)+'\n')
