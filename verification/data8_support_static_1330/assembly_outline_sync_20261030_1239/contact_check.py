from pathlib import Path
import sys,json
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
O=Path(__file__).resolve().parent;B=2.264793176328504;F=B+.93
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,A.Vector(x0,y0,z0))
def patch(x0,x1,z0,z1,y=B):return Part.Face(Part.makePolygon([A.Vector(x0,y,z0),A.Vector(x1,y,z0),A.Vector(x1,y,z1),A.Vector(x0,y,z1),A.Vector(x0,y,z0)]))
rows=[]
for ctx in ['RevD_BENCH','ACCESS19','ACCESS20']:
 d=A.openDocument(str(O/(ctx+'_exact_outline_NOFAB.FCStd')));S={o.Label:o.Shape for o in d.Objects if hasattr(o,'Shape')};board=S['Native_outline_dcbd_99p8_t0p93_NOFAB'];old=box(-7,7,B,F,32,133.5)
 label='Lower_common_datum_STUDY'if ctx.startswith('ACCESS')else next(k for k in S if 'Common_base' in k)
 support=S[label];head=support.common(box(-7,-5,B,B+.4,31.5,32));r={'context':ctx,'head_feature_volume':head.Volume,'head_old_distance_mm':old.distToShape(head)[0],'head_exact_distance_mm':board.distToShape(head)[0],'B_support_patches':[]}
 for side,z in [(-1,45),(1,45),(-1,131 if ctx.startswith('ACCESS')else 95),(1,131 if ctx.startswith('ACCESS')else 95)]:
  xa,xb=(-7,-6.75)if side<0 else(6.75,7);p=patch(xa,xb,z-1,z+1);r['B_support_patches'].append({'side':side,'Z':z,'old_board_patch_mm2':p.common(old).Area,'new_board_patch_mm2':p.common(board).Area,'support_face_contact_mm2':p.common(support).Area})
 if ctx.startswith('ACCESS'):
  frame=S['COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED'];toe=frame.common(box(6.9,7.7,B+.265,B+.665,130.7,131.3));r['RF_lateral_toe']={'old_distance':toe.distToShape(old)[0],'exact_distance':toe.distToShape(board)[0],'feature_volume':toe.Volume}
  tail=frame.common(box(-5.85,-5.15,B+.265,B+.665,133.4,134.15));r['tail_toe_exact_distance']=tail.distToShape(board)[0]
 if abs((r['head_exact_distance_mm']-r['head_old_distance_mm'])-1.7)>1e-6:raise RuntimeError(r)
 rows.append(r);A.closeDocument(d.Name)
(O/'contact_results.json').write_text(json.dumps(rows,indent=2)+'\n')
