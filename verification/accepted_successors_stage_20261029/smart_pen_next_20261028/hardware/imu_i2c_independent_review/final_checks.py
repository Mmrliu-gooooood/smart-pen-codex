from pathlib import Path
import json
D=Path(__file__).resolve().parent
for s in ['verify','compare_drc','measure','continuous_reference','via_plane_screen','return_plane_delta','aon_neck_counterfactual','mems_approach_screen','extra']:
 a=json.loads((D/(s+'_normal.json')).read_text());b=json.loads((D/(s+'_optimized.json')).read_text())
 if a!=b:raise RuntimeError('Normal/-O mismatch '+s)
def read(s):return json.loads((D/(s+'.json')).read_text())
v=read('via_plane_screen');r=v['critical_projection']['RF_F_copper_and_pads']
if v['new_RF_region_intrusions']or r['new_void_projected_overlap_mm2']!=0 or r['nearest_new_In1_void_to_copper_mm']<.35:raise RuntimeError('Project RF geometry screen')
if read('return_plane_delta')['items']:raise RuntimeError('Old reference projection lost')
a=read('aon_neck_counterfactual')
if len(a['affected_vias'])!=2 or a['old_pad_group_splits']or a['additional_AON_area_removed_mm2']<.5:raise RuntimeError('AON counterfactual ineffective')
if read('mems_approach_screen')['nonapproach_area_mm2']>1e-12:raise RuntimeError('MEMS outward approach')
n=read('negative_results')
if n['cases']!=5 or len(n['runs'])!=10 or any(x['exit']!=1 for x in n['runs']):raise RuntimeError('negative tests')
r=read('replay_result')
if r['pcb_sha256']!='6b44e149edf7e3b6c843375125a71247ece6c664eb531686dd3b451e1586ee71':raise RuntimeError('Replay SHA')
print(json.dumps({'normal_optimized_report_pairs':9,'negative_rejections':10,'exact_delta_replay_fresh_fill':True,'project_RF_screen_pass_only':True,'AON_edge_sliver_not_necessary_pad_connection':True,'MEMS_outward_approach_pass_only':True,'decision':'ACCEPT_STATIC_I2C_LAYOUT_BASELINE_ONLY_NOFAB'},indent=2))
