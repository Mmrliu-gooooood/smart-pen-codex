import sys,math,json,os
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
V=A.Vector;R=Path(__file__).resolve().parent
out=[]
for dia in [18,19,20]:
 ri=dia/2-1.2
 for eccentric in [3,3.2,3.4,3.6,3.8,4.,4.2]:
  cy=5.6-eccentric
  for contact_d in [6,7,8]:
   cm=ri-math.hypot(4,cy+4);contact=ri-(eccentric+contact_d/2)
   out.append(dict(outer_dia=dia,wall=1.2,refill_y=-eccentric,camera_y=cy,contact_OD=contact_d,camera_corner_margin_mm=cm,contact_radial_margin_mm=contact,minimum_mm=min(cm,contact),meets_assumed_0p3_budget=min(cm,contact)>=.3))
(R/'eccentricity_contact_scan.json').write_text(json.dumps(out,indent=2))
def ribbon(direction,width,radius,h=6.5):
 sections=[]
 for i in range(17):
  t=math.pi/2*i/16;z=17.5+h+radius*(1-math.cos(t))
  if direction in ['minusY','plusY']:
   sign=-1 if direction=='minusY' else 1;y=1.8+sign*4+sign*radius*math.sin(t)
   center=V(0,y,z);u=V(1,0,0);n=V(0,-sign*math.sin(t),math.cos(t))
  else:center=V(4+radius*math.sin(t),1.8,z);u=V(0,1,0);n=V(-math.sin(t),0,math.cos(t))
  corners=[center+u*(a*width/2)+n*(b*.075) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]]
  sections.append(Part.Wire(Part.makePolygon(corners)))
 return Part.makeLoft(sections,True,False)
routes=[];d=A.newDocument('FPC_bend_tests_NOT_ASSEMBLY')
for direction in ['minusY','plusY','plusX']:
 for width in [3,5,8]:
  for radius in [3,5]:
   s=ribbon(direction,width,radius);n=f'{direction}_W{width}_R{radius}';o=d.addObject('Part::Feature',n);o.Shape=s;o.addProperty('App::PropertyString','Basis');o.Basis='Mutually exclusive diagnostic quarter bend, not supplier flex geometry or full routed interconnect. Thickness0.15 assumed. Width/radius not qualified.'
   record=dict(direction=direction,width=width,radius=radius,valid=s.isValid(),refill_collision_mm3=s.common(Part.makeCylinder(1.175,67,V(0,-3.8,0))).Volume,outside_mm3={})
   for dia in [18,19,20]:record['outside_mm3'][str(dia)]=s.cut(Part.makeCylinder(dia/2-1.2,40)).Volume
   routes.append(record)
d.recompute();d.saveAs(str(R/'FPC_bend_tests_NOT_ASSEMBLY.FCStd'));Part.export(d.Objects,str(R/'FPC_bend_tests_NOT_ASSEMBLY.step'));(R/'fpc_quarter_bend_scan.json').write_text(json.dumps(routes,indent=2));A.closeDocument(d.Name)
opt=[]
for name in ['A18_axial_210','B19_axial_210','C19_parallel_180_CONDITIONAL','D20_parallel_180_budget']:
 d=A.openDocument(str(R/(name+'.FCStd')));shell=d.getObject('Housing_candidate').Shape;head=d.getObject('SC031GS_head_H6p5_candidate').Shape;nib=d.getObject('D1_refill_nominal').Shape
 shellv=shell.tessellate(.2)[0];headv=head.tessellate(.2)[0]
 for deg in [30,45,60]:
  t=math.radians(deg)
  for roll in [-30,0,30,90,180]:
   a=math.radians(roll);N=V(math.sin(t)*math.sin(a),-math.sin(t)*math.cos(a),math.cos(t));tip=V(0,-3.8,0);front=V(0,1.8,17.5);u=V(math.cos(a),math.sin(a),0);v=N.cross(u)
   wd=N.dot(front-tip)/N.z;hit=front+V(0,0,-wd);pts=[hit]+[hit+u*(sx*3)+v*(sy*3) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
   segments=[Part.LineSegment(front,p).toShape() for p in pts]
   opt.append(dict(config=name,theta_deg=deg,roll_deg=roll,lens_axis_WD_mm=wd,head_min_paper_clearance_mm=min(N.dot(p-tip) for p in headv),housing_min_paper_clearance_mm=min(N.dot(p-tip) for p in shellv),ray_housing_intersection_length_mm=sum(s.common(shell).Length for s in segments),ray_refill_intersection_length_mm=sum(s.common(nib).Length for s in segments),ROI_note='6mm square test patch only, not verified near-focus FOV or imaging accuracy'))
 A.closeDocument(d.Name)
(R/'paper_and_ray_checks.json').write_text(json.dumps(opt,indent=2));print('Scans complete:',len(out),'eccentric/contact,',len(routes),'FPC,',len(opt),'paper/ray cases')
