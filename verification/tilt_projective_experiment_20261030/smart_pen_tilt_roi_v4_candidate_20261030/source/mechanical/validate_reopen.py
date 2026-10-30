import sys,json,os
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part,Mesh
root=os.path.dirname(__file__);checks={}
for name in ['optical_bench','pen18_envelope_NOT_FOR_PRINT','pen18_compact170_NOT_FOR_PRINT']:
 d=A.openDocument(root+'/'+name+'.FCStd');d.recompute()
 checks[name]={'objects':len(d.Objects),'valid':all(o.Shape.isValid() for o in d.Objects)}
 A.closeDocument(d.Name)
 s=Part.Shape();s.read(root+'/'+name+'.step');checks[name]['step_valid']=s.isValid();checks[name]['step_solids']=len(s.Solids)
for f in os.listdir(root+'/stl'):
 m=Mesh.Mesh(root+'/stl/'+f);checks[f]={'closed':m.isSolid(),'facets':m.CountFacets,'volume_mm3':m.Volume,'nonmanifold':m.hasNonManifolds(),'nonuniform_orientation':m.hasNonUniformOrientedFacets(),'bbox_mm':[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength]}
json.dump(checks,open(root+'/reopen_validation.json','w'),indent=2);print(checks)
