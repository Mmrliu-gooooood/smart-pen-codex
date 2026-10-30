from pathlib import Path
import json
D=Path(__file__).resolve().parent
for s in ['verify','compare_drc','plane_reference_audit','connector_mask_audit','extra','path_mask']:
 a=json.loads((D/(s+'_normal.json')).read_text());b=json.loads((D/(s+'_optimized.json')).read_text())
 if a!=b:raise RuntimeError('Normal/-O mismatch '+s)
def read(s):return json.loads((D/(s+'.json')).read_text())
n=read('negative_results')
if n['cases']!=6 or len(n['runs'])!=12 or any(v['exit']!=1 for v in n['runs']):raise RuntimeError('Negative evidence')
r=read('replay_result')
if r['pcb_sha256']!='4994ba2d8810b2f44434bd43f7cecfaab16aa601a0837c9923883613583554f6':raise RuntimeError('Replay SHA')
p=read('plane_reference_audit')
if p['affected_old_tracks']or p['new_RF_region_intrusions']:raise RuntimeError('Reference/RF regression')
m=read('connector_mask_audit')
if m['pin13_inner_bar_intersection_with_J202_mask_mm2']!=0 or m['new_track_explicit_mask_openings']:raise RuntimeError('Mask exposure')
print(json.dumps({'normal_optimized_pairs_equal':6,'negative_rejections':12,'replay_and_refill_exact':True,'native_mask_and_ground_return_static_checks':True,'decision':'ACCEPT_J202_GROUND_STATIC_BASELINE_ONLY_NOFAB'},indent=2))
