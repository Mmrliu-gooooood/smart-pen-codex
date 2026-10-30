import bpy,json,os
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__));bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for v in json.load(open(R+'/preview_meshes.json')):
 m=bpy.data.meshes.new(v['name']);m.from_pydata(v['v'],[],v['f']);m.update();o=bpy.data.objects.new(v['name'],m);bpy.context.collection.objects.link(o);mat=bpy.data.materials.new(v['name']);n=v['name'];color=(.63,.67,.70,1)
 if n.startswith('REF_CTX_'):color=(.15,.18,.21,1)
 if n=='REF_CTX_main_board':color=(.16,.52,.32,1)
 elif 'Housing' in n:color=(.17,.37,.55,1)
 elif 'keeper' in n or 'collar' in n or 'Fork_jaw' in n:color=(.23,.48,.67,1)
 elif 'shim' in n or 'spacer' in n:color=(.75,.44,.65,1)
 elif 'Harness' in n:color=(.85,.72,.16,1)
 elif n=='REF_CTX_power':color=(.85,.49,.18,1)
 mat.diffuse_color=color;o.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.94,.94,.94)
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO';c.location=(95,90,180);target=Vector((0,-3,80));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=172;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.filepath=R+'/common_bench_overview_PREVIEW.png';bpy.ops.render.render(write_still=True)
# Local cutaway hides mainboard/component context only to reveal cassette common mount; CAD unchanged.
for o in bpy.context.scene.objects:
 if o.type=='MESH'and o.name.startswith('REF_CTX_'):o.hide_render=True
c.location=(30,30,90);target=Vector((0,-3,70));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=35;s.render.filepath=R+'/common_bench_cassette_CUTAWAY.png';bpy.ops.render.render(write_still=True)
