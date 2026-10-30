from pathlib import Path
import os,sys,json
os.environ['XDG_CONFIG_HOME']='/tmp/indesupport1258';sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
O=Path(__file__).resolve().parent;W=O.parent;C=W/'assembly_support_tongue_variant_20261030_1251/corrected_connected';BASE=W/'assembly_outline_sync_20261030_1239';B=2.264793176328504

def req(x,msg):
 if not x:raise RuntimeError(msg)
def load(p):
 d=A.openDocument(str(p));s={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};g={o.Label:o.Evidence for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')};A.closeDocument(d.Name);return s,g
rows=[]
for ctx in ['RevD_BENCH','ACCESS19','ACCESS20']:
 s,g=load(C/(ctx+'_support_proposal_NOFAB.FCStd'));old,og=load(BASE/(ctx+'_exact_outline_NOFAB.FCStd'));req(g==og and len(g)==6,'operation metadata');keys=['Common_base']if ctx=='RevD_BENCH'else['Lower_common_datum_STUDY','Upper_nonlocating_cover_STUDY','COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED'];board=s['Native_outline_dcbd_99p8_t0p93_NOFAB'];env={k:v for k,v in s.items()if k.startswith('INSTALL_')};req(len(env)==104,'104');j=next(v for k,v in env.items()if k.startswith('INSTALL_J202_'));head=s[keys[0]]
 req(abs(head.distToShape(j)[0]-.2)<1e-8,'J202 distance');area=sum(a.common(b).Area for a in head.Faces for b in board.Faces if abs(a.BoundBox.ZMin-33.7)<1e-7 and abs(a.BoundBox.ZMax-33.7)<1e-7 and abs(b.BoundBox.ZMin-33.7)<1e-7 and abs(b.BoundBox.ZMax-33.7)<1e-7);req(abs(area-.8)<1e-8,'actual full head area')
 for k in keys:req(s[k].isValid()and len(s[k].Solids)==1,'valid connected changed solid')
 for k in s:
  if k in keys:continue
  a,b=s[k],old[k];req(a.exportBrepToString()==b.exportBrepToString()or a.cut(b).Volume+b.cut(a).Volume<1e-8,'unrelated saved geometry changed '+k)
 # Saved-native candidate difference to regenerated candidate, when available, is checked separately.
 # Negative uses preserved earlier zero-gap proposal, NOT accepted as usable support.
 zero,zg=load(W/'assembly_support_proposal_20261030_1238/corrected_connected'/(ctx+'_support_proposal_NOFAB.FCStd'));neg=zero[keys[0]].distToShape(j)[0];req(neg<1e-8 and not neg>=.2-1e-8,'zero-gap control not rejected')
 # No gap-area threshold relaxation for native contact.
 rows.append({'context':ctx,'head_actual_face_contact_area':area,'J202_full_budget_gap_mm':head.distToShape(j)[0],'modified_valid_single_solid_count':len(keys),'unchanged_other_geometry_count':len(s)-len(keys),'operation_metadata_identical':True,'earlier_zero_margin_negative_gap':neg,'negative_rejected_by_0p2_gate':True})
(O/'independent_saved.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
