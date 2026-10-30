import sys,json,math,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parent;V=A.Vector
prior=R.parent/'compact_contact_cassette_backspacer_revB_0031'
d=A.openDocument(str(prior/'compact_contact_candidate.FCStd'))
S={o.Name:o.Shape.copy() for o in d.Objects if hasattr(o,'Shape') and o.Name!='Context_ONLY' and not o.Name.startswith('Wire_')};labels={o.Name:o.Label for o in d.Objects};A.closeDocument(d.Name)
snap=json.loads((R/'context_imu_snapshot.json').read_text())
if hashlib.sha256(Path(snap['source']).read_bytes()).hexdigest()!=snap['sha256']:raise ValueError('new PCB changed')
for p in snap['parts']:
 for key in list(S):
  if labels.get(key,'') in ['CTX_'+p['ref'],'CTX_'+p['ref']+'_latest']:S.pop(key)
 a,b,c,e=p['bounds'];key='CTX_'+p['ref']+'_dd55';S[key]=Part.makeBox(c-a,p['height_assumption'],e-b,V(a-7,3.194793176328504,127-e));labels[key]=key

def cyl(a,b,r):
 u=b-a;return Part.makeCylinder(r,u.Length,a,u)
def route(x,tx,shift=0):
 a=V(x,-1.6,78.4-.1143+shift);b=V(tx,2.264793176328504-.1143,75);u=b-a;u.normalize();core=cyl(a,b,.1143);coat=cyl(a+u*.8,b-u*.8,.3048);return a,b,core.fuse(coat),u
# Existing carrier holes replaced by actual new SMD lands: refill substrate holes only.
for x in [-2.3,2.3]:S['SwitchCarrierPCB']=S['SwitchCarrierPCB'].fuse(Part.makeCylinder(.3,.8,V(x,-1.6,78.4)))
# Full front insulating shim with switch window keeps lower connecting web.
S['FrontCalibrationShim']=Part.makeBox(7.5,6,.2,V(-3.75,-6.4,78.2)).cut(Part.makeBox(3.4,3.8,.4,V(-1.7,-5.7,78.1))).cut(Part.makeBox(8,2,.4,V(-4,-2.15,78.1)))
# Shift rear fastener +.5Z to clear full calibration envelope. Only the existing flange is refilled.
for key,x0,x1 in [('HousingLeft',-3.5,0),('HousingRight',0,3.5)]:
 fill=Part.makeCylinder(.9,x1-x0,V(x0,.6,78),V(1,0,0))
 S[key]=S[key].fuse(fill).cut(Part.makeCylinder(.9,8,V(-4,.6,78.5),V(1,0,0))).removeSplitter()
S['M1p6x8_at_78'].translate(V(0,0,.5))
# Proposed open machining grooves. Continuous union across calibration envelope; oversized groove is NOT grip qualification.
channels=[]
for x,tx in [(-2.3,-4),(2.3,-1.6)]:
 for shift in [-.2,-.1,0,.1,.2]:
  a,b,w,u=route(x,tx,shift);channels.append(cyl(a-u*.3,b+u*.3,.5048))
for key in ['HousingLeft','HousingRight','FrontCalibrationShim']:
 for c in channels:S[key]=S[key].cut(c)
 S[key]=S[key].removeSplitter()
# Side solder-access windows, keep +Y fastener-bearing material intact.
# Actual tool must fit diameter .6mm budget; this is not a selected soldering-tip specification.
S['HousingLeft']=S['HousingLeft'].cut(Part.makeBox(3,1.1,1.5,V(-4.45,-2.15,77.4))).removeSplitter()
S['HousingRight']=S['HousingRight'].cut(Part.makeBox(3,1.1,1.5,V(1.45,-2.15,77.4))).removeSplitter()
rows=[];wires={};collision=[];clearances=[]
# Removable interference-bushing trial: installed envelope only, material and force MUST be tested.
# Tube is prethreaded, seated axially into the straight machined bore before either wire end is soldered.
supports={}
for name,x,tx in [('CONTACT',-2.3,-4),('GND',2.3,-1.6)]:
 a,b,w,u=route(x,tx,0)
 supports['StrainBushing_'+name+'_TRIAL']=cyl(a+u*1.0,a+u*2.2,.5048).cut(cyl(a+u*.99,a+u*2.21,.3048))
S.update(supports)

for name,x,tx in [('CONTACT',-2.3,-4),('GND',2.3,-1.6)]:
 for shift in [-.2,0,.2]:
  a,b,w,u=route(x,tx,shift);hits=[];near=[]
  for key,t in S.items():
   if key.startswith('StrainBushing_'):continue
   if 'J103' in labels.get(key,''):continue # intentional host solder land target, separately mapped
   # carrier and SPVE move together with calibration, other prior motion envelope remains unchanged
   tt=t.copy()
   if key in ['SwitchCarrierPCB','SPVE_body_conservative','SPVE_actuator_at_rest']:tt.translate(V(0,0,shift))
   vol=w.common(tt).Volume
   if vol>1e-7:hits.append([key,vol])
   dist=w.distToShape(tt)[0]
   if dist<.3:near.append([key,dist])
  rows.append(dict(net=name,calibration_shift=shift,start_center=list(a),end_center=list(b),unit_tangent=list(u),straight_cut_length=(b-a).Length,strip_each_end=.8,insulated_length=(b-a).Length-1.6,collisions=hits,near=near))
  if shift==0:wires['Harness_'+name]=w
  collision+=hits
# Own solder budgets clipped to copper-facing planes; not vendor fillet process specification.
for name,x,tx in [('CONTACT',-2.3,-4),('GND',2.3,-1.6)]:
 a,b,w,u=route(x,tx,0)
 sa=cyl(a-u*.1,a+u*.65,.25).common(Part.makeBox(20,20,20,V(-10,-10,58.4)))
 sb=cyl(b-u*.65,b+u*.1,.25).common(Part.makeBox(20,20,20,V(-10,2.264793176328504-20,65)))
 S['Solder_'+name+'_carrier_STUDY']=sa;S['Solder_'+name+'_main_STUDY']=sb
# Reopened mainboard B52 destination, exclude coarse J103 terminal boxes only; they represent these soldered wires now.
S.update(wires)
doc=A.newDocument('ContactObliqueHarnessRevC')
for key,shape in S.items():o=doc.addObject('Part::Feature',key);o.Label=labels.get(key,key);o.Shape=shape
for i,c in enumerate(channels):pass
# no channels as physical solids
for key in ['CTX_J103_1','CTX_J103_2']: pass
doc.recompute();doc.saveAs(str(R/'contact_oblique_harness.FCStd'));A.closeDocument(doc.Name)
doc=A.openDocument(str(R/'contact_oblique_harness.FCStd'));valid=all(o.Shape.isValid() for o in doc.Objects if hasattr(o,'Shape'));counts={k:len(S[k].Solids) for k in ['HousingLeft','HousingRight','FrontCalibrationShim','SwitchCarrierPCB']};pair=wires['Harness_CONTACT'].distToShape(wires['Harness_GND'])[0];A.closeDocument(doc.Name)
res=dict(status='PROPOSED_STATIC_ASSEMBLY_PATH_NOT_STRAIN_RELIEF_OR_PRODUCTION_RELEASE',source_mainboard_sha256=snap['sha256'],carrier_sha256=hashlib.sha256((R/'contact_carrier_NOFAB.kicad_pcb').read_bytes()).hexdigest(),rows=rows,reopen_all_valid=valid,modified_part_solid_counts=counts,wire_pair_clearance=pair,collisions=collision,wire_radius=.3048,bare_conductor_nominal_radius=.1143,groove_radius=.5048,bend_curvature=0,calibration_requires_final_wire_cut_and_solder_after_calibration=True)
(R/'route_results.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
