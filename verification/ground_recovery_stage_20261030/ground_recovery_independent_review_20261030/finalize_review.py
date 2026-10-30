from pathlib import Path
import json,hashlib,csv
O=Path(__file__).resolve().parent;D=O/'mirror/smart_pen_next_20261028/hardware/ground_recovery_native_0818';R=O.parent/'smart_pen_next_20261028';checks={}
for name in ['verify','physical_native','probe_access','negative_ground','replay_rollback']:
 a=(O/f'raw/{name}_normal.json').read_bytes();b=(O/f'raw/{name}_optimized.json').read_bytes();checks[name+'_byte_equal']=a==b
 if a!=b:raise RuntimeError(name)
cases=json.load(open(O/'raw/negative_ground_normal.json'))['cases'];checks['cuts']=[{'case':c['case'],'lost':c['actual_lost_pads'],'islands':c['newly_isolated_components'],'drc':c['actual_DRC_unconnected_parity']}for c in cases]
if len(cases)!=20:raise RuntimeError('20cuts')
for label in ['base','candidate']:
 d=json.load(open(D/'checks'/label/'drc.json'));checks[label+'_drc']=[len(d[k])for k in ['violations','unconnected_items','schematic_parity']];e=json.load(open(D/'checks'/label/'erc.json'));checks[label+'_erc']=[(v['severity'],v['type'])for s in e['sheets']for v in s['violations']]
rows=json.load(open(O/'raw/frozen_hashes.json'));checks['frozen_unchanged']=all(hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']for x in rows)
if not checks['frozen_unchanged']:raise RuntimeError('source changed')
checks['bom_candidate_rows']=[r for r in csv.DictReader(open(D/'checks/candidate/bom.csv'))if r['Reference']in ['U205','C209','R202']]
checks['negative_exact_uuid_comparison']=json.load(open(O/'raw/exact_negative_comparison.json'))['status']
(O/'raw/completion.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
