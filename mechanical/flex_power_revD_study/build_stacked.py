import sys,json,math
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad-python3/lib'])
import FreeCAD as A,Part
V=A.Vector;R=Path(__file__).resolve().parent
source=R/'D18_AXIAL_260_CONDITIONAL_NOFAB.FCStd';d=A.openDocument(str(source));d.Label='D18_STACKED_213_CONDITIONAL_NOFAB'
for o in d.Objects:
 if o.Name.startswith('Main_') or o.Name=='Mainboard_XCLK5_12x95':s=o.Shape.copy();s.translate(V(0,1.9,0));o.Shape=s
 elif o.Name=='Power14x45_THICKNESS_BUDGET4p15':s=o.Shape.copy();s.translate(V(0,-.625,-110));o.Shape=s
 elif o.Name=='USB12x20_HEIGHT_BUDGET5':s=o.Shape.copy();s.translate(V(0,0,-47));o.Shape=s
 elif o.Name=='Barrel_OD18_wall1p2_reference':o.Shape=Part.makeCylinder(9,183,V(0,0,30)).cut(Part.makeCylinder(7.8,185,V(0,0,29)))
physical=[o for o in d.Objects if o.Name not in ['RF_reserved_UNQUALIFIED','Barrel_OD18_wall1p2_reference']]
inside=Part.makeCylinder(7.8,215,V(0,0,-1));collisions=[];outside={};radial={}
for i,o in enumerate(physical):
 s=o.Shape;outside[o.Name]=s.cut(inside).Volume
 # Tessellation distance checks use vertices of nominal prisms/cylinders. Power/main are rectangles; exact corner radii.
 if o.Name.startswith('Main_') or o.Name.startswith('Mainboard') or o.Name.startswith('Power') or o.Name.startswith('USB'):
  b=s.BoundBox;radial[o.Name]=7.8-max(math.hypot(x,y) for x in [b.XMin,b.XMax] for y in [b.YMin,b.YMax])
 for other in physical[i+1:]:
  v=s.common(other.Shape).Volume
  if v>1e-6:collisions.append([o.Name,other.Name,v])
power=d.getObject('Power14x45_THICKNESS_BUDGET4p15').Shape
rpt=dict(status='NOFAB; closest exact rectangular corner margin below chosen0.30budget',length=213,compared_axial_260_reduction=47,compared_old_axial_210_increase=3,power_z=[82,127],power_y=[-2.7,1.45],mainboard_y=[2.9,3.7],mainboard_all_actual_parts=74,still_missing_footprints=16,outside_mm3=outside,collisions=collisions,rectangular_corner_radial_clearance_mm=radial,min_rectangular_margin_mm=min(radial.values()),power_to_back_R105_mm=power.distToShape(d.getObject('Main_R105').Shape)[0],power_to_back_R214_mm=power.distToShape(d.getObject('Main_R214').Shape)[0],power_to_contact_mm=power.distToShape(d.getObject('Compact_contact_REQUIRED').Shape)[0],power_to_battery_mm=power.distToShape(d.getObject('Battery_complete_REQUIRED_12p2x49').Shape)[0])
d.recompute();d.saveAs(str(R/'D18_STACKED_213_CONDITIONAL_NOFAB.FCStd'));Part.export(d.Objects,str(R/'D18_STACKED_213_CONDITIONAL_NOFAB.step'));A.closeDocument(d.Name)
d=A.openDocument(str(R/'D18_STACKED_213_CONDITIONAL_NOFAB.FCStd'));rpt['native_valid']=all(o.Shape.isValid() for o in d.Objects if hasattr(o,'Shape'));rpt['native_objects']=len(d.Objects);A.closeDocument(d.Name)
s=Part.Shape();s.read(str(R/'D18_STACKED_213_CONDITIONAL_NOFAB.step'));rpt['step_valid']=s.isValid();rpt['step_solids']=len(s.Solids)
(R/'stacked213_validation.json').write_text(json.dumps(rpt,indent=2));print(json.dumps({k:v for k,v in rpt.items() if k not in ['outside_mm3','rectangular_corner_radial_clearance_mm']},indent=2))
