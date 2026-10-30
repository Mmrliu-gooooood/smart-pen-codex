import os,sys,json,math,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
D=Path(__file__).resolve().parent;W=D.parents[3];M=W/'smart_pen_mechanics_next_20261028/mechanical';V=A.Vector
inputs=[('RevC',M/'gate508e_joint_screen_0247/RevC_gate508e.FCStd','CTX_'),('RevD_BENCH',M/'gate508e_joint_screen_0247/RevD_gate508e.FCStd','REF_CTX_')]+[(f'ACCESS{od}',M/f'compliant_retainer_longarc_0415/access_revision/ACCESS_retainer_OD{od}_t0p93_NOFAB.FCStd','REF_CTX_')for od in [19,20]]
poses={'C103':{'old':[1.2,7.025],'new':[.8,7.025]},'R503':{'old':[2.5,7.5],'new':[2.5,11.5]}}
def hit(a,b):
 x,y=a.BoundBox,b.BoundBox
 if any(min(getattr(x,t+'Max'),getattr(y,t+'Max'))-max(getattr(x,t+'Min'),getattr(y,t+'Min'))<=1e-8 for t in 'XYZ'):return 0
 return a.common(b).Volume
rows=[]
for name,path,pre in inputs:
 d=A.openDocument(str(path));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and o.TypeId!='App::DocumentObjectGroup'};A.closeDocument(d.Name);modified={};contracts={}
 for ref,c in poses.items():
  keys=[k for k in S if k==pre+ref or k.startswith(pre+ref+'.')or k.startswith(pre+ref+'_')]
  if not keys:raise ValueError('missing '+ref+' '+name)
  for k in keys:
   s=S[k].copy();s.translate(V(c['new'][0]-c['old'][0],0,-(c['new'][1]-c['old'][1])));modified[k]=s;bb=s.BoundBox;contracts[k]={'ref':ref,'retained_XYZ':[bb.XLength,bb.YLength,bb.ZLength],'bounds':[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax],'height_qualified':False}
 S.update(modified);hh=[]
 for k,s in modified.items():
  for kk,t in S.items():
   if kk==k or kk in ['Context_ONLY','REF_Context_ONLY']:continue
   v=hit(s,t)
   if v>1e-7:hh.append({'moved':k,'other':kk,'volume_mm3':v})
 rows.append({'context':name,'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'contracts':contracts,'collisions':hh})
 print(name,hh,flush=True)
(D/'mechanics.json').write_text(json.dumps({'scope':'nominal inherited full installation envelope only; contexts do not constitute qualified final assembly; no zero heights substituted','poses':poses,'contexts':rows},indent=2)+'\n')
