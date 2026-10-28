import bpy,json,os,sys
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__));section='--section' in sys.argv
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
colors={'Base':(.48,.55,.63,1),'NoseGuide':(.25,.44,.6,1),'FrontGuide':(.25,.44,.6,1),'RearGuide':(.25,.44,.6,1),'Slider':(.9,.5,.1,1),'HardStop':(.8,.25,.2,1),'SwitchCarrier':(.55,.45,.65,1),'Switch_testPCB_template':(.1,.5,.25,1),'D1_nominal_envelope':(.7,.7,.72,1),'Spring_visual_ONLY':(.8,.8,.8,1),'HDT_body_reference':(.12,.12,.12,1),'HDT_actuator_motion_reference':(.78,.8,.82,1)}
for item in json.load(open(R+('/section_meshes.json' if section else '/preview_meshes.json'))):
 mesh=bpy.data.meshes.new(item['name']);mesh.from_pydata(item['v'],[],item['f']);mesh.update();ob=bpy.data.objects.new(item['name'],mesh);bpy.context.collection.objects.link(ob)
 mat=bpy.data.materials.new(item['name']);mat.diffuse_color=colors.get(item['name'],(.3,.32,.36,1));ob.data.materials.append(mat)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.92,.92,.92)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
views=[('section',(40,-130,90),(70,0,20),74)] if section else [('assembly',(130,-160,115),(47,0,15),140),('mechanism_detail',(115,-120,82),(70,0,20),64)]
for name,location,target,scale in views:
 cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=R+'/'+name+'.png';bpy.ops.render.render(write_still=True)
