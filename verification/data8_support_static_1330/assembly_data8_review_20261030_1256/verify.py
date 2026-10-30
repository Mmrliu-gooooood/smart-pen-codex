from pathlib import Path
import json
O=Path(__file__).resolve().parent
j=json.load(open(O/'results.json'));r=j['stages'][0];g=json.load(open(O/'placement_results.json'))
def require(v,msg):
 if not v:raise RuntimeError(msg)
require(r['all103_contract_equal']and r['reference_zone_definitions_equal'],'contracts/zone')
require(r['outline']==[0,-6.5,14,93.3],'outline')
require((r['new_outer_tracks'],r['new_inner_tracks'],r['new_vias'])==(32,7,11),'counts')
for t in r['rows']:
 for typ in ['envelope_hits','fab_bbox_hits','courtyard_hits']:
  require(not any(not h['declared_target_ref']for h in t[typ]),'non-target interference')
  if t['type']=='via':require(not t[typ],'via underbody/courtyard')
 require(not any(h['ref']=='U201'for h in t['fab_bbox_hits']),'U201 body intrusion')
for c in g:require(not c['hits']and c['fullbody_count']==104 and c['negative_R210_left3_overlap_R216_mm3']>0,'four context placement')
require(r==json.load(open(O/'results_normal.json'))['stages'][0],'normal/-O finite mismatch')
require(g==json.load(open(O/'placement_normal.json')),'normal/-O CAD mismatch')
(O/'verification.json').write_text(json.dumps({'status':'PASS_NARROW_NOMINAL_ONLY','finite_shapes':50,'exterior_tracks':32,'vias':11,'full_static_entities':104,'contracts':103,'four_contexts':4,'negative_pose_control':'R210 shifted−3X overlaps R216, detected','U201_Fab_projection_intrusions':0,'all_via_fullbudget_Fab_courtyard_intersections':0,'normal_optimized_equal':True},indent=2)+'\n')
