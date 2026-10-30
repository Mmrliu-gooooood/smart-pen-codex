import sys,json,math,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;V=A.Vector
def req(b,m):
 if not b:raise ValueError(m)
r=json.loads((R/'fixture_results.json').read_text());req(not r['context_collisions'],'context collision');req(not r['fixture_collisions'],'fixture collision');req(not r['RF_project_prism_collisions'],'RF intrusion');req(r['reopen_valid'],'invalid CAD');req(all(n==1 for n in r['part_solid_counts'].values()),'disconnected part')
n=json.loads((R/'native_contract.json').read_text());req(hashlib.sha256(Path(n['source']).read_bytes()).hexdigest()==n['sha256'],'native changed');req(n['all_102_footprint_geometry_pad_identity_equal'],'physical delta');req(all(not c['track_pad_via_bbox_hits']for c in n['contacts']),'edge copper bbox hit')
d=A.openDocument(str(R/'common_datum_bench.FCStd'));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')};parts={k:s for k,s in S.items()if not k.startswith('REF_')};ctx={k[4:]:s for k,s in S.items()if k.startswith('REF_')}
def disjoint_bbox(a,b):
 x=a.BoundBox;y=b.BoundBox
 return any(getattr(x,k+'Max')<=getattr(y,k+'Min')+1e-9 or getattr(y,k+'Max')<=getattr(x,k+'Min')+1e-9 for k in'XYZ')
def hits(a,others):
 out=[]
 for k,t in others.items():
  if disjoint_bbox(a,t):continue
  v=a.common(t).Volume
  if v>1e-7:out.append([k,v])
 return out
# Assembly sampled Y translations; bare assembly before wire soldering, removables explicitly absent.
cas={k:s for k,s in ctx.items()if not k.startswith(('CTX_','Harness_','Solder_','StrainBushing'))}
openbase={k:s for k,s in parts.items()if not k.startswith(('Cassette_top','Cassette_upper','Collar_screw','PCB_keeper','Keeper_screw','Keeper_hardstop','Antirot_shim','Axial_shim','Fork_'))}
assembly=[]
for shift in [0,.1,.5,1,2,5,10]:
 h=[]
 for k,s in cas.items():
  q=s.copy();q.translate(V(0,shift,0));h.extend([[k]+x for x in hits(q,openbase)])
 assembly.append(dict(stage='cassette_into_open_base_before_mainboard',shiftY=shift,hits=h));req(not h,'cassette insertion collision '+str(h[:3]))
# Assemble removable keyed jaws and their shim packs horizontally, then insert fastening screws.
for side in [-1,1]:
 which='R'if side>0 else'L'
 group={k:s for k,s in parts.items()if k=='Fork_jaw_'+which or k.startswith('Fork_keyshim_'+which) or k.startswith('Axial_shim_'+str(side)+'_')or k=='Antirot_shim_'+str(side)}
 for shift in [0,.1,.5,1,2,5,10]:
  h=[]
  for key,solid in group.items():
   q=solid.copy();q.translate(V(side*shift,0,0));others={**openbase,**cas};h.extend([[key]+v for v in hits(q,others)])
  assembly.append(dict(stage='sideways_keyed_fork_and_shims',side=side,offsetX=side*shift,hits=h));req(not h,'fork insertion '+str(h[:3]))
board={k:s for k,s in ctx.items()if k.startswith('CTX_')and k!='CTX_power'}
fixture_open={k:s for k,s in parts.items()if not k.startswith(('PCB_keeper','Keeper_screw','Keeper_hardstop','PCB_side_shim'))}
others={**fixture_open,**cas}
for shift in [0,.1,.5,1,2,5,10]:
 h=[]
 for k,s in board.items():
  q=s.copy();q.translate(V(0,shift,0));h.extend([[k]+x for x in hits(q,others)])
 assembly.append(dict(stage='mainboard_from_plusY_keepers_and_side_shims_removed',shiftY=shift,hits=h));req(not h,'board insertion collision '+str(h[:3]))
access=[]
for side in [-1,1]:
 for shift in [-.2,0,.2]:
  a=V(side*8,-1.6,78.1+shift);b=V(side*2.5,-1.6,78.1+shift);u=b-a;t=Part.makeCylinder(.3,u.Length,a,u);h=hits(t,parts);access.append(dict(side=side,shift=shift,hits=h));req(not h,'fixture blocks solder access')
# Regression: preinstalling keyed forks before lowering the cassette is not a valid sequence.
bad_insert=[]
for shift in [.1,.5,1,2]:
 volume=0
 for k,solid in cas.items():
  q=solid.copy();q.translate(V(0,shift,0))
  for j,t in parts.items():
   if j.startswith(('Fork_jaw','Axial_shim','Antirot_shim')):volume+=q.common(t).Volume
 bad_insert.append(dict(shiftY=shift,overlap_mm3=volume))
req(any(v['overlap_mm3']>1e-5 for v in bad_insert),'assembly negative not detected')
old_post=Part.makeBox(5,13.2647931763,2,V(-12,-11,94));old_gap=old_post.distToShape(ctx['CTX_power'])[0];req(old_gap<.1,'power touch negative')
powergap=min(s.distToShape(ctx['CTX_power'])[0]for s in parts.values());req(powergap>=.1-1e-7,'fixture loads power budget')
# Whole battery budget deliberately reserved behind Z141, none of this fixture reaches it.
maxz=max(s.BoundBox.ZMax for s in parts.values());req(maxz<141,'battery budget hit')
# Relative displacement sensitivity, not a qualified strain allowable.
rr=json.loads((R.parent/'contact_oblique_harness_revC_0038/route_results.json').read_text());sens=[]
for v in rr['rows']:
 if v['calibration_shift']!=0:continue
 u=v['unit_tangent'];L=v['straight_cut_length'];sens.append(dict(net=v['net'],length_mm=L,unit_tangent=u,each_axis_relative_0p01_mm_worst_linear_deltaL=sum(abs(t)for t in u)*.01,axialZ_0p01_mm_linear_strain=abs(u[2])*.01/L,each_axis_uncalibrated_print_plusminus0p2_each_body_worst_deltaL=sum(abs(t)for t in u)*.4))
# Preserve exact nominal support plane, not undocumented elastic simulation.
out=dict(rejected_preinstalled_forks=bad_insert,rejected_original_power_touch_gap=old_gap,status='BENCH_COMMON_DATUM_GEOMETRY_ONLY_NOFAB_NOT19MM_PRODUCT',source_native=n['sha256'],assembly_samples=assembly,solder_access_samples=access,minimum_fixture_to_power_budget_mm=powergap,maximum_fixture_Z=maxz,battery_axial_gap_to_reserved_Z141=141-maxz,relative_displacement_sensitivity=sens,qualified_allowable_joint_motion_mm=None,unloaded_metrology_target_each_axis_mm=.01,metrology_target_not_fatigue_allowance=True,printed_plusminus0p2_is_scenario_not_machine_spec=True,RF_rule_prism_no_fixture=True,fixture_parts=len(parts),all_parts_single_solid=all(len(s.Solids)==1 for s in parts.values()))
# Native re-export for geometry exchange only. Manufacturing pilot/tapped holes require process drawing.
tmp=R.parent/'common_datum_bench_revD_verify_scratch';tmp.mkdir(exist_ok=True)
objs=[o for o in d.Objects if not o.Name.startswith('REF_')];Part.export(objs,str(tmp/'reexport_REFERENCE_ONLY.step'));A.closeDocument(d.Name);st=Part.read(str(tmp/'reexport_REFERENCE_ONLY.step'));req(st.isValid(),'STEP');out['STEP_valid']=st.isValid();out['STEP_solids']=len(st.Solids)
if '--read-only'not in sys.argv:(R/('verify_optimized.json'if sys.flags.optimize else'verify_normal.json')).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
