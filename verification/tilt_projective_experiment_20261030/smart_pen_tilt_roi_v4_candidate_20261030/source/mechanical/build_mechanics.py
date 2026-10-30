"""Regenerate candidate study and printable bench. mm; python3 + FreeCAD libs.
No selected sensor, switch, cell or complete-pen manufacturing release.
"""
import sys,os,json,math
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part,Mesh
V=A.Vector; ROOT=os.path.dirname(os.path.abspath(__file__)); os.makedirs(ROOT+'/stl',exist_ok=True)
def box(x,y,z,at):return Part.makeBox(x,y,z,V(*at))
def cyl(r,h,at,axis=(0,0,1)):return Part.makeCylinder(r,h,V(*at),V(*axis))
def cut_holes(s,locations,r,h,axis=(0,0,1)):
 for p in locations:s=s.cut(cyl(r,h,p,axis))
 return s
from cad_features import ParamPart,build

report={'units':'mm','status':'BENCH PRINT CANDIDATES; PEN ENVELOPE STUDY ONLY','parts':{},'bench_interferences':[]}
doc=A.newDocument('OpticalBench')
for kind in ['Base','Upright','Carrier','Adapter_SC035HGS_candidate','Nose_guide_coupon','Paper_wedge_30','Paper_wedge_45','Paper_wedge_60']:
 o=doc.addObject('Part::FeaturePython',kind);ParamPart(o,kind);o.addProperty('App::PropertyString','Release');o.Release='Bench prototype. Camera adapter from SC035HGS drawing; actual ear datum/screw length requires measurement.'
 doc.recompute();s=o.Shape;assert s.isValid() and len(s.Solids)==1
 # Save individual STL in local printable coordinates, all bounding-box minima at Z0.
 p=s.copy();p.translate(V(0,0,-s.BoundBox.ZMin));mesh=Mesh.Mesh();vv,ff=p.tessellate(.08)
 for face in ff:mesh.addFacet(*[vv[i] for i in face])
 mesh.write(ROOT+'/stl/'+kind+'.stl')
 report['parts'][kind]={'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'bbox_mm':[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength],'mesh_closed':mesh.isSolid(),'mesh_facets':mesh.CountFacets}
for i,a in enumerate(['Base','Upright','Carrier','Adapter_SC035HGS_candidate']):
 for b in ['Base','Upright','Carrier','Adapter_SC035HGS_candidate'][i+1:]:
  v=doc.getObject(a).Shape.common(doc.getObject(b).Shape).Volume
  if v>1e-6:report['bench_interferences'].append([a,b,v])
# Hardware envelopes: bolt shanks must pass holes, head/washer/nut at outer faces.
hw=[]
for x in (-28,28):
 for y in (22,41):
  hw.append(('BaseBolt_%s_%s'%(x,y),cyl(2,16,(x,y,0)).fuse(cyl(3.5,3,(x,y,0))).fuse(cyl(4.5,3,(x,y,12)))))
for x in (-28,28):
 hw.append(('SliderBolt_%s'%x,cyl(2,20,(x,20,50),(0,1,0)).fuse(cyl(4.5,3,(x,21,50),(0,1,0))).fuse(cyl(4.5,3,(x,36,50),(0,1,0)))))
for x in (-15,15):
 for y in (-12.5,12.5):
  hw.append(('AdapterM3_%s_%s'%(x,y),cyl(1.5,12,(x,y,33)).fuse(cyl(2.75,3,(x,y,45))).fuse(cyl(3.2,3,(x,y,35)))))
# M1.6 retention: conditional envelope; actual camera ear datum and screw length to measure.
for x in (-9,9):
 hw.append(('CameraM1p6_%s'%x,cyl(.8,9,(x,0,39)).fuse(cyl(1.5,1.5,(x,0,45))).fuse(cyl(1.75,2,(x,0,40)))))
report['hardware_vs_print_interferences']=[]
hardware_objects={}
for n,s in hw:
 o=doc.addObject('Part::Feature',n);o.Shape=s;hardware_objects[n]=o
 for p in ['Base','Upright','Carrier','Adapter_SC035HGS_candidate']:
  v=s.common(doc.getObject(p).Shape).Volume
  if v>1e-6:report['hardware_vs_print_interferences'].append([n,p,v])
# Slider swept positions end ranges, no integrated camera envelope claimed.
report['slider_swept_checks']=[]
for delta in [-26,44]:
 carrier=doc.getObject('Carrier').Shape.copy();carrier.translate(V(0,0,delta))
 report['slider_swept_checks'].append({'delta_z':delta,'upright_collision_mm3':carrier.common(doc.getObject('Upright').Shape).Volume,'base_collision_mm3':carrier.common(doc.getObject('Base').Shape).Volume})
report['moving_assembly_sampled_collisions']=[]
report['moving_assembly_min_base_clearance_mm']=None
moving=['Carrier','Adapter_SC035HGS_candidate']+[n for n,_ in hw if not n.startswith('BaseBolt')]
for delta in [-26,-19,-12,-5,2,9,16,23,30,37,44]:
 for n in moving:
  sh=(hardware_objects[n] if n in hardware_objects else doc.getObject(n)).Shape.copy();sh.translate(V(0,0,delta))
  clearance=sh.distToShape(doc.getObject('Base').Shape)[0]
  old=report['moving_assembly_min_base_clearance_mm']
  report['moving_assembly_min_base_clearance_mm']=clearance if old is None else min(old,clearance)
  for fixed in ['Base','Upright']:
   volume=sh.common(doc.getObject(fixed).Shape).Volume
   if volume>1e-6:report['moving_assembly_sampled_collisions'].append([delta,n,fixed,volume])
doc.recompute();doc.saveAs(ROOT+'/optical_bench.FCStd');Part.export(doc.Objects,ROOT+'/optical_bench.step')
# New pen study; complete envelope dimensions are assumptions, not usable PCB outline.
d=A.newDocument('Pen18Envelope');S={}
def add(n,s,basis):
 o=d.addObject('Part::Feature',n);o.Shape=s;o.addProperty('App::PropertyString','Basis');o.Basis=basis;S[n]=s
add('Shell_d18_wall1p5',cyl(9,210,(0,0,0)).cut(cyl(7.5,212,(0,0,-1))),'Space boundary only. No joints or fasteners; not print release.')
add('Refill_D1_nominal',cyl(1.175,67,(0,0,0)),'2.35x67 nominal, actual tip and tail unknown')
add('Refill_service_sweep',cyl(1.65,80,(0,0,-13)),'Full forward extraction corridor only; carrier release unknown')
add('Camera_candidate8x8x8',box(8,8,8,(-4,2.5,6)),'ASSUMED HEIGHT; 8x8 supplier PCB candidate; optical tilt/FPC not resolved')
add('Contact_stack_budget',cyl(6.5,10,(0,0,67)),'Not engineered; 0.3mm nominal actuation/0.6mm hard stop design targets only')
add('Controller_populated_candidate',box(16,3.2,26,(-8,-1.6,82)),'REJECTED MINI BRANCH ONLY. PCB16 wide,0.8 thick + module2.4. Narrow PICO/bare-chip alternatives unresolved.')
add('PICO_narrowPCB_alternative',box(12,4,60,(-6,-2,78)),'ALTERNATIVE TO MINI; 12x60x0.8 board + assumed component allowance. Not electronics placement/final board shape.')
add('Protected10440_cell_alternative',cyl(5.4,45,(0,0,148)),'ALTERNATIVE TO POUCH; vendor nominal10.6x44.8 plus0.2 dimensional allowance; holder contacts sleeve NTC not included.')
add('Battery_complete_budget',box(12,7,45,(-6,-3.5,148)),'UNSELECTED 12x7x45 complete package budget; not a qualified cell or capacity claim')
add('Battery_expansion_reserve',box(13,8,47,(-6.5,-4,147)),'ASSUMED reserve; supplier swelling/NTC/PCM requirements may exceed this')
add('USB_tail_budget',box(10,6,10,(-5,-3,200)),'Candidate connector charge/program board, connector insertion load not designed')
add('Antenna_keepout_placeholder',box(10,10,8,(-5,-5,138)),'NOT selected antenna keepout. Requires vendor ground/copper/metal rules; candidate between PCB and cell; still requires selected antenna rules')
add('FPC_route_placeholder',box(4,.5,95,(-2,-6,16)),'No actual FPC exit/connectors. Minimum bend radius must come from flex supplier')
report['pen_containment']={n:s.cut(cyl(7.5,210,(0,0,0))).Volume for n,s in S.items() if n!='Shell_d18_wall1p5'}
physical=['Refill_D1_nominal','Camera_candidate8x8x8','Contact_stack_budget','Controller_populated_candidate','Battery_complete_budget','USB_tail_budget']
report['pen_physical_collisions']=[]
for i,a in enumerate(physical):
 for b in physical[i+1:]:
  v=S[a].common(S[b]).Volume
  if v>1e-6:report['pen_physical_collisions'].append([a,b,v])
report['controller_min_enclosing_diameter_mm']=math.hypot(16,3.2)
report['controller_min_outer_diameter_at_1p5_wall_mm']=math.hypot(16,3.2)+3
report['pen_solids']={n:{'valid':s.isValid(),'solids':len(s.Solids)} for n,s in S.items()}
d.recompute();d.saveAs(ROOT+'/pen18_envelope_NOT_FOR_PRINT.FCStd');Part.export(d.Objects,ROOT+'/pen18_envelope_NOT_FOR_PRINT.step')
json.dump(report,open(ROOT+'/geometry_validation.json','w'),indent=2)
print(json.dumps(report,indent=2))
# Compact alternative: front thin electronics overlaps refill on opposite side of camera.
d=A.newDocument('Pen18Compact170');S={}
add('Shell_d18_wall1p5',cyl(9,170,(0,0,0)).cut(cyl(7.5,172,(0,0,-1))),'170mm geometric alternative; not finished mechanism or enclosure')
add('Refill_D1_nominal',cyl(1.175,67,(0,0,0)),'Nominal only')
add('Refill_service_sweep',cyl(1.65,80,(0,0,-13)),'Full extraction corridor, release not engineered')
add('Camera_candidate8x8x8',box(8,8,8,(-4,2.5,6)),'UNSELECTED replacement candidate; existing21.82mm-ear module excluded')
add('Thin_mainPCB_11p5x60x2p4_budget',box(11.5,2.4,60,(-5.75,-4.4,7)),'Inclusive0.8mmPCB plus<=1.6mm package+solder allowance; no underside components. Unplaced/unrouted. Opposite camera.')
add('Contact_stack_budget',cyl(6.5,10,(0,0,67)),'Unengineered spring/contact/hard-stop budget')
add('PowerPCB_12x20x4_budget',box(12,4,20,(-6,-2,80)),'Tallpower separate island. Thermal/routing/assembly unverified')
add('RF_keepout_placeholder',box(10,10,8,(-5,-5,100)),'Placeholder only. Antenna supplier/return-plane/metal-distance rules not selected')
add('Protected10440_cell_only',cyl(5.4,45,(0,0,110)),'10.8x45 max candidate cell; sleeve/NTC/holder/tabs/leads excluded')
add('USB_tail_budget',box(10,6,10,(-5,-3,160)),'Mechanical load path and charging heat unresolved')
checks={'status':'GEOMETRIC ALTERNATIVE ONLY; NOT FOR PRINT','length_mm':170,'containment_mm3':{},'collisions':[]}
for n,s in S.items():
 if n!='Shell_d18_wall1p5':checks['containment_mm3'][n]=s.cut(cyl(7.5,170,(0,0,0))).Volume
physical=[n for n in S if n not in ['Shell_d18_wall1p5','Refill_service_sweep','RF_keepout_placeholder']]
for i,a in enumerate(physical):
 for b in physical[i+1:]:
  vol=S[a].common(S[b]).Volume
  if vol>1e-6:checks['collisions'].append([a,b,vol])
checks['thin_board_to_refill_service_mm']=S['Thin_mainPCB_11p5x60x2p4_budget'].distToShape(S['Refill_service_sweep'])[0]
checks['thin_board_to_shell_mm']=S['Thin_mainPCB_11p5x60x2p4_budget'].distToShape(S['Shell_d18_wall1p5'])[0]
d.recompute();d.saveAs(ROOT+'/pen18_compact170_NOT_FOR_PRINT.FCStd');Part.export(d.Objects,ROOT+'/pen18_compact170_NOT_FOR_PRINT.step')
json.dump(checks,open(ROOT+'/compact170_validation.json','w'),indent=2)
