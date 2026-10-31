# NEW Oct31 derivative from exact recovered saved4d7d, not restoration of any lost later CAD.
from pathlib import Path
import os,sys,json,hashlib
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;W=R.parent;O=Path(os.environ.get('RECOVERY_CAD_OUTPUT',str(R)));O.mkdir(parents=True,exist_ok=True);C=W/'reconstruction_saved_cad_f27_20261031_0156';PCB='d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b';sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def hit(s,t):
 a,b=bb(s),bb(t)
 if any(min(a[k+3],b[k+3])-max(a[k],b[k])<1e-8 for k in range(3)):return 0.
 return s.common(t).Volume
need(sha(C/'manifest.json')=='16459c2cf811324a6e59658426d18297dc7aa3a7e4d335c233d7f47ebbc4ad66','recovered CAD manifest');cm=json.load(open(C/'manifest.json'))['files'];M=W/'reconstruction_receive_margin_mechanics_20261031_0305';need(sha(M/'manifest.json')=='7b5941e25c88ecb1dfad76c88c43555a6a50f0a4d36fe22dd077976fe860c6d5','exact mechanical evidence')
for f,h in json.load(open(M/'manifest.json'))['files'].items():need(sha(M/f)==h['sha256'],'mechanical file binding')
need(sha(M/'selected_native.kicad_pcb')==PCB,'selected PCB');sr=json.load(open(M/'results.json'));need(sr['all103_contracts_only_two_exact_rigid_changes']and sr['all104_full_budgets_retained']and sr['pcb_sha256']==PCB,'full contract evidence')
refs={r['ref']for r in json.load(open(W/'reconstruction_mechanics_20261031_0053/native_contracts.json'))['rows']};out=[]
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 q=C/f'{ctx}_NEW_f27_RESEARCH_NOFAB.FCStd';before=sha(q);need(before==cm[q.name],'exact recovered CAD');d=A.openDocument(str(q));S={o.Label:o for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};original={k:o.Shape.copy()for k,o in S.items()};ops={o.Label:o.Evidence for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')};statuses={k:getattr(o,'Status',None)for k,o in S.items()};changed={}
 for ref,x,y,angle in [('R230',11.1,34.25,90),('R219',6.2,39.5,0)]:
  keys=[k for k in S if k.startswith('INSTALL_'+ref+'_')];need(len(keys)==1,'unique full body');k=keys[0];s=S[k].Shape.copy();center=s.BoundBox.Center
  if angle:s.rotate(center,A.Vector(0,1,0),angle)
  s.translate(A.Vector(x-7-center.x,0,127-y-center.z));need(abs(s.Volume-original[k].Volume)<1e-7,'full volume preserved');S[k].Shape=s;changed[k]=s
 meta=d.getObject('NativeBinding');need(meta is not None and meta.PCB_SHA256=='f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71','original binding');meta.Label='NEW_OCT31_RESEARCH_D855_NATIVE_BINDING';meta.PCB_SHA256=PCB;meta.Gate='NEW recovery derivative. Independent electrical review pending. NOFAB NO POWER. .93 thickness is budget, not measurement.'
 for prop,value in [('ParentSavedCAD_SHA256',before),('ParentSavedPCB_SHA256','f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71'),('CurrentPoseDeltaJSON',json.dumps({'R230':{'from':[7.5,40.9,0,'F.Cu'],'to':[11.1,34.25,90,'F.Cu']},'R219':{'from':[7.5,41.5,0,'B.Cu'],'to':[6.2,39.5,0,'B.Cu']}}))]:
  if prop not in meta.PropertiesList:meta.addProperty('App::PropertyString',prop)
  setattr(meta,prop,value)
 boardkey=next(k for k in S if k.startswith('Native_outline'));need(S[boardkey].CurrentPCB_SHA256=='f27d375c941b5cd026cf441b18994a47f4c27169b9e3a34946511542b69b1c71','old board metadata');S[boardkey].CurrentPCB_SHA256=PCB
 hits=[];near=[]
 for k,s in changed.items():
  for kk,o in S.items():
   if kk in [k,boardkey]:continue
   v=hit(s,o.Shape)
   if v>1e-7:hits.append({'moved':k,'other':kk,'volume_mm3':v})
   near.append({'moved':k,'other':kk,'gap_mm':s.distToShape(o.Shape)[0]})
 need(not hits,'new pose collision');static={k.split('_')[1]for k in S if k.startswith('INSTALL_')};operation={k.removeprefix('UNQUALIFIED_OPERATION_')for k in ops};need(len(operation)==6 and static|operation==refs and not(static&operation),'103 refs/six operations');need(sum(k.startswith('INSTALL_')for k in S)==104,'104 bodies')
 for k,o in S.items():
  if k not in changed:need(bb(o.Shape)==bb(original[k])and abs(o.Shape.Volume-original[k].Volume)<1e-7,'unchanged board/support/other bodies')
 target=O/f'{ctx}_NEW_d855_RESEARCH_NOFAB.FCStd';stepfile=target.with_suffix('.step');d.recompute();d.saveAs(str(target));Part.export(list(S.values()),str(stepfile));A.closeDocument(d.Name)
 rd=A.openDocument(str(target));new={o.Label:o for o in rd.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};need(set(new)==set(S),'saved labels');need({o.Label:o.Evidence for o in rd.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')}==ops,'saved operation evidence');need(rd.getObject('NativeBinding').PCB_SHA256==PCB and rd.getObject('NativeBinding').ParentSavedCAD_SHA256==before and new[boardkey].CurrentPCB_SHA256==PCB,'reopened native metadata')
 for k,o in new.items():
  expected=changed[k]if k in changed else original[k];need(max(abs(a-z)for a,z in zip(bb(o.Shape),bb(expected)))<1e-7 and abs(o.Shape.Volume-expected.Volume)<1e-6,'saved exact body bounds/volume');need(getattr(o,'Status',None)==statuses[k],'retained uncertainty/basis status')
 sb=new[boardkey].Shape.BoundBox;need(abs(sb.XLength-14)<1e-7 and abs(sb.ZLength-99.8)<1e-7 and abs(sb.YLength-.93)<1e-7,'exact board budget dimensions')
 step=Part.Shape();step.read(str(stepfile));residual=step.Volume-sum(o.Shape.Volume for o in new.values());need(step.isValid()and len(step.Solids)==sum(len(o.Shape.Solids)for o in new.values())and abs(residual)<.005,'STEP exchange')
 out.append({'context':ctx,'source_CAD_sha256':before,'saved_path':target.name,'selected_native_sha256':PCB,'full_static_entities':104,'static_refs':len(static),'operation_refs':sorted(operation),'unchanged_objects_except_two_full_bodies':len(S)-2,'body_changes':{k:{'before':bb(original[k]),'after':bb(s)}for k,s in changed.items()},'nearest':sorted(near,key=lambda x:x['gap_mm'])[:8],'hits':hits,'reopened_all_shapes_metadata_operations_equal':True,'STEP_valid':step.isValid(),'STEP_solids':len(step.Solids),'STEP_volume_exchange_residual_mm3':residual});A.closeDocument(rd.Name);need(sha(q)==before,'recovered source changed')
(O/'results.json').write_text(json.dumps({'status':'NEW_RESEARCH_ONLY_SAVED_D855_GEOMETRY','pcb_sha256':PCB,'mechanical_manifest_sha256':sha(M/'manifest.json'),'contexts':out},indent=2)+'\n')
