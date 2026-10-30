from pathlib import Path
import json
D=Path(__file__).resolve().parent
for s in ['verify','compare_drc','plane_reference_audit','measure_routes','continuous_reference','aon_margin_counterfactual','extra','vio_pin','vio_erratum','numeric_erratum']:
 a=json.loads((D/(s+'_normal.json')).read_text());b=json.loads((D/(s+'_optimized.json')).read_text())
 if a!=b:raise RuntimeError('Normal/-O mismatch '+s)
def read(s):return json.loads((D/(s+'.json')).read_text())
n=read('negative_results')
if n['cases']!=6 or len(n['runs'])!=12 or any(v['exit']!=1 for v in n['runs']):raise RuntimeError('Negative evidence')
if read('replay_result')['pcb_sha256']!='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038':raise RuntimeError('Replay SHA')
p=read('plane_reference_audit');want={'USB_EN1':.000592207987,'SENS_VIO_1V8':.179811208664,'SENS_SCL':.094964881603,'CAM_SCL':2.9815e-08};actual=p['old_track_new_reference_unique_union_mm2']
if set(actual)!=set(want)or any(abs(actual[k]-v)>1e-9 for k,v in want.items())or p['new_RF_region_intrusions']:raise RuntimeError('Reference delta differs')
a=read('aon_margin_counterfactual')
if len(a['affected_vias'])!=14 or a['old_pad_group_splits']or a['additional_AON_area_removed_mm2']<6:raise RuntimeError('Counterfactual ineffective')
print(json.dumps({'normal_optimized_pairs_equal':10,'negative_rejections':12,'replay_and_refill_exact':True,'reference_loss_not_zero':actual,'AON_counterfactual_static_only':True,'decision':'STATIC_BASELINE_ACCEPTABLE_WITH_BOTH_MANDATORY_ERRATA_NOFAB'},indent=2))
