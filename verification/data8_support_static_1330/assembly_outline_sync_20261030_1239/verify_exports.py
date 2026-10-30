from pathlib import Path
import sys,json,hashlib
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
O=Path(__file__).resolve().parent;rows=[]
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 d=A.openDocument(str(O/(ctx+'_exact_outline_NOFAB.FCStd')));ss=[o.Shape for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()];step=Part.Shape();step.read(str(O/(ctx+'_exact_outline_NOFAB.step')))
 native_volume=sum(s.Volume for s in ss);err=abs(step.Volume-native_volume)
 if err>max(.002,abs(native_volume)*1e-6) or not step.isValid():raise RuntimeError((ctx,err,'STEP invalid or volume mismatch'))
 b=next(o.Shape for o in d.Objects if o.Label=='Native_outline_dcbd_99p8_t0p93_NOFAB');shift=b.copy();shift.translate(A.Vector(0,0,-1.7))
 if shift.cut(b).Volume<1:raise RuntimeError('negative datum-shift control failed')
 rows.append({'context':ctx,'step_valid':step.isValid(),'cad_sum_volume_mm3':native_volume,'exchange_volume_tolerance_mm3':max(.002,abs(native_volume)*1e-6),'step_solids':len(step.Solids),'cad_solid_count':sum(len(s.Solids)for s in ss),'step_vs_cad_sum_volume_error_mm3':err,'negative_shift_added_volume_mm3':shift.cut(b).Volume});A.closeDocument(d.Name)
(O/'export_verification.json').write_text(json.dumps(rows,indent=2)+'\n')
