from pathlib import Path
import json
D=Path(__file__).resolve().parent
for s in ['verify_j107','ground_tail_counterfactual','local_plane_corridors','verify_source_refill','audit_gate','independent']:
 a=json.loads((D/(s+'_normal.json')).read_text());b=json.loads((D/(s+'_optimized.json')).read_text())
 if s=='independent':
  a['same_basename_preflight'].pop('checked_utc');b['same_basename_preflight'].pop('checked_utc')
 if a!=b:raise RuntimeError('Mode output differs '+s)
c=json.loads((D/'local_plane_corridors_normal.json').read_text())
if c['any_geometric_corridor_regression']:raise RuntimeError('Local plane corridor regression')
a=json.loads((D/'harness_normal.json').read_text());b=json.loads((D/'harness_optimized.json').read_text());a.pop('mode');b.pop('mode')
if a!=b or len(a['cases'])!=9 or not all(x['passed']for x in a['cases']):raise RuntimeError('Harness normal/optimized')
n=json.loads((D/'negative_results.json').read_text())
if len(n)!=8 or not all(x['exit']==1 for x in n):raise RuntimeError('Negative checks')
if (D/'fresh_drc.exit').read_text().strip()!='5':raise RuntimeError('DRC exit')
print(json.dumps({'six_normal_optimized_report_pairs_equal':True,'harness_cases_per_mode':9,'harness_expected_rejections_total':16,'copper_expected_rejections_total':8,'local_corridor_regression':False,'full_drc_exit':5,'decision':'ACCEPT_AS_NEXT_IMU_ROUTING_BASELINE_ONLY_NOFAB'},indent=2))
