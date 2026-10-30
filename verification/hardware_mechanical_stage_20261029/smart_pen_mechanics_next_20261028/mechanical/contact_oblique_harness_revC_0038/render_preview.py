import bpy,json,os
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__));bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for v in json.load(open(R+'/preview_meshes.json')):
 m=bpy.data.meshes.new(v['name']);m.from_pydata(v['v'],[],v['f']);m.update();o=bpy.data.objects.new(v['name'],m);bpy.context.collection.objects.link(o);mat=bpy.data.materials.new(v['name']);n=v['name'];color=(.55,.58,.65,1)
 if n=='Slider':color=(.92,.43,.12,1)
 elif 'Housing' in n:color=(.27,.46,.62,1)
 elif 'PCB' in n:color=(.12,.50,.27,1)
 elif 'SPVE_body' in n:color=(.12,.12,.14,1)
 elif 'Shim' in n:color=(.75,.40,.65,1)
 elif 'Harness' in n:color=(.82,.74,.2,1)
 mat.diffuse_color=color;o.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.94,.94,.94)
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO';c.location=(-30,25,65);target=Vector((0,-.5,77));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=16;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.filepath=R+'/cassette_cutaway_PREVIEW.png';bpy.ops.render.render(write_still=True)
