import json,sys
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
from patch_supports import B,box,ROOT
R=Path(__file__).resolve().parent/'corrected_connected';rows=[]
for context in ['RevD_BENCH','ACCESS19','ACCESS20']:
 p=R/(context+'_support_proposal_NOFAB.FCStd');d=A.openDocument(str(p));O={o.Label:o.Shape for o in d.Objects if hasattr(o,'Shape')}
 board=O['Native_outline_dcbd_99p8_t0p93_NOFAB'];lower=O['Common_base' if context=='RevD_BENCH' else 'Lower_common_datum_STUDY']
 head=lower.common(box(-7.01,-4.99,B-.01,B+.94,33.69,33.71));intersection=head.common(board)
 faces_head=[f for f in head.Faces if abs(f.BoundBox.ZMin-33.7)<1e-6 and abs(f.BoundBox.ZMax-33.7)<1e-6]
 faces_board=[f for f in board.Faces if abs(f.BoundBox.ZMin-33.7)<1e-6 and abs(f.BoundBox.ZMax-33.7)<1e-6]
 area=sum(a.common(b).Area for a in faces_head for b in faces_board)
 row=dict(context=context,head_distance=head.distToShape(board)[0],head_contact_face_area=area,head_common_volume=intersection.Volume)
 if context.startswith('ACCESS'):
  frame=O['COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED'];toe=frame.common(box(6.9,7.96,B+.16,B+.87,118.5,119.5));catch=lower.common(box(6.75,7,B-.8,B-.099,118,120));section=board.common(box(6.75,7,B,B+.93,118,120))
  row.update(right_toe_distance=toe.distToShape(section)[0],right_toe_common_volume=toe.common(board).Volume,secondary_catch_gap=catch.distToShape(section)[0],secondary_catch_projected_area=.25*2)
 
 if context.startswith('ACCESS'):
  source=A.openDocument(str(ROOT/'assembly_outline_sync_20261030_1239'/(context+'_exact_outline_NOFAB.FCStd')))
  old=next(o.Shape for o in source.Objects if o.Label=='Lower_common_datum_STUDY')
  row['new_head_block_old_root_overlap_mm3']=old.common(box(-7.2,-5,B+.2,B+.6,31.5,33.7)).Volume
  A.closeDocument(source.Name)
 else:
  source=A.openDocument(str(ROOT/'assembly_outline_sync_20261030_1239'/(context+'_exact_outline_NOFAB.FCStd')))
  old=next(o.Shape for o in source.Objects if o.Label=='Common_base')
  row['new_head_block_old_root_overlap_mm3']=old.common(box(-7.2,-5,B+.2,B+.6,30.5,33.7)).Volume
  A.closeDocument(source.Name)
 rows.append(row);A.closeDocument(d.Name)
(R/'contact_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
