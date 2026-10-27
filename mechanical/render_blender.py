import bpy,sys,json,os,math
from mathutils import Vector
r=os.path.dirname(__file__);name=sys.argv[-1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
colors={'Base':(.46,.56,.66,1),'Upright':(.20,.39,.55,1),'Carrier':(.94,.52,.13,1),'Adapter_SC035HGS_candidate':(.85,.71,.38,1),'Shell_d18_wall1p5':(.6,.65,.72,1),'Refill_D1_nominal':(.55,.55,.58,1),'Camera_candidate8x8x8':(.58,.3,.65,1),'Contact_stack_budget':(.9,.3,.2,1),'PICO_narrowPCB_alternative':(.1,.55,.25,1),'Protected10440_cell_alternative':(.15,.5,.8,1),'Thin_mainPCB_11p5x60x2p4_budget':(.1,.55,.25,1),'PowerPCB_12x20x4_budget':(.2,.7,.4,1),'Protected10440_cell_only':(.15,.5,.8,1),'USB_tail_budget':(.85,.6,.15,1)}
for item in json.load(open(r+'/'+name+'_render_meshes.json')):
 mesh=bpy.data.meshes.new(item['name']);mesh.from_pydata(item['v'],[],item['f']);mesh.update()
 ob=bpy.data.objects.new(item['name'],mesh);bpy.context.collection.objects.link(ob)
 mat=bpy.data.materials.new(item['name']);mat.diffuse_color=colors.get(item['name'],(.22,.25,.3,1));ob.data.materials.append(mat)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.world.color=(.9,.9,.9)
scene.display.shading.background_type='WORLD';scene.display.shading.show_specular_highlight=True
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
if name=='optical_bench':target=Vector((0,0,53));cam.location=(160,-230,180);scale=190;res=(1400,1200)
elif name=='pen18_compact170_NOT_FOR_PRINT':target=Vector((0,0,85));cam.location=(95,-240,110);scale=195;res=(650,1500)
else:target=Vector((0,0,105));cam.location=(80,-240,120);scale=235;res=(650,1500)
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
scene.render.resolution_x=res[0];scene.render.resolution_y=res[1];scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=r+'/'+name+'_preview.png';bpy.ops.render.render(write_still=True)
