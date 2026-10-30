import sys,math,json,hashlib
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad-python3/lib'])
import FreeCAD as A,Part
V=A.Vector;R=Path(__file__).resolve().parent
E=json.loads((R/'inputs/current_board_extract.json').read_text())
def box(w,h,l,x,y,z):return Part.makeBox(w,h,l,V(x,y,z))
def cylinder(r,l,x=0,y=0,z=0):return Part.makeCylinder(r,l,V(x,y,z))
def add(doc,name,shape,basis):
 o=doc.addObject('Part::Feature',name);o.Shape=shape;o.addProperty('App::PropertyString','Basis');o.Basis=basis;return o
# Rectangular-section quarter turn from back-face pads toward board centre.
# This intentionally changes the assumed departure tangent from old outward-edge routes.
def bend(width,radius,gap,side='minusY'):
 sections=[];sign=1 if side=='minusY' else -1;edge=1.8-sign*4
 for i in range(33):
  t=math.pi*.5*i/32;c=V(0,edge+sign*radius*math.sin(t),24+gap+radius*(1-math.cos(t)))
  u=V(1,0,0);n=V(0,-sign*math.sin(t),math.cos(t))
  pts=[c+u*(a*width/2)+n*(b*.075) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]]
  sections.append(Part.Wire(Part.makePolygon(pts)))
 return Part.makeLoft(sections,True,False)
camera=box(8,8,.8,-4,-2.2,23.2).fuse(cylinder(3,3.67,0,1.8,17.5)).fuse(box(6.5,6.5,4.2,-3.25,-1.45,19))
refill=cylinder(1.175,67,0,-3.8)
scan=[]
for side in ['minusY','plusY']:
 for w in [5,8]:
  for rad in [3,5]:
   for gap in [.2,.5]:
    s=bend(w,rad,gap,side)
    rec=dict(side=side,width=w,radius=rad,rear_gap=gap,valid=s.isValid(),outside_ID15p6_mm3=s.cut(cylinder(7.8,40)).Volume,camera_collision_mm3=s.common(camera).Volume,refill_collision_mm3=s.common(refill).Volume,camera_distance_mm=s.distToShape(camera)[0],refill_distance_mm=s.distToShape(refill)[0],endpoint_y=1.8+(1 if side=='minusY' else -1)*(rad-4),endpoint_z=24+gap+rad)
    rec['geometric_only_pass']=rec['valid'] and max(rec[k] for k in ['outside_ID15p6_mm3','camera_collision_mm3','refill_collision_mm3'])<1e-6
    scan.append(rec)
(R/'inward_flex_scan.json').write_text(json.dumps(scan,indent=2))
doc=A.newDocument('D18_AXIAL_260_CONDITIONAL_NOFAB');physical={}
def obj(n,s,b):physical[n]=s;return add(doc,n,s,b)
obj('Camera_8mm_UNKNOWN_HEIGHT',camera,'Future 8x8 head only; H6.5 and rear inward departure unconfirmed. NOT existing SC035HGS custom camera.')
obj('D1_nominal',refill,'Nominal refill dimensions, tolerances not qualified')
obj('Flex_W8_R3_inward_REQUIRES_NEW_EXIT',bend(8,3,.2),'Assumed 0.15mm flex, R3 neutral-axis. Rear-face inward pads required; actual supplier exit/stack/radius unknown. Ends before host connector, NOT full interconnect.')
obj('Compact_contact_REQUIRED',cylinder(3,12,0,-3.8,68),'Required envelope, not finished mechanism')
main=E['mainboard'];obj('Mainboard_XCLK5_12x95',box(12,.8,95,-6,1,32),'Actual source '+main['sha256']+'; five unconnected/16 missing footprints retained as design limitation')
for p in main['parts']:
 if p['dnp']:continue
 a,b,c,d=p['bounds'];h=p['height']+.15;y=1-h if p['back'] else 1.8
 obj('Main_'+p['ref'],box(c-a,h,d-b,a-6,y,127-d),p['footprint']+'; '+p['height_basis']+' +0.15 assumed solder; actual side '+('B' if p['back'] else 'F'))
obj('Battery_complete_REQUIRED_12p2x49',cylinder(6.1,49,0,0,141),'Conditional complete pack incl NTC/sleeve/contacts; no assembled product qualified')
obj('Power14x45_THICKNESS_BUDGET4p15',box(14,4.15,45,-7,-2.075,192),'Actual board outline 14x45; total 4.15mm double-side budget conditional, not per-component CAD. Source '+E['power']['sha256'])
obj('USB12x20_HEIGHT_BUDGET5',box(12,5,20,-6,-2.5,239),'Actual board outline 12x20; 5mm height budget assumed; connector mating opening and loadpath missing. Source '+E['usb']['sha256'])
add(doc,'RF_reserved_UNQUALIFIED',box(10,12,11,-5,-6,128),'Reserved only; not antenna keepout qualification')
add(doc,'Barrel_OD18_wall1p2_reference',cylinder(9,230,z=30).cut(cylinder(7.8,232,z=29)),'Reference cylindrical barrel only, not split shell, front housing or released print')
inside=cylinder(7.8,262,z=-1);collisions=[];outside={};radial={}
for n,s in physical.items():
 outside[n]=s.cut(inside).Volume
 for m,t in physical.items():
  if n<m:
   v=s.common(t).Volume
   if v>1e-6:collisions.append([n,m,v])
report=dict(status='NOFAB; envelopes and partial bend only',length=260,old_axial_length=210,increase=50,mainboard=main['sha256'],main_parts=len(main['parts']),power=E['power']['sha256'],usb=E['usb']['sha256'],outside_mm3=outside,collisions=collisions,power_rect_radial_clearance=7.8-math.hypot(7,2.075),unqualified=['8mm head total height and connector','FPC stack/minimum radius/actual exit','Full FPC-to-host route and strain relief','16 missing mainboard footprints','battery assembled pack and thermal interface','USB insertion load path','RF antenna and clearances','shell fasteners and tolerance chain'])
(R/'axial260_validation.json').write_text(json.dumps(report,indent=2))
doc.recompute();doc.saveAs(str(R/'D18_AXIAL_260_CONDITIONAL_NOFAB.FCStd'));Part.export(doc.Objects,str(R/'D18_AXIAL_260_CONDITIONAL_NOFAB.step'));A.closeDocument(doc.Name)
# Reopen both native and exported STEP, no mesh-only correctness claim.
a=A.openDocument(str(R/'D18_AXIAL_260_CONDITIONAL_NOFAB.FCStd'));checks={'native_objects':len(a.Objects),'native_valid':all(o.Shape.isValid() for o in a.Objects if hasattr(o,'Shape'))};A.closeDocument(a.Name)
s=Part.Shape();s.read(str(R/'D18_AXIAL_260_CONDITIONAL_NOFAB.step'));checks.update(step_valid=s.isValid(),step_solids=len(s.Solids));(R/'reopen_validation.json').write_text(json.dumps(checks,indent=2))
# Necessary aligned-section bounds only, not proof against tilted layouts.
limits={'existing_custom_camera':{'PCB_nominal_square':13,'PCB_max_square':13.2,'ear_span_nominal':21.82,'wall':1.2,'body_aligned_OD_lower_bound_nominal':math.sqrt(2)*13+2.4,'body_aligned_OD_lower_bound_max':math.sqrt(2)*13.2+2.4,'ear_span_OD_lower_bound_nominal':21.82+2.4,'qualification':'Necessary bounds for board transverse to barrel; ears full shape and tolerances unknown. Tilting board changes optics/FPC and is NOT excluded globally.'},'power_pack_side_by_side':{'power_width':14,'power_total_thickness_budget':4.15,'complete_pack_D':12.2,'gap':.3}}
best=None
for i in range(1801):
 cy=-9+i*.01;py=cy+6.1+.3;radius=max(abs(cy)+6.1,math.hypot(7,max(abs(py),abs(py+4.15))))
 if best is None or radius<best['required_inner_radius']:best=dict(cell_y=cy,power_bottom_y=py,required_inner_radius=radius,outer_dia_with_wall1p2=2*radius+2.4)
limits['power_pack_side_by_side']['best_simple_cross_section']=best
(R/'dimensional_limits.json').write_text(json.dumps(limits,indent=2))
print(json.dumps({'flex_passes':sum(x['geometric_only_pass'] for x in scan),'cases':len(scan),'collisions':collisions,'outside_nonzero':{k:v for k,v in outside.items() if v>1e-6},'reopen':checks,'side_by_side':best},indent=2))
