from pathlib import Path
import json,copy,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];data=json.loads((D/'recovery_plan.json').read_text())
def req(x,m):
 if not x:raise ValueError(m)
def check(p):
 objs=p['objects'];byid={x['uuid']:x for x in objs};req(len(byid)==len(objs)==5317,'object identities')
 req(sum(bool(x['new_conflicts'])for x in objs)==p['new_conflict_object_count'],'conflict count')
 req(sum(bool(x['original_violations'])for x in objs)==p['original_violation_track_object_count'],'hazard count')
 safe={x['uuid']for x in objs if not x['new_conflicts']and not x['original_violations']};req(len(safe)==p['candidate_object_count'],'safe count')
 req(all(x['geometry_candidate']==(x['uuid']in safe)for x in objs),'unsafe candidate')
 grouped=[u for c in p['components']for u in c['uuids']];req(len(grouped)==len(set(grouped))and set(grouped)==safe,'component partition')
 for c in p['components']:req(all(byid[u]['net']==c['net']for u in c['uuids']),'crossnet component')
 chosen=[]
 for row in p['net_summary']:
  net=row['net'];cs=[p['components'][i]for i in row['components']];req(all(c['net']==net for c in cs),'net component index')
  ids={u for u,x in byid.items()if x['net']==net};req(len(ids)==row['original_objects'],'net total');req(len(ids&safe)==row['retained_geometry_candidate_objects'],'net safe')
  if row['whole_track_net_candidate']:
   req(not row['new_geometry_conflict_objects']and not row['original_net_violation_hazard']and not row['relocated_terminals']and len(cs)==1,'whole-net invalid')
   req(set(cs[0]['fixed_pad_contacts'])==set(row['all_current_terminals']),'incomplete terminal set');chosen.append(net)
 req(chosen==p['whole_track_net_candidates'],'whole list')
 req('3V3_AON'not in chosen and'GND'not in chosen and'CAM_3V3_SW'not in chosen,'unsafe power inheritance')
 req(any(q['net']=='3V3_AON'and q['new_via_exclusion_union_mm2']>0 for q in p['old_fill_new_via_antipad_exclusions']),'missing AON holes')
 for q in p['old_fill_new_via_antipad_exclusions']:req(q['new_via_exclusion_union_mm2']<=sum(v['old_fill_exclusion_area_mm2']for v in q['vias'])+1e-8,'union excess')
check(data);tests=[]
p=copy.deepcopy(data);next(x for x in p['objects']if x['new_conflicts'])['geometry_candidate']=True;tests.append(('conflicting_object_marked_safe',p))
p=copy.deepcopy(data);next(x for x in p['net_summary']if x['net']=='3V3_AON')['whole_track_net_candidate']=True;tests.append(('AON_false_whole',p))
p=copy.deepcopy(data);p['components'][0]['uuids'].append(p['components'][0]['uuids'][0]);tests.append(('duplicate_component_member',p))
p=copy.deepcopy(data)
for q in p['old_fill_new_via_antipad_exclusions']:
 if q['net']=='3V3_AON':q['new_via_exclusion_union_mm2']=0
tests.append(('omit_AON_antipad',p))
reject=[]
for name,p in tests:
 try:check(p)
 except ValueError:reject.append(name)
 else:raise RuntimeError('NEGATIVE ACCEPTED '+name)
for path,expected in [(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb',data['baseline_sha']),(R/'hardware/dvp_mechanical_clearance_successor_1957/native/mainboard_revD.kicad_pcb',data['target_sha'])]:req(hashlib.sha256(path.read_bytes()).hexdigest()==expected,'input drift')
print(json.dumps({'status':'ACCOUNTING_AND_FAIL_CLOSED_CHECKS_PASS','objects':len(data['objects']),'components':len(data['components']),'whole_track_candidates':len(data['whole_track_net_candidates']),'negative_cases_rejected':reject,'native_inputs_unchanged':True,'no_native_candidate_created':True},indent=2))
