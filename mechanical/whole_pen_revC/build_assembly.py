"""Actual RevC footprint-derived mutually exclusive whole-pen studies. NO FAB."""
import sys,os,json,math,csv,hashlib
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
from pathlib import Path
V=A.Vector;R=Path(__file__).resolve().parent
pcb=json.loads((R/'inputs/revC_mechanical_extract.json').read_text())
def box(w,t,l,x,y,z):return Part.makeBox(w,t,l,V(x,y,z))
def cyl(r,l,x=0,y=0,z=0):return Part.makeCylinder(r,l,V(x,y,z))
def camera(h,y=1.8,z=17.5):
 board=box(8,8,.8,-4,y-4,z+h-.8)
 lens=cyl(3,3.67,0,y,z)
 holder=box(6.5,6.5,max(h-.8-1.5,.1),-3.25,y-3.25,z+1.5)
 return board.fuse(lens).fuse(holder).removeSplitter()
def outer_shell(dia,wall,length):
 rad=dia/2;ri=rad-wall
 main=cyl(rad,length-30,z=30).cut(cyl(ri,length-28,z=29))
 # Camera pod is clearance-based geometry, not a selected-holder drawing.
 pod=box(10.8,10.8,13.7,-5.4,1.8-5.4,16.3).common(cyl(rad,36))
 # Cone around eccentric nib axis enforces >=1mm housing/paper separation for theta<=60, all roll angles.
 safecone=Part.makeCone(0,38/math.tan(math.pi/3),38,V(0,-3.8,2))
 pod=pod.common(safecone).cut(box(8.4,8.4,22,-4.2,1.8-4.2,15))
 # Refill support interrupted across camera head so the guide does not invade PCB space.
 guide=cyl(2.2,6,0,-3.8,6).fuse(cyl(2.2,6,0,-3.8,30))
 rib=box(2.4,4.5,24,-1.2,-7.5,12).common(cyl(rad,40))
 s=main.fuse(pod).fuse(guide).fuse(rib).cut(cyl(1.45,40,0,-3.8,0))
 return s.removeSplitter()
def maxrad(s):
 b=s.BoundBox;return max(math.hypot(x,y) for x in [b.XMin,b.XMax] for y in [b.YMin,b.YMax])
def add(doc,n,s,basis,group=None):
 o=doc.addObject('Part::Feature',n);o.Shape=s;o.addProperty('App::PropertyString','Basis');o.Basis=basis
 if group:group.addObject(o)
 return o
configs=[dict(name='A18_axial_210',d=18.,wall=1.2,L=210.,pcbY=1.,cellY=0.,packD=12.2,packZ=141.,tailZ=192.,rfZ=128.,rfL=11.),dict(name='B19_axial_210',d=19.,wall=1.2,L=210.,pcbY=1.,cellY=0.,packD=12.2,packZ=141.,tailZ=192.,rfZ=128.,rfL=11.),dict(name='C19_parallel_180_CONDITIONAL',d=19.,wall=1.2,L=180.,pcbY=3.8,cellY=-2.2,packD=11.4,packZ=82.,tailZ=158.,rfZ=134.,rfL=22.),dict(name='D20_parallel_180_budget',d=20.,wall=1.2,L=180.,pcbY=4.1,cellY=-2.3,packD=12.2,packZ=82.,tailZ=158.,rfZ=134.,rfL=22.)]
reports=[]
for c in configs:
 doc=A.newDocument(c['name']);S={};ri=c['d']/2-c['wall'];inner=cyl(ri,c['L']+2,z=-1)
 group=doc.addObject('App::DocumentObjectGroup','ActualRevC_Components')
 def obj(n,s,basis,grp=None):S[n]=s;return add(doc,n,s,basis,grp)
 shell=outer_shell(c['d'],c['wall'],c['L'])
 obj('Housing_candidate',shell,'Conditional connected shell, no fasteners/seam/USB loadpath release. No STL. Camera pod clearance not supplier holder.')
 obj('RevC_board_12x95x0p8',box(12,.8,95,-6,c['pcbY'],32),'Actual board outline unchanged. KiCad source SHA256 '+pcb['source_sha256'])
 populated=[]
 for p in pcb['components']:
  a,b,xmax,ymax=p['bounds'];h=p['height_max']+.15
  sh=box(xmax-a,h,ymax-b,a-6,c['pcbY']+.8,127-ymax)
  n=p['ref']+('_DNP_RESERVE' if p['dnp'] else '')
  ob=obj(n,sh,p['footprint']+'; '+p['height_basis']+'; +0.15mm assumed solder allowance. Bounding prism of actual fab+pad footprint, not vendor solid.',group)
  if not p['dnp']:populated.append(n)
 obj('D1_refill_nominal',cyl(1.175,67,0,-3.8,0),'Real ink refill candidate; nominal tube only, tip/shoulder tolerances unknown. Eccentric axis Y=-3.8.')
 obj('Refill_service_sweep',cyl(1.45,82,0,-3.8,-15),'Forward extraction corridor incl assumed allowance, no frozen front release mechanism.')
 obj('Contact_cassette_REQUIRED_ENVELOPE',cyl(3,12,0,-3.8,68),'Required maximum Ø6x12 for compact mechanism. NOT scaled-down released fixture; real spring/stop/switch design remains open.')
 obj('SC031GS_head_H6p5_candidate',camera(6.5),'8x8 PCB published; total height6.5 SCAN EXAMPLE, not supplied module height. CH2035AB nominal lens/holder only.')
 obj('Cell10440_only',cyl(5.4,45,0,c['cellY'],c['packZ']+2),'Protected cell candidate max Ø10.8x45; actual source and NTC/contacts/holder must be selected. NO bare-cell substitution.')
 obj('Complete_battery_pack_BUDGET',cyl(c['packD']/2,49,0,c['cellY'],c['packZ']),'ASSUMED complete radial budget including sleeve/retention/NTC. Not an approved battery assembly; overlaps contained cell intentionally.')
 obj('Tail_power_USB_REQUIRED_BUDGET',box(10,5,c['L']-c['tailZ'],-5,-2.5,c['tailZ']),'Unrouted tail electrical/mechanical budget, not a real populated board; USB insert loads not designed.')
 obj('RF_region_UNQUALIFIED',box(10,12,c['rfL'],-5,-6,c['rfZ']),'Provisional reserved region, not vendor antenna keepout. Cannot claim RF qualification or tuning from separation.')
 # Paper optical geometry at theta45; central ray and requested 6mm square ROI only, no infinity-FOV inference.
 theta=math.pi/4;front=V(0,1.8,17.5);hit=V(0,1.8,5.6*math.tan(theta));e=V(0,math.cos(theta),math.sin(theta))
 corners=[hit+V(sx*3,0,0)+e*(sy*3) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 rays=Part.Compound([Part.LineSegment(front,p).toShape() for p in corners]+[Part.LineSegment(front,hit).toShape()])
 add(doc,'Optical_rays_theta45_ROI6_ONLY',rays,'6x6mm test ROI, no proven near-focus FOV; housing/refill ray checks are geometric only.')
 rpt={'config':c,'source_sha256':pcb['source_sha256'],'actual_footprints':len(pcb['components']),'populated':len(populated),'shape_valid':{},'containment_outside_mm3':{},'radial_clearance_mm':{},'pair_collisions':[],'housing_collisions':[]}
 physical=['RevC_board_12x95x0p8','D1_refill_nominal','Contact_cassette_REQUIRED_ENVELOPE','SC031GS_head_H6p5_candidate','Complete_battery_pack_BUDGET','Tail_power_USB_REQUIRED_BUDGET']+populated
 for n,s in S.items():
  rpt['shape_valid'][n]={'valid':s.isValid(),'solids':len(s.Solids)}
  if n!='Housing_candidate':rpt['containment_outside_mm3'][n]=s.cut(inner).Volume
 for n in physical:
  s=S[n];rpt['radial_clearance_mm'][n]=ri-maxrad(s) if n not in ['D1_refill_nominal','Contact_cassette_REQUIRED_ENVELOPE','Complete_battery_pack_BUDGET'] else ri-(abs(s.CenterOfMass.y)+(s.BoundBox.XLength/2))
  v=s.common(shell).Volume
  if v>1e-6:rpt['housing_collisions'].append([n,v])
 for i,n in enumerate(physical):
  for other in physical[i+1:]:
   # Shared PCB boundary and intentional lead solder allowance contact allowed at zero volume only.
   v=S[n].common(S[other]).Volume
   if v>1e-6:rpt['pair_collisions'].append([n,other,v])
 rpt['board_pack_clearance_mm']=S['RevC_board_12x95x0p8'].distToShape(S['Complete_battery_pack_BUDGET'])[0]
 rpt['camera_refill_clearance_mm']=S['SC031GS_head_H6p5_candidate'].distToShape(S['D1_refill_nominal'])[0]
 rpt['assembly_release']='NO: incomplete PCB/connector/RF, unqualified camera stack/FPC, unselected battery pack, compact contact mechanism not yet engineered'
 doc.recompute();doc.saveAs(str(R/(c['name']+'.FCStd')));Part.export([doc.getObject(n) for n in S],str(R/(c['name']+'.step')));reports.append(rpt);A.closeDocument(doc.Name)
(R/'assembly_validation.json').write_text(json.dumps(reports,indent=2))
# Height/radial and paper-clearance sweep. All geometric camera stacks mutually exclusive.
scans=[]
for dia in [18.,19.,20.]:
 for wall in [1.2,1.5]:
  ri=dia/2-wall
  for h in [4.5,6.,6.5,7.5,9.,10.5]:
   sh=camera(h);nib=cyl(1.175,67,0,-3.8);s={'outer_dia':dia,'wall':wall,'head_height':h,'radial_margin_mm':ri-maxrad(sh),'outside_cylinder_mm3':sh.cut(cyl(ri,40)).Volume,'head_refill_collision_mm3':sh.common(nib).Volume,'board_start_margin_mm':32-(17.5+h)}
   scans.append(s)
(R/'camera_height_scan.json').write_text(json.dumps(scans,indent=2))
# Cross section optimizer uses real footprint bounds and conservative height allowances, not miniaturized PCB.
trade=[]
for dia in [18.,19.,20.]:
 for pack in [10.8,11.4,12.2]:
  for passive_h in [1.,1.6]:
   ri=dia/2-1.2;best=None
   for i in range(401):
    cy=-4+i*.01;py=cy+pack/2+.3
    if py<0:continue
    radial=math.hypot(6,py+.8)
    for p in pcb['components']:
     if p['dnp']:continue
     b=p['bounds'];x=max(abs(b[0]-6),abs(b[2]-6));height=p['height_max'] if not p['height_basis'].startswith('ASSUMED') else passive_h
     radial=max(radial,math.hypot(x,py+.8+.15+height))
    margin=min(ri-(abs(cy)+pack/2),ri-radial)
    if best is None or margin>best['minimum_radial_margin_mm']:best=dict(cell_y=cy,pcb_inner_y=py,minimum_radial_margin_mm=margin)
   trade.append(dict(outer_dia=dia,wall=1.2,complete_pack_dia=pack,passive_height=passive_h,required_board_pack_gap=.3,target_radial_budget=.3,passes_assumed_budget=best['minimum_radial_margin_mm']>=.3,**best))
(R/'cross_section_tradeoffs.json').write_text(json.dumps(trade,indent=2))
# Lens centre ray / front lens rim paper clearance over theta; optical quality is not inferred.
opt=[]
for angle in [30,45,60]:
 t=math.radians(angle);wd=17.5-5.6*math.tan(t)
 opt.append(dict(theta_from_paper_normal_deg=angle,lens_axis_WD_mm=wd,fieldcentre_offset_from_tip_on_paper_mm=5.6/math.cos(t),front_lens_rim_paper_clearance_mm=17.5*math.cos(t)-8.6*math.sin(t),axial_stroke_residual_example_mm=.1,uncompensated_projected_error_mm=.1*math.sin(t)))
(R/'optical_geometry.json').write_text(json.dumps(opt,indent=2))
print(json.dumps([{'config':r['config']['name'],'housing_collisions':r['housing_collisions'],'pair_collisions':r['pair_collisions'],'board_pack_gap':r['board_pack_clearance_mm'],'camera_refill_gap':r['camera_refill_clearance_mm']} for r in reports],indent=2))
