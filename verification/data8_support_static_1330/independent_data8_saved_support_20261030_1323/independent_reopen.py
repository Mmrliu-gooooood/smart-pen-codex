from pathlib import Path
import os,sys,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/indesaved1323';sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
O=Path(__file__).resolve().parent;W=O.parent;C=W/'assembly_data8_support_sync_20261030_1314';P='4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad'
def req(x,msg):
 if not x:raise RuntimeError(msg)
req(hashlib.sha256((W/'smart_pen_next_20261028/hardware/data_bias_relocate_1242/native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest()==P,'PCB changed')
refs={r['ref']for r in json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']};evidence=json.load(open(W/'assembly_data8_review_20261030_1256/placement_results.json'));rows=[]
def load(path):
 d=A.openDocument(str(path));s={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};g={o.Label:o.Evidence for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')};return d,s,g
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 src=W/'assembly_outline_sync_20261030_1239/RevC_exact_outline_NOFAB.FCStd'if ctx=='RevC'else W/'assembly_support_tongue_variant_20261030_1251/corrected_connected'/f'{ctx}_support_proposal_NOFAB.FCStd';h=hashlib.sha256(src.read_bytes()).hexdigest();req(h==next(x['source_cad_sha256']for x in evidence if x['context']==ctx),'source binding');d,old,og=load(src);A.closeDocument(d.Name);p=C/(ctx+'_data8_support_RESEARCH_NOFAB.FCStd');d,S,g=load(p);req(S.keys()==old.keys(),'shape label set');req(g==og and len(g)==6,'six operations');static={k.split('_')[1]for k in S if k.startswith('INSTALL_')};ops={k.removeprefix('UNQUALIFIED_OPERATION_')for k in g};req(static|ops==refs and not static&ops,'103 coverage');req(sum(k.startswith('INSTALL_')for k in S)==104,'104')
 bind=next(o for o in d.Objects if o.Label=='RESEARCH_ONLY_DATA8_NATIVE_BINDING');req(bind.PCB_SHA256==P,'current native binding');board=next(o for o in d.Objects if o.Label.startswith('Native_outline'));req(board.CurrentPCB_SHA256==P,'board current revision property');req(abs(board.Shape.BoundBox.XLength-14)<1e-8 and abs(board.Shape.BoundBox.ZLength-99.8)<1e-8 and abs(board.Shape.BoundBox.YLength-.93)<1e-8 and abs(board.Shape.Volume-1276.146)<1e-7,'board exact dimensions/volume');changed=[]
 for k,s in S.items():
  expected=old[k].copy()
  if k.startswith('INSTALL_R210_'):expected.translate(A.Vector(9,0,-2));changed.append(k)
  if k.startswith('INSTALL_R217_'):expected.translate(A.Vector(1.4,0,-7.19));changed.append(k)
  req(s.isValid(),'invalid saved solid')
  req(s.exportBrepToString()==expected.exportBrepToString()or s.cut(expected).Volume+expected.cut(s).Volume<1e-8,'not exact expected geometry '+k)
 req(len(changed)==2,'only2 bodies')
 step=Part.Shape();step.read(str(C/(ctx+'_data8_support_RESEARCH_NOFAB.step')));count=sum(len(s.Solids)for s in S.values());err=step.Volume-sum(s.Volume for s in S.values());req(step.isValid()and len(step.Solids)==count and abs(err)<.005,'STEP');rows.append({'context':ctx,'candidate_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_sha256':h,'only_expected_two_translations':changed,'all_other_geometry_identical':True,'103contracts':True,'static_solids':104,'six_operation_evidence_identical':True,'current_PCB_properties':P,'step_valid':True,'step_solids':count,'step_volume_residual':err});A.closeDocument(d.Name);req(hashlib.sha256(src.read_bytes()).hexdigest()==h,'source mutated')
(O/'independent_reopen.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
