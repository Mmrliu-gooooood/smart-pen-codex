from pathlib import Path
import sys,json,hashlib
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
O=Path(__file__).resolve().parent;W=O.parent;C=W/'recovery_inputs59_20261031/assembly_data8_support_sync_20261030_1314';E=json.load(open(O/'full104_4d7d.json'));rows=[]
def hit(a,b):
 x,y=a.BoundBox,b.BoundBox
 if any(min(getattr(x,k+'Max'),getattr(y,k+'Max'))-max(getattr(x,k+'Min'),getattr(y,k+'Min'))<1e-8 for k in 'XYZ'):return 0.
 return a.common(b).Volume
for ctx in E['contexts']:
 name=ctx['context'];q=C/f'{name}_data8_support_RESEARCH_NOFAB.FCStd'
 if hashlib.sha256(q.read_bytes()).hexdigest()!=ctx['source_cad_sha256']:raise RuntimeError('recovered source changed')
 d=A.openDocument(str(q));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};A.closeDocument(d.Name)
 key=next(k for k in S if k.startswith('INSTALL_R503_'));old=S[key];s=old.copy();s.translate(A.Vector(5.5,0,-5));b=s.BoundBox
 if max(abs(a-z)for a,z in zip([b.XLength,b.YLength,b.ZLength],[2.45,1.45,.95]))>1e-7:raise RuntimeError('full contract changed')
 hits=[];near=[]
 for k,t in S.items():
  if k==key or k.startswith('Native_outline'):continue
  v=hit(s,t)
  if v>1e-7:hits.append({'other':k,'volume_mm3':v})
  near.append({'other':k,'gap_mm':s.distToShape(t)[0]})
 wrong=s.copy();wrong.translate(A.Vector(0,1.1,0));c104=next(t for k,t in S.items()if k.startswith('INSTALL_C104_'));negative=hit(wrong,c104)
 if hits or negative<=0:raise RuntimeError('pose/negative guard')
 rows.append({'context':name,'source_sha256':ctx['source_cad_sha256'],'basis_pcb_sha256':E['basis_sha256'],'proposal_only':{'R503':[8,16.5,0,'B.Cu']},'static_envelopes':104,'hits':hits,'nearest':sorted(near,key=lambda x:x['gap_mm'])[:6],'wrong_face_Y_plus1p1_negative_overlap_mm3':negative})
(O/'proposed_R503_contexts.json').write_text(json.dumps(rows,indent=2)+'\n')
