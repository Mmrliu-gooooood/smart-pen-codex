from pathlib import Path
import sys,json,os
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;O=Path(os.environ.get('DATA8_CAD_OUTPUT',str(R)));B=2.264793176328504;rows=[]
def box(a,b,c,d,e,f):return Part.makeBox(b-a,d-c,f-e,A.Vector(a,c,e))
def face(x0,x1,z0,z1):return Part.Face(Part.makePolygon([A.Vector(x0,B,z0),A.Vector(x1,B,z0),A.Vector(x1,B,z1),A.Vector(x0,B,z1),A.Vector(x0,B,z0)]))
def require(v,msg):
 if not v:raise RuntimeError(msg)
for ctx in ['RevD_BENCH','ACCESS19','ACCESS20']:
 d=A.openDocument(str(O/(ctx+'_data8_support_RESEARCH_NOFAB.FCStd')));S={o.Label:o.Shape for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};board=S['Native_outline_dcbd_99p8_t0p93_NOFAB'];lower=S['Common_base'if ctx=='RevD_BENCH'else'Lower_common_datum_STUDY'];J202=next(s for k,s in S.items()if k.startswith('INSTALL_J202_'))
 head=lower.common(box(-7.01,-4.99,B-.01,B+.94,33.69,33.71));hf=[f for f in head.Faces if abs(f.BoundBox.ZMin-33.7)<1e-6 and abs(f.BoundBox.ZMax-33.7)<1e-6];bf=[f for f in board.Faces if abs(f.BoundBox.ZMin-33.7)<1e-6 and abs(f.BoundBox.ZMax-33.7)<1e-6];area=sum(a.common(b).Area for a in hf for b in bf);gap=lower.distToShape(J202)[0];require(abs(area-.8)<1e-6 and abs(gap-.2)<1e-6,'head/J202')
 row={'context':ctx,'head_contact_area_mm2':area,'head_board_distance_mm':head.distToShape(board)[0],'head_board_overlap_mm3':head.common(board).Volume,'whole_lower_J202_gap_mm':gap}
 labels=['Common_base']if ctx=='RevD_BENCH'else['Lower_common_datum_STUDY','Upper_nonlocating_cover_STUDY','COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED'];dist=[]
 for k in labels:
  s=S[k];require(s.isValid()and len(s.Solids)==1,'support validity');ds=[{'ref':kk,'distance_mm':s.distToShape(t)[0]}for kk,t in S.items()if kk.startswith('INSTALL_')];require(len(ds)==104 and all(x['distance_mm']>1e-8 for x in ds),'support/full envelope contact');dist.append({'part':k,'full_envelopes_checked':len(ds),'nearest':sorted(ds,key=lambda x:x['distance_mm'])[:5]})
 row['support_fullbudget_clearance_checks']=dist
 if ctx.startswith('ACCESS'):
  frame=S[labels[2]];toe=frame.common(box(6.9,7.96,B+.16,B+.87,118.5,119.5));section=board.common(box(6.75,7,B,B+.93,118,120));catch=lower.common(box(6.75,7,B-.8,B-.099,118,120));tail=frame.common(box(-5.85,-5.15,B+.265,B+.665,133.4,134.15));primary=[]
  for side,z in [(-1,45),(1,45),(-1,131)]:
   xa,xb=(-7,-6.75)if side<0 else(6.75,7);patch=face(xa,xb,z-1,z+1);a=patch.common(lower).Area;ab=patch.common(board).Area;require(abs(a-.5)<1e-7 and abs(ab-.5)<1e-7,'primary support');primary.append({'side':side,'Z':z,'board_patch_area':ab,'lower_face_area':a})
  row.update(RF_side_toe_distance_mm=toe.distToShape(section)[0],secondary_catch_gap_mm=catch.distToShape(section)[0],tail_toe_distance_mm=tail.distToShape(board)[0],primary_B_patches=primary)
  require(row['RF_side_toe_distance_mm']<1e-7 and abs(row['secondary_catch_gap_mm']-.1)<1e-7 and row['tail_toe_distance_mm']<1e-7,'retention contacts')
 rows.append(row);A.closeDocument(d.Name)
(O/'saved_contact_results.json').write_text(json.dumps(rows,indent=2)+'\n')
