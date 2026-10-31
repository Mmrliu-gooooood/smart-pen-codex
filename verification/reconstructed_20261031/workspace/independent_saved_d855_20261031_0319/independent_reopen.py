from pathlib import Path
import sys,json,hashlib
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
O=Path(__file__).resolve().parent;W=O.parent;C=W/'reconstruction_saved_cad_f27_20261031_0156';out=[]
def need(v,m):
 if not v:raise RuntimeError(m)
def objects(d):return {o.Label:o for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()}
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 src=C/f'{ctx}_NEW_f27_RESEARCH_NOFAB.FCStd';target=O/f'{ctx}_NEW_d855_RESEARCH_NOFAB.FCStd';d=A.openDocument(str(src));S=objects(d);shapes={k:o.Shape.copy()for k,o in S.items()};ops={o.Label:o.Evidence for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')};statuses={k:getattr(o,'Status',None)for k,o in S.items()};A.closeDocument(d.Name)
 d=A.openDocument(str(target));T=objects(d);need(set(S)==set(T),'all actual labels');diffs=[];changed=[]
 for k,o in T.items():
  expected=shapes[k]
  if k.startswith('INSTALL_R230_') or k.startswith('INSTALL_R219_'):
   ref=k.split('_')[1];x,y,angle={'R230':(11.1,34.25,90),'R219':(6.2,39.5,0)}[ref];c=expected.BoundBox.Center
   if angle:expected.rotate(c,A.Vector(0,1,0),angle)
   expected.translate(A.Vector(x-7-c.x,0,127-y-c.z));changed.append(k)
  need(o.Shape.isValid(),'valid saved shape')
  if o.Shape.exportBrepToString()!=expected.exportBrepToString():
   delta=o.Shape.cut(expected).Volume+expected.cut(o.Shape).Volume;need(delta<1e-8,'actual shape altered '+k);diffs.append({'label':k,'symmetric_difference_mm3':delta})
  need(getattr(o,'Status',None)==statuses[k],'uncertainty metadata')
 need(len(changed)==2,'two full moves');need({o.Label:o.Evidence for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')}==ops and len(ops)==6,'six actual Evidence records')
 m=d.getObject('NativeBinding');need(m.PCB_SHA256=='d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b'and m.ParentSavedCAD_SHA256==sha(src),'actual new metadata')
 board=next(o for k,o in T.items()if k.startswith('Native_outline'));need(board.CurrentPCB_SHA256==m.PCB_SHA256,'boardbinding');need(abs(board.Shape.Volume-1276.146)<1e-6,'steppedboardvolume');step=Part.Shape();step.read(str(target.with_suffix('.step')));residual=step.Volume-sum(o.Shape.Volume for o in T.values());solids=sum(len(o.Shape.Solids)for o in T.values());need(step.isValid()and len(step.Solids)==solids and abs(residual)<.005,'STEP')
 # Direct nonmutating wrong-face negative on actual delivered saved state.
 r=next(o.Shape.copy()for k,o in T.items()if k.startswith('INSTALL_R230_'));c=next(o.Shape for k,o in T.items()if k.startswith('INSTALL_U201_'));r.translate(c.BoundBox.Center-r.BoundBox.Center);neg=r.common(c).Volume;need(neg>0,'actual saved body negative')
 out.append({'context':ctx,'source_sha256':sha(src),'delivered_FCStd_sha256':sha(target),'delivered_STEP_sha256':sha(target.with_suffix('.step')),'all_shapes_exact_source_or_two_translations':True,'symmetric_differences':diffs,'retained_operations':sorted(ops),'shape_count':len(T),'full_budget_count':sum(k.startswith('INSTALL_')for k in T),'STEP_solids':solids,'STEP_exchange_residual_mm3':residual,'STEP_exchange_bound_mm3':.005,'wrong_face_negative_mm3':neg});A.closeDocument(d.Name)
(O/'independent_reopen.json').write_text(json.dumps(out,indent=2)+'\n')
