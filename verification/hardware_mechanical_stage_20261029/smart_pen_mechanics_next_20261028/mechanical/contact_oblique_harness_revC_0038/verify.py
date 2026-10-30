import sys,json,hashlib,math
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;V=A.Vector
def req(b,s):
 if not b:raise ValueError(s)
r=json.loads((R/'route_results.json').read_text());req(not r['collisions'],'route collision');req(r['reopen_all_valid'],'invalid reopened');req(all(x==1 for x in r['modified_part_solid_counts'].values()),'disconnected part');req(r['wire_pair_clearance']>.1,'wire pair');d=A.openDocument(str(R/'contact_oblique_harness.FCStd'));S={o.Name:o.Shape.copy() for o in d.Objects if hasattr(o,'Shape')};A.closeDocument(d.Name)
physical=['HousingLeft','HousingRight','SwitchCarrierPCB','FrontCalibrationShim','RearCalibrationShim','SPVE_body_conservative','M1p6x8_at_66','M1p6x8_at_78','Slider'];hits=[]
for i,k in enumerate(physical):
 for j in physical[i+1:]:
  v=S[k].common(S[j]).Volume
  if v>1e-7:hits.append([k,j,v])
req(not hits,'internal collision')
checks={};context={k:s for k,s in S.items() if k.startswith('CTX_') and 'J103' not in k}
for k in physical+[k for k in S if k.startswith(('Solder_','StrainBushing'))]:
 for j,t in context.items():
  v=S[k].common(t).Volume
  if v>1e-7:hits.append([k,j,v])
req(not hits,'context collision')
for k in [k for k in S if k.startswith(('Solder_','StrainBushing'))]:
 for j in physical:
  req(S[k].common(S[j]).Volume<1e-7,'solder or support intersects '+k+'/'+j)

new=[k for k in S if k.endswith('_dd55')];newmin={}
for k in new:
 for j,t in S.items():
  if j==k or not j.startswith('CTX_'):continue
  v=S[k].common(t).Volume
  req(v<1e-7,'new IMU part collision '+k+'/'+j)
 b=S[k].BoundBox;newmin[k]=max(math.hypot(x,y)for x in[b.XMin,b.XMax]for y in[b.YMin,b.YMax])
 req(newmin[k]<=7.9,'radial overrun')
access=[]
for sign in [-1,1]:
 for shift in [-.2,0,.2]:
  a=V(sign*8,-1.6,78.1+shift);b=V(sign*2.5,-1.6,78.1+shift);u=b-a;t=Part.makeCylinder(.3,u.Length,a,u);h=[]
  for k in physical:
   q=S[k].copy()
   if k in ['SwitchCarrierPCB','SPVE_body_conservative']:q.translate(V(0,0,shift))
   v=t.common(q).Volume
   if v>1e-7:h.append([k,v])
  access.append(dict(side=sign,shift=shift,tool_diameter_budget=.6,hits=h));req(not h,'solder access blocked '+str(h))
motion=[]
for stroke in [0,.05,.1,.15,.2,.25]:
 t=S['Slider'].copy();t.translate(V(0,0,stroke));h=[]
 for k,q in S.items():
  if k.startswith(('Harness_','Solder_')):
   v=t.common(q).Volume
   if v>1e-7:h.append([k,v])
 motion.append(dict(stroke=stroke,hits=h));req(not h,'moving slider hits wire')
# Regression counterexample: uncut RevB housing obstructs this actual wire route.
d=A.openDocument(str(R.parent/'compact_contact_cassette_backspacer_revB_0031/compact_contact_candidate.FCStd'));negative=sum(S['Harness_CONTACT'].common(d.getObject(k).Shape).Volume for k in ['HousingLeft','HousingRight']);A.closeDocument(d.Name);req(negative>.1,'negative collision not caught')
# Export only own reference solids; original long refill and context intentionally excluded.
d=A.openDocument(str(R/'contact_oblique_harness.FCStd'))
objs=[o for o in d.Objects if hasattr(o,'Shape') and not o.Name.startswith('CTX_') and o.Name!='D1_nominal']
Part.export(objs,str(R/'oblique_harness_REFERENCE_ONLY.step'))
A.closeDocument(d.Name)
step=Part.read(str(R/'oblique_harness_REFERENCE_ONLY.step'));req(step.isValid(),'STEP invalid')

out=dict(status='LOCAL_GEOMETRY_PASS_PROCESS_AND_STRAIN_RELIEF_GATED',internal_and_context_collisions=hits,new_native_IMU_radial_max_mm=newmin,side_solder_access=access,slider_motion_vs_harness=motion,old_uncut_housing_negative_overlap_mm3=negative,step_valid=step.isValid(),step_solid_count=len(step.Solids),source_sha256=r['source_mainboard_sha256'],all_current_shapes_valid=all(s.isValid()for s in S.values()),all_calibration_routes_independent_cut_lengths=True)
(R/('verify_optimized.json' if sys.flags.optimize else 'verify_normal.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
