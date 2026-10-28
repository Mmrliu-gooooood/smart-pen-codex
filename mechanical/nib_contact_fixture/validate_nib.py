import os,sys,json
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part,Mesh
R=os.path.dirname(os.path.abspath(__file__));out={}
d=A.openDocument(R+'/D1_nib_contact_fixture.FCStd');d.recompute()
out['FCStd']={'objects':len(d.Objects),'all_shapes_valid':all(o.Shape.isValid() for o in d.Objects)}
s=Part.Shape();s.read(R+'/D1_nib_contact_fixture.step');out['STEP']={'valid':s.isValid(),'solids':len(s.Solids)}
for f in sorted(os.listdir(R+'/stl')):
 m=Mesh.Mesh(R+'/stl/'+f);out[f]={'closed':m.isSolid(),'nonmanifold':m.hasNonManifolds(),'nonuniform_orientation':m.hasNonUniformOrientedFacets(),'volume_mm3':m.Volume,'bbox_mm':[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength]}
 assert m.isSolid() and not m.hasNonManifolds() and not m.hasNonUniformOrientedFacets(),f
j=json.load(open(R+'/geometry_validation.json'))
for k in ['rigid_collisions','motion_collisions','hardware_collisions','service_collisions']:assert j[k]==[],(k,j[k])
assert j['overstroke_0p70_interception_mm3']>0 and j['stop_contact_distance_mm']<1e-6
json.dump(out,open(R+'/reopen_validation.json','w'),indent=2);print(json.dumps(out,indent=2))
