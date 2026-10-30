import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'assembly_support_tongue_variant_20261030_1251'))
from patch_supports import B,box,corrected_frame,SOURCE
R=Path(__file__).resolve().parent;C=ROOT/'assembly_support_tongue_variant_20261030_1251/corrected_connected';rows=[]
for ctx in ['RevD_BENCH','ACCESS19','ACCESS20']:
 docs=[A.openDocument(str(p))for p in [ROOT/'assembly_outline_sync_20261030_1239'/(ctx+'_exact_outline_NOFAB.FCStd'),C/(ctx+'_support_proposal_NOFAB.FCStd')]]
 maps=[{o.Label:o for o in d.Objects}for d in docs];O=maps[1];old=maps[0]
 metadata={k:[old[k].Evidence,O[k].Evidence]for k in old if k.startswith('UNQUALIFIED_OPERATION_')}
 if len(metadata)!=6 or any(a!=b for a,b in metadata.values()):raise RuntimeError('operation gate changed')
 shapes=[o.Shape for o in O.values()if hasattr(o,'Shape')];nativevol=sum(s.Volume for s in shapes);nativecount=sum(len(s.Solids)for s in shapes)
 step=Part.Shape();step.read(str(C/(ctx+'_support_proposal_NOFAB.step')));residual=step.Volume-nativevol
 if not step.isValid()or len(step.Solids)!=nativecount or abs(residual)>.005:raise RuntimeError('STEP exchange exceeds declared bound')
 row=dict(context=ctx,operation_metadata=metadata,step_valid=step.isValid(),step_solids=len(step.Solids),native_solids=nativecount,step_volume_residual_mm3=residual,exchange_tolerance_mm3=.005)
 if ctx.startswith('ACCESS'):
  lo=O['Lower_common_datum_STUDY'].Shape;frame=O['COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED'].Shape;board=O['Native_outline_dcbd_99p8_t0p93_NOFAB'].Shape
  areas=[]
  for x,z in [(-7,45),(6.75,45),(-7,131)]:
   cut=lo.common(box(x,x+.25,B-.01,B+.01,z-1,z+1));lf=[f for f in cut.Faces if abs(f.BoundBox.YMin-B)<1e-7 and abs(f.BoundBox.YMax-B)<1e-7];bf=[f for f in board.Faces if abs(f.BoundBox.YMin-B)<1e-7 and abs(f.BoundBox.YMax-B)<1e-7]
   areas.append(sum(a.common(b).Area for a in lf for b in bf))
  tail=frame.common(box(-5.81,-5.19,B+.16,B+.87,133.1,134.1));taildist=tail.distToShape(board)[0]
  tool=Part.makeCylinder(1.1,5,A.Vector(-6.3,-2.7,28),A.Vector(0,0,1));toolvol=[m['Lower_common_datum_STUDY'].Shape.common(tool).Volume for m in maps]
  anchorvol=[]
  for z in [30.5,136.2]:
   shaft=Part.makeCylinder(.85,7.7,A.Vector(-3.8,-4.3,z),A.Vector(0,1,0));anchorvol.append([m['Lower_common_datum_STUDY'].Shape.common(shaft).Volume for m in maps])
  if any(abs(a-.5)>1e-7 for a in areas)or taildist>1e-8 or any(abs(a-b)>1e-7 for a,b in [toolvol]+anchorvol):raise RuntimeError('retained contact or access geometry changed')
  row.update(primary_B_contact_areas_mm2=areas,tail_toe_distance=taildist,tool_channel_intersection_old_new=toolvol,anchor_channel_intersection_old_new=anchorvol)
 rows.append(row)
 for d in docs:A.closeDocument(d.Name)
 (R/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(ctx,'PASS',flush=True)
ns={'__name__':'original_retainer_source'};exec(compile(SOURCE.read_text(),str(SOURCE),'exec'),ns);states=[]
for name,t,free,stop in [('FREE',.75,True,False),('INSTALLED_0p83',.83,False,False),('INSTALLED_0p93',.93,False,False),('STOP',1.05,False,True)]:
 a=ns['retainer'](t,free,stop);b=corrected_frame(t,free,stop)
 if not b.isValid()or len(b.Solids)!=1 or abs(a.Volume-b.Volume)>1e-6:raise RuntimeError('state geometry change beyond rigid lateral station shift')
 states.append(dict(state=name,valid=b.isValid(),solids=len(b.Solids),volume_difference=b.Volume-a.Volume,lateral_z_old=131,lateral_z_new=119,lateral_toe_min_x=6.95 if free else(7.1 if stop else 7.0)))
(R/'states.json').write_text(json.dumps(states,indent=2)+'\n');print('states PASS',flush=True)
