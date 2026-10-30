from pathlib import Path
import json
from pcb_preflight import verify
D=Path(__file__).resolve().parent
for s in ['verify','compare_drc','reference_and_lengths','continuous_return_screen','extra']:
 a=json.loads((D/(s+'_normal.json')).read_text());b=json.loads((D/(s+'_optimized.json')).read_text())
 if a!=b:raise RuntimeError('Mode mismatch '+s)
r=json.loads((D/'replay_and_refill.json').read_text())
if not all(v['exact_candidate_sha_match']and v['verify_exit']==0 for v in r.values()):raise RuntimeError('Replay identity')
n=json.loads((D/'negative_results.json').read_text())
if len(n)!=10 or not all(v['exit_code']==1 and v['actual_reason'].startswith(v['expected_reason_prefix'])for v in n):raise RuntimeError('Negatives')
rr=json.loads((D/'reference_and_lengths.json').read_text())
if any(v['outside_explicit_pin12_outward_approach_mm2']>1e-12 for v in rr['new_IRQ_F_body_intersections']):raise RuntimeError('Pin12 approach violation')
try:verify(D/'native/mainboard_revD.kicad_pcb',json.loads((D/'preflight_lock.json').read_text()),'manufacturing')
except ValueError as e:reason=str(e)
else:raise RuntimeError('Manufacturing unexpectedly allowed')
print(json.dumps({'normal_optimized_report_pairs_equal':5,'replay_refill_exact_hash':True,'negative_rejections':10,'pin12_outward_approach_screen':True,'manufacturing_rejection':reason,'decision':'ACCEPT_BOUNDED_IRQ_STATIC_BASELINE_ONLY_NOFAB'},indent=2))
