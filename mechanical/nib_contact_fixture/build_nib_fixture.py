#!/usr/bin/env python3
"""D1 nib-contact parameter-validation fixture. mm; not complete pen release."""
import os,sys,json,math
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part,Mesh
from nib_features import NibPart,shape,box,cyl,V
R=os.path.dirname(os.path.abspath(__file__));os.makedirs(R+'/stl',exist_ok=True)
d=A.newDocument('D1NibContactFixture');S={};O={}
parts=['Base','NoseGuide','FrontGuide','RearGuide','Slider','HardStop','SwitchCarrier']
for name in parts:
 o=d.addObject('Part::FeaturePython',name);NibPart(o,name);O[name]=o
 o.addProperty('App::PropertyString','Release');o.Release='PARAMETER VALIDATION FIXTURE: inspect print; measure actual refill and switch before loading'
d.recompute()
for name in parts:S[name]=O[name].Shape

def ref(name,s,basis):
 o=d.addObject('Part::Feature',name);o.Label=name;o.Shape=s;o.addProperty('App::PropertyString','Basis');o.Basis=basis;S[name]=s;O[name]=o
ref('D1_nominal_envelope',cyl(1.175,67,0),'2.35x67 nominal only. Tip profile and tolerances NOT verified; no spring/contact part selected.')
ref('SoftGrip_loaded_envelope',cyl(2.1,3,54).cut(cyl(1.175,5,53)),'Soft silicone candidate free OD4.3/ID2.0/L3; loaded envelope only, grip/pullout must be measured. Not a printable part.')
ref('Spring_installed_envelope',cyl(4,9,65).cut(cyl(3.7,11,64)),'Envelope only, no selected spring. Candidate ID>=7.4 OD<=8, free11, installed9, rate0.025..0.075N/mm; coil-bind margin required.')
helix=Part.makeHelix(8.7/8,8.7,3.85)
path=Part.Wire(helix.Edges);profile=Part.Wire([Part.makeCircle(.15,helix.Vertexes[0].Point,V(0,1,0))])
coil=path.makePipeShell([profile],True,True);coil.rotate(V(0,0,0),V(0,1,0),90);coil.translate(V(65.15,0,20))
ref('Spring_visual_ONLY',coil,'ILLUSTRATIVE helix, wire0.3 and8turns; not selected part, not spring manufacturing geometry, ends not ground. Force target must be measured independently.')
# Generic mechanical interface for a test PCB, not a released electrical board.
pcb=box(.8,14,14,87.4,-7,13)
for y in [-5,5]:
 for z in [15,25]:pcb=pcb.cut(cyl(1.2,2,87,y,z))
ref('Switch_testPCB_template',pcb,'14x14x0.8 template only. Four Ø2.4 mounting holes,10x10 pattern. Electrical footprint/routing not supplied.')
ref('HDT_body_reference',box(2.25,3.5,2.8,85.15,-1.75,18.6),'Conservative body box based on official HDT0001 drawing. Not detailed vendor STEP.')
ref('HDT_actuator_motion_reference',box(1.1,.6,1.2,84.05,-.3,19.4),'MOVING ACTUATOR ENVELOPE. Free actuator tip84.05, PCBdatum87.4; compresses when slider reaches it. Intentional swept overlap, not rigid collision.')
# Actual attachment hardware envelope: ISO low-head dimensions MUST be checked before buying.
hardware={}
# Base attachment: use M3 threaded inserts in guide feet would require heater; instead through rods long enough above blocks.
# Model M3x30 for nose/front/rear (head belowbase) + nuts at z28, M3x16 stop (nut z12), M3x10 carrier(nut z8).
for x,nutz,length in [(8,28,30),(59.5,28,30),(67.65,12,16),(77,28,30),(90,8,10)]:
 for y in [-12,12]:
  n='M3_at_%s_%s'%(x,y);s=cyl(1.5,length,x,y,2.6,(0,0,1)).fuse(cyl(2.9,2.5,x,y,.1,(0,0,1))).fuse(cyl(3.2,2.4,x,y,nutz,(0,0,1)))
  hardware[n]=s;ref(n,s,'M3 bolt/round nut envelope; actual hex AF5.5 fits circumradius3.2; lowhead Ø<=5.8 height<=2.5. Verify lengths.')
for y in [-5,5]:
 for z in [15,25]:
  n='M2_PCB_%s_%s'%(y,z);s=cyl(1,8,87.4,y,z).fuse(cyl(1.9,2,85.4,y,z)).fuse(cyl(2.4,1.6,92.2,y,z));hardware[n]=s;ref(n,s,'M2x8 conditional PCB attachment envelope, no threads. Four corner points.')
# Straight refill service corridor and transverse access are checked against retained parts, not against soft grip contact.
report={'status':'FIXTURE ONLY; NOT PEN RELEASE','parameters':{'stroke_mm':.65,'switch_gap_mm':.05,'guide_diameter_mm':6.4,'slider_diameter_mm':6,'nominal_D1_mm':[2.35,67]},'parts':{},'rigid_collisions':[],'motion_collisions':[],'hardware_collisions':[],'service_collisions':[]}
for name in parts:
 s=S[name];assert s.isValid() and len(s.Solids)==1,name
 p=s.copy();p.translate(V(0,0,-s.BoundBox.ZMin));v,f=p.tessellate(.06);m=Mesh.Mesh()
 for tri in f:m.addFacet(*[v[i] for i in tri])
 m.write(R+'/stl/'+name+'.stl');report['parts'][name]={'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bbox_mm':[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength]}
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  vol=S[a].common(S[b]).Volume
  if vol>1e-6:report['rigid_collisions'].append([a,b,vol])
for n,h in hardware.items():
 for p in parts+['Switch_testPCB_template','HDT_body_reference']:
  v=h.common(S[p]).Volume
  if v>1e-6:report['hardware_collisions'].append([n,p,v])
for travel in [i*.05 for i in range(14)]:
 for moving in ['Slider','D1_nominal_envelope','SoftGrip_loaded_envelope']:
  s=S[moving].copy();s.translate(V(travel,0,0))
  for fixed in ['Base','NoseGuide','FrontGuide','RearGuide','HardStop','SwitchCarrier','Switch_testPCB_template','HDT_body_reference']+list(hardware):
   v=s.common(S[fixed]).Volume
   if v>1e-6:report['motion_collisions'].append([travel,moving,fixed,v])
# Stop penetration immediately beyond permissible motion proves hard mechanical interception.
s=S['Slider'].copy();s.translate(V(.70,0,0));report['overstroke_0p70_interception_mm3']=s.common(S['HardStop']).Volume
s=S['Slider'].copy();s.translate(V(.65,0,0));report['stop_contact_distance_mm']=s.distToShape(S['HardStop'])[0]
for travel in [-67,-50,-25,0]:
 s=S['D1_nominal_envelope'].copy();s.translate(V(travel,0,0))
 for p in ['Base','NoseGuide','FrontGuide','RearGuide','HardStop','SwitchCarrier','Slider']:
  v=s.common(S[p]).Volume
  if v>1e-6:report['service_collisions'].append([travel,p,v])
report['force_model_N']={'spring_rest_range':[.05,.15],'spring_at_stop_range':[.06625,.19875],'switch_max_HDT':.035*9.80665,'friction':'UNKNOWN: measure, not assumed zero'}
report['spring_min_installed_length_mm']=9-.65
report['switch_nominal_actuation_from_home_mm']=.05+.3
report['switch_depression_at_stop_mm']=.65-.05
report['switch_rated_min_load']='Not specified in HDT public datasheet; low-uA reliability NOT qualified'
d.recompute();d.saveAs(R+'/D1_nib_contact_fixture.FCStd');Part.export(d.Objects,R+'/D1_nib_contact_fixture.step')
json.dump(report,open(R+'/geometry_validation.json','w'),indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2))
