from pathlib import Path
import sys,json,hashlib,os
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;W=R.parent;O=Path(os.environ.get('DATA8_CAD_OUTPUT',str(R)));O.mkdir(parents=True,exist_ok=True)
PCB='4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad';sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
sourcepcb=W/'smart_pen_next_20261028/hardware/data_bias_relocate_1242/native/mainboard_revD.kicad_pcb'
def require(v,msg):
 if not v:raise RuntimeError(msg)
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def hit(s,t):
 a,b=bb(s),bb(t)
 if any(min(a[k+3],b[k+3])-max(a[k],b[k])<1e-8 for k in range(3)):return 0.
 return s.common(t).Volume
require(sha(sourcepcb)==PCB,'native changed')
M=W/'assembly_data8_review_20261030_1256';sr=json.load(open(M/'results.json'))['stages'][0];require(sr['sha256']==PCB and sr['all103_contract_equal'],'native contract evidence');require(sr['outline']==[0,-6.5,14,93.3],'outline')
refs={r['ref']for r in json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']};out=[]
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 q=W/'assembly_outline_sync_20261030_1239/RevC_exact_outline_NOFAB.FCStd'if ctx=='RevC'else W/'assembly_support_tongue_variant_20261030_1251/corrected_connected'/f'{ctx}_support_proposal_NOFAB.FCStd'
 before=sha(q);require(before==next(c['source_cad_sha256']for c in json.load(open(M/'placement_results.json'))if c['context']==ctx),'frozen support CAD hash');d=A.openDocument(str(q));S={o.Label:o for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};original={k:o.Shape.copy()for k,o in S.items()};ops={o.Label:o.Evidence for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')};changed={}
 for ref,delta in [('R210',(9,0,-2)),('R217',(1.4,0,-7.19))]:
  keys=[k for k in S if k.startswith('INSTALL_'+ref+'_')];require(len(keys)==1,'unique full body');k=keys[0];s=S[k].Shape.copy();s.translate(A.Vector(*delta));S[k].Shape=s;changed[k]=s
 meta=d.addObject('App::FeaturePython','NativeBinding');meta.Label='RESEARCH_ONLY_DATA8_NATIVE_BINDING';meta.addProperty('App::PropertyString','PCB_SHA256');meta.PCB_SHA256=PCB;meta.addProperty('App::PropertyString','Gate');meta.Gate='Research only; electrical joint review pending; NOFAB NO POWER. .93 thickness budget, not measured.'
 boardkey=next(k for k in S if k.startswith('Native_outline'));S[boardkey].addProperty('App::PropertyString','CurrentPCB_SHA256');S[boardkey].CurrentPCB_SHA256=PCB
 hits=[];near=[]
 for k,s in changed.items():
  for kk,obj in S.items():
   if kk==k or kk==boardkey:continue
   v=hit(s,obj.Shape)
   if v>1e-7:hits.append({'moved':k,'other':kk,'volume_mm3':v})
   near.append({'moved':k,'other':kk,'gap_mm':s.distToShape(obj.Shape)[0]})
 require(not hits,'new body collision')
 static={k.split('_')[1]for k in S if k.startswith('INSTALL_')};operation={k.removeprefix('UNQUALIFIED_OPERATION_')for k in ops};require(static|operation==refs and not(static&operation),'103 refs coverage');require(sum(k.startswith('INSTALL_')for k in S)==104,'104 full entities')
 for k,obj in S.items():
  if k in changed:continue
  require(abs(obj.Shape.Volume-original[k].Volume)<1e-7 and bb(obj.Shape)==bb(original[k]),'unchanged geometry')
 target=O/(ctx+'_data8_support_RESEARCH_NOFAB.FCStd');d.recompute();d.saveAs(str(target));Part.export(list(S.values()),str(O/(ctx+'_data8_support_RESEARCH_NOFAB.step')));A.closeDocument(d.Name)
 reopened=A.openDocument(str(target));new={o.Label:o.Shape for o in reopened.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};require(set(new)==set(S),'saved shape labels');require({o.Label:o.Evidence for o in reopened.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')}==ops,'saved operation metadata')
 for k,s in new.items():
  expected=changed[k]if k in changed else original[k];require(max(abs(a-b)for a,b in zip(bb(s),bb(expected)))<1e-7 and abs(s.Volume-expected.Volume)<1e-6,'saved shape dimensions')
 step=Part.Shape();step.read(str(O/(ctx+'_data8_support_RESEARCH_NOFAB.step')));total=sum(s.Volume for s in new.values());residual=step.Volume-total;require(step.isValid()and len(step.Solids)==sum(len(s.Solids)for s in new.values())and abs(residual)<.005,'STEP exchange')
 row={'context':ctx,'source_path':str(q.relative_to(W)),'source_sha256':before,'saved_path':target.name,'native_sha256':PCB,'full_static_entities':104,'static_refs':len(static),'operation_refs':sorted(operation),'all103_native_contracts_bound':True,'unchanged_board_and_supports':True,'unchanged_objects_except_two_bodies':len(S)-2,'body_changes':{k:{'before':bb(original[k]),'after':bb(s)}for k,s in changed.items()},'hits':hits,'nearest':sorted(near,key=lambda r:r['gap_mm'])[:6],'STEP_valid':step.isValid(),'STEP_solids':len(step.Solids),'STEP_volume_exchange_residual_mm3':residual,'saved_reopened_shapes_match':True}
 out.append(row);A.closeDocument(reopened.Name);require(sha(q)==before,'source changed')
(O/'results.json').write_text(json.dumps({'status':'RESEARCH_ONLY_INTEGRATED_NOMINAL_GEOMETRY','pcb_sha256':PCB,'native_contract_report_sha256':sha(M/'results.json'),'contexts':out},indent=2)+'\n')
