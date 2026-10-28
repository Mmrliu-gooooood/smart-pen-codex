import sys,os,json,math
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
R=os.path.dirname(os.path.abspath(__file__));d=A.openDocument(R+'/D1_nib_contact_fixture.FCStd');out=[]
for o in d.Objects:
 if o.Name in ['Spring_installed_envelope','SoftGrip_loaded_envelope']:continue
 s=o.Shape;v,f=s.tessellate(.35 if o.Name=='Spring_visual_ONLY' else .10);out.append({'name':o.Name,'v':[[a.x,a.y,a.z] for a in v],'f':f})
json.dump(out,open(R+'/preview_meshes.json','w'))

out=[]
for o in d.Objects:
 if o.Name in ['Spring_installed_envelope','SoftGrip_loaded_envelope']:continue
 if o.Name.startswith('M3') and o.Shape.BoundBox.YMax<0:continue
 s=o.Shape
 if o.Name in ['NoseGuide','FrontGuide','RearGuide','HardStop','Slider']:s=s.cut(Part.makeBox(120,18,45,A.Vector(-5,-18,0)))
 v,f=s.tessellate(.35 if o.Name=='Spring_visual_ONLY' else .10)
 out.append({'name':o.Name,'v':[[a.x,a.y,a.z] for a in v],'f':f})
json.dump(out,open(R+'/section_meshes.json','w'))
