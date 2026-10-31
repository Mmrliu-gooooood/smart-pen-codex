from pathlib import Path
import sys,json,hashlib,copy
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
O=Path(__file__).resolve().parent;W=O.parent;R=W/'recovery_inputs59_20261031';C=R/'assembly_data8_support_sync_20261030_1314';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();M=C/'manifest.json'
if sha(M)!='ec6805bee4836155277582c691aabfe3ba9106bf35e75a4c0d524af3c84b519a':raise RuntimeError('restored CAD manifest')
man=json.load(open(M))['files'];N=json.load(open(O/'native_contracts.json'));fps={r['ref']:r for r in N['rows']};L={r['ref']:r for r in json.load(open(R/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']};contexts=[]
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 q=C/f'{ctx}_data8_support_RESEARCH_NOFAB.FCStd'
 if sha(q)!=man[q.name]:raise RuntimeError('saved CAD exact hash')
 d=A.openDocument(str(q));rows=[];ops=[]
 for obj in d.Objects:
  if obj.Label.startswith('UNQUALIFIED_OPERATION_'):ops.append(obj.Label.removeprefix('UNQUALIFIED_OPERATION_'));continue
  if not obj.Label.startswith('INSTALL_'):continue
  ref=obj.Label.split('_')[1];b=obj.Shape.BoundBox;native=[b.XMin+7,127-b.ZMax,b.XMax+7,127-b.ZMin]
  if not obj.Shape.isValid():raise RuntimeError('invalid saved envelope')
  bases=[e.get('basis')for c in L[ref]['contexts']if c['context']==ctx for e in c['entities']]
  rows.append({'ref':ref,'side':fps[ref]['side'],'entity':obj.Label,'xy_bounds':native,'height':b.YLength,'cad_bounds_XYZ':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'basis':bases or ['retained saved-CAD provisional full budget; not measured/manufacturing qualified'],'native_pose':fps[ref]['pose'],'native_footprint':fps[ref]['footprint']})
 if len(rows)!=104 or {r['ref']for r in rows}|set(ops)!=set(fps)or len(ops)!=6:raise RuntimeError('104 static/103 refs/six gates')
 contexts.append({'context':ctx,'source_cad_sha256':sha(q),'rows':sorted(rows,key=lambda x:x['entity']),'unqualified_operations':sorted(ops)});A.closeDocument(d.Name)
base=contexts[0]['rows'];diff=[]
for c in contexts[1:]:
 for a,b in zip(base,c['rows']):
  if a['entity']!=b['entity']or max(abs(x-y)for x,y in zip(a['xy_bounds']+[a['height']],b['xy_bounds']+[b['height']]))>1e-7:diff.append({'context':c['context'],'base':a,'other':b})
if diff:raise RuntimeError('contexts differ; export explicit union rather than silently choose one')
for ref,expected in [('R217',[2.18,28.22,2.82,29.78]),('R210',[9.275,27.525,11.725,28.475]),('U101',[2.25,6.25,9.75,13.75])]:
 r=next(r for r in base if r['ref']==ref)
 if max(abs(a-b)for a,b in zip(r['xy_bounds'],expected))>1e-7:raise RuntimeError('expected restored full envelope')
out={'status':'NEW_OCT31_EXPORT_FROM_VERIFIED_RESTORED_BYTES_NOFAB_NOPOWER','basis_sha256':N['pcb_sha256'],'source_CAD_manifest_sha256':sha(M),'all_static_rectangles':base,'unqualified_operation_refs':contexts[0]['unqualified_operations'],'all_four_context_envelopes_equal':True,'contexts':[{k:v for k,v in c.items()if k!='rows'}for c in contexts]}
(O/'full104_4d7d.json').write_text(json.dumps(out,indent=2)+'\n')
proposed=copy.deepcopy(out);r=next(r for r in proposed['all_static_rectangles']if r['ref']=='R503');r['xy_bounds']=[6.775,16.025,9.225,16.975];r['native_pose']=[8,16.5,0];r['proposal_only']=True;r['cad_bounds_XYZ']=None;proposed['status']='PROPOSED_R503_OVERLAY_ONLY_NOT_ACCEPTED_NATIVE';proposed['proposed_poses']={'R503':[8,16.5,0]};(O/'full104_proposed_R503.json').write_text(json.dumps(proposed,indent=2)+'\n')
print('Exported104 identical full budgets across4 exact saved contexts;103refs/six operational gates; proposedR503 separate')
