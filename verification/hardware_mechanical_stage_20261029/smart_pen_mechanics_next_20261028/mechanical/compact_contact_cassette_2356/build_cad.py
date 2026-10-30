import sys,json,math,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parent;V=A.Vector;cy=-3.8
# Own design dimensions, not fabricated vendor specifications. All dimensions mm.
def cyl(r,z0,z1,x=0,y=cy):return Part.makeCylinder(r,z1-z0,V(x,y,z0))
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def gap(a,b):
 x=a.BoundBox;y=b.BoundBox
 return math.sqrt(sum(max(0,getattr(x,k+'Min')-getattr(y,k+'Max'),getattr(y,k+'Min')-getattr(x,k+'Max'))**2 for k in 'XYZ'))
# Clamshell can be machined with open access to all bores/shoulders. Two screw holes are above the sliding axis.
housing=cyl(3.8,62,80.6)
for z in [66,78]:housing=housing.fuse(box(-3.5,3.5,-1.2,1.8,z-1.6,z+1.6))
for r,z0,z1 in [(2.1,61.9,66.5),(3.1,66.5,67.75),(1.8,67.75,73.3),(1.1,73.3,74.3),(3.0,74.3,78.2)]:housing=housing.cut(cyl(r,z0,z1))
# Adjustable carrier slot 78.2..79.6: 0.8 PCB plus total0.6 measured shims.
outline=box(-3.75,3.75,-6.4,-.4,78.2,79.6).cut(box(3.5,3.8,-1.0,-.3,78.1,79.7))
housing=housing.cut(outline)
for x in [-2.3,2.3]:housing=housing.cut(box(x-1.2,x+1.2,-2.6,-.6,79.15,80.7))
for z in [66,78]:housing=housing.cut(Part.makeCylinder(.9,8,V(-4.4,.6,z),V(1,0,0)))
housing=housing.removeSplitter();left=housing.common(box(-10,0,-10,5,60,83));right=housing.common(box(0,10,-10,5,60,83))
slider=cyl(2,62,67.5).fuse(cyl(3,66.5,67.5)).fuse(cyl(1,67.5,74.8)).cut(cyl(1.25,61.9,67)).cut(cyl(1.5,61.9,65)).removeSplitter()
soft=cyl(1.5,62,65).cut(cyl(1.175,61.9,65.1))
refill=cyl(1.175,0,67)
pcb=box(-3.75,3.75,-6.4,-.4,78.4,79.2).cut(box(3.5,3.8,-1.0,-.3,78.3,79.3))
# Own TH wire pads .6 drills; real switch recommended pads are captured separately in nativePCB.
for x in [-2.3,2.3]:pcb=pcb.cut(cyl(.3,78.3,79.3,x,-1.6))
shimring=cyl(3.8,78.2,78.4).cut(cyl(3.0,78.1,78.5));shimfront=shimring.common(box(-3.75,3.75,-6.4,-.4,78.2,78.4))
shimback=cyl(3.8,79.2,79.6).cut(cyl(3.0,79.1,79.7)).common(box(-3.75,3.75,-6.4,-.4,79.2,79.6))
for x in [-2.3,2.3]:shimback=shimback.cut(box(x-1.2,x+1.2,-2.6,-.6,79.1,79.7))
# Body nominal3x3.4 and height2.3+.3max; extra.1 XY each side/.15 assembly is explicit study allowance.
switch=box(-1.6,1.6,cy-1.8,cy+1.8,78.4-2.75,78.4)
actuator=cyl(.375,74.8,75.65)
spring=cyl(1.675,67.5,73.3).cut(cyl(1.15,67.4,73.4))
fixed={'HousingLeft':left,'HousingRight':right,'SwitchCarrierPCB':pcb,'FrontCalibrationShim':shimfront,'RearCalibrationShim':shimback,'SPVE_body_conservative':switch}
screws={}
for z in [66,78]:
 # ISO4762 supplier dimensional reference: M1.6 headØ3/H1.6; selected8mm length study, threads suppressed.
 sh=Part.makeCylinder(.8,8,V(-4.5,.6,z),V(1,0,0)).fuse(Part.makeCylinder(1.5,1.6,V(3.5,.6,z),V(1,0,0)))
 screws['M1p6x8_at_'+str(z)]=sh
fixed.update(screws)
wire={}
for name,x in [('CONTACT',-2.3),('GND',2.3)]:wire['Wire_'+name]=box(x-1.1,x+1.1,-2.5,-.7,79.2,81.2)
S={**fixed,'Slider':slider,'SoftGrip_COMPRESSED_ASSUMPTION':soft,'D1_nominal':refill,'D001_spring_RESERVED_ENVELOPE':spring,'SPVE_actuator_at_rest':actuator,**wire}
# Intentional touching and spring/reference overlaps are not treated as interpenetration.
checks=[]
physical=list(fixed)+['Slider']
for i,n in enumerate(physical):
 for m in physical[i+1:]:
  if gap(S[n],S[m])<1e-8:
   v=S[n].common(S[m]).Volume
   if v>1e-7:checks.append(dict(a=n,b=m,volume=v))
wirehits=[]
for n,s in wire.items():
 for m,t in fixed.items():
  if gap(s,t)<1e-8:
   v=s.common(t).Volume
   # The pad starts exactly on rear board copper face; no board volume should overlap.
   if v>1e-7:wirehits.append(dict(a=n,b=m,volume=v))
motion=[]
for t in [0,.05,.10,.15,.20,.25]:
 s=slider.copy();s.translate(V(0,0,t));hits=[]
 for n,solid in fixed.items():
  if gap(s,solid)<1e-8:
   v=s.common(solid).Volume
   if v>1e-7:hits.append(dict(other=n,volume=v))
 motion.append(dict(stroke=t,hits=hits,spring_length=5.8-t,actuator_height_from_PCB=3.6-t))
s=slider.copy();s.translate(V(0,0,.30));over=sum(s.common(t).Volume for t in [left,right])
service=[]
for t in [0,25,50,67]:
 s=refill.copy();s.translate(V(0,0,-t));hits=[]
 for n,solid in {**fixed,'Slider':slider}.items():
  if gap(s,solid)<1e-8:
   v=s.common(solid).Volume
   if v>1e-7:hits.append(dict(other=n,volume=v))
 service.append(dict(extraction=t,hits=hits))
# Actual contextual comparison: replace obsolete abstractcassette only; retain actualboard/power/refill.
P=R.parent/'contact_near_cassette_2354';d=A.openDocument(str(P/'B52.FCStd'));context={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and o.Label not in ['contact','refill','Indicator_budget_NOT_SELECTED_PART']};A.closeDocument(d.Name)
# Additional current RC delta, exact native extraction accompanies results; R503/C504 far away unchanged context not remapped here.
rc=json.loads((R/'context_rc_snapshot.json').read_text())
if hashlib.sha256(Path(rc['source']).read_bytes()).hexdigest()!=rc['sha256']:raise ValueError('RC source changed')
for p in rc['parts']:
 context.pop(p['ref'],None);a,b,c,d=p['bounds'];lo=2.264793176328504-p['height_assumption'] if p['side']=='B.Cu' else 3.194793176328504;hi=2.264793176328504 if p['side']=='B.Cu' else 3.194793176328504+p['height_assumption'];context[p['ref']+'_latest']=box(a-7,c-7,lo,hi,127-d,127-b)
context_hits=[]
for n,s in {**fixed,'Slider':slider,**wire}.items():
 for m,t in context.items():
  if gap(s,t)<1e-8:
   v=s.common(t).Volume
   if v>1e-7:context_hits.append(dict(a=n,b=m,volume=v))
doc=A.newDocument('CompactContactCandidate')
for n,s in S.items():o=doc.addObject('Part::Feature',n);o.Shape=s
# Include current mainboard context as a distinct group, not fused into the mechanism.
g=doc.addObject('App::DocumentObjectGroup','Context_ONLY')
for n,s in context.items():o=doc.addObject('Part::Feature','CTX_'+n.replace('.','_'));o.Label='CTX_'+n;o.Shape=s;g.addObject(o)
doc.recompute();doc.saveAs(str(R/'compact_contact_candidate.FCStd'));vols={o.Name:o.Shape.Volume for o in doc.Objects if hasattr(o,'Shape')};A.closeDocument(doc.Name)
doc=A.openDocument(str(R/'compact_contact_candidate.FCStd'));valid=all(o.Shape.isValid()for o in doc.Objects if hasattr(o,'Shape'));drift=max(abs(vols[o.Name]-o.Shape.Volume)for o in doc.Objects if hasattr(o,'Shape'));A.closeDocument(doc.Name)
result=dict(status='EXPERIMENTAL_CASSETTE_NOFAB_NOT_CONSUMER_RELEASE',local_collisions=checks,wire_envelope_collisions=wirehits,motion=motion,overstroke_0p30_housing_overlap_mm3=over,refill_service=service,current_B52_context_collisions=context_hits,reopen_valid=valid,reopen_volume_drift=drift,physical_bounds=dict(body_OD=7.6,body_Z=[62,80.6],axis=[0,-3.8],carrier_bounds=[-3.75,3.75,-6.4,-.4,78.4,79.2],max_body_radius_about_pen=7.6),terminal_candidate=dict(CONTACT=[-2.3,-1.6,79.2],GND=[2.3,-1.6,79.2],meaning='Own carrier TH wire pad rear surface, nominal calibratedPCB position; true vendor switch terminals are separately mapped',straight_exit='+Z through rear relieved apertures; no qualified bend or strain relief',PCB_adjustment_Z=[-.2,.2],wire_OD_study_max=1.6,wire_OD_basis='aperture minimum2.0 minus .2 clearance each side; NOT wire material/current/bend approval'),limits=['SPVE minimum50uA@3V not met by frozen100k source;47k conditional only','SPVE50000cycle catalog rating not consumer lifetime approval','BodyXY nominal with explicitstudy allowance, formal supply tolerances pending','D001 rate tolerance/working-load force curve and fatigue not fully qualified','M1.6 threads not modeled; right half requires actualtap and pullout/load test; no tightening torque approval','Softgrip own customgeometry only; elastomer material/friction/supply not selected','No approved externalwire path/bend; Alpha2840R6.096 not proved by portapertures','Per-unit measuredON/OFF calibration required; fixed nominalpreload invalid at vendorON±.2 corners','No target handwritingaccuracy, opticaltipcalibration, wholebody or380CNY budget qualification'])
(R/'cad_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
