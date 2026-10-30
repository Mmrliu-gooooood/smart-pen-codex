import bpy,json,os,sys
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent;name=sys.argv[-1];section='section95' in name
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
colors={'Housing_candidate':(.58,.64,.7,1),'RevC_board_12x95x0p8':(.12,.48,.28,1),'Complete_battery_pack_BUDGET':(.18,.48,.76,1),'D1_refill_nominal':(.73,.73,.76,1),'Contact_cassette_REQUIRED_ENVELOPE':(.85,.38,.25,1),'SC031GS_head_H6p5_candidate':(.58,.36,.65,1),'Tail_power_USB_REQUIRED_BUDGET':(.45,.3,.6,1)}
for item in json.loads((R/(name+'_mesh.json')).read_text()):
 me=bpy.data.meshes.new(item['name']);me.from_pydata(item['v'],[],item['f']);me.update();ob=bpy.data.objects.new(item['name'],me);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new(item['name']);mat.diffuse_color=colors.get(item['name'],(.78,.57,.25,1));ob.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.95,.95,.95)
bpy.ops.object.camera_add();c=bpy.context.object;s.camera=c;c.data.type='ORTHO'
if section:target=Vector((0,0,95));c.location=(0,0,200);c.data.ortho_scale=23;s.render.resolution_x=1200;s.render.resolution_y=1200
else:target=Vector((0,0,105 if name.startswith('A18') else 90));c.location=(150,-90,115);c.data.ortho_scale=235 if name.startswith('A18') else 205;s.render.resolution_x=700;s.render.resolution_y=1500
c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_percentage=100;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
