import sys,json,hashlib,os
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parent
reports=json.loads((R/'assembly_validation.json').read_text());out=[]
for rep in reports:
 name=rep['config']['name'];d=A.openDocument(str(R/(name+'.FCStd')));d.recompute()
 shapes=[o for o in d.Objects if hasattr(o,'Shape')];rec=dict(name=name,FCStd_shapes=len(shapes),FCStd_all_valid=all(o.Shape.isValid() for o in shapes),zero_nominal_collisions=not rep['pair_collisions'] and not rep['housing_collisions'])
 s=Part.Shape();s.read(str(R/(name+'.step')));rec.update(STEP_valid=s.isValid(),STEP_solids=len(s.Solids));assert rec['FCStd_all_valid'] and rec['STEP_valid'] and rec['zero_nominal_collisions'];out.append(rec)
 if name in ['A18_axial_210','C19_parallel_180_CONDITIONAL','D20_parallel_180_budget']:
  for section in [False,True]:
   mesh=[]
   for o in shapes:
    if o.Name in ['Cell10440_only','Refill_service_sweep','RF_region_UNQUALIFIED','Optical_rays_theta45_ROI6_ONLY'] or 'DNP_RESERVE' in o.Name:continue
    s=o.Shape
    if section:s=s.common(Part.makeBox(40,40,.25,A.Vector(-20,-20,94.875)))
    elif o.Name=='Housing_candidate':s=s.cut(Part.makeBox(30,60,230,A.Vector(0,-30,-5)))
    if s.isNull() or s.Volume<1e-8:continue
    v,f=s.tessellate(.15);mesh.append(dict(name=o.Name,v=[[a.x,a.y,a.z] for a in v],f=f))
   (R/(name+('_section95' if section else '_cutaway')+'_mesh.json')).write_text(json.dumps(mesh))
 A.closeDocument(d.Name)
d=A.openDocument(str(R/'FPC_bend_tests_NOT_ASSEMBLY.FCStd'));d.recompute();s=Part.Shape();s.read(str(R/'FPC_bend_tests_NOT_ASSEMBLY.step'));assert all(o.Shape.isValid() for o in d.Objects) and s.isValid();out.append(dict(name='FPC_bend_tests_NOT_ASSEMBLY',FCStd_all_valid=True,STEP_valid=True,STEP_solids=len(s.Solids),intentional_mutually_exclusive_routes=True));A.closeDocument(d.Name)
(R/'reopen_validation.json').write_text(json.dumps(out,indent=2));print(out)
