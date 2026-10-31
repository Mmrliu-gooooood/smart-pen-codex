from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;checks={}
def read(n):return json.loads((D/n).read_text())
def req(k,v):
 checks[k]=bool(v)
 if not v:raise RuntimeError(k)
a=read('final_verification.json');b=read('final_verification_optimized.json');req('312_native_checks_equal_normal_optimized',a==b and len(a['checks'])==312 and all(a['checks'].values()));req('finite_fullpath_normal_optimized',read('finite_final.json')==read('finite_final_optimized.json')and not read('finite_final.json')['errors']);req('source_roles_normal_optimized',read('source_roles.json')==read('source_roles_optimized.json')and all(read('source_roles.json')['checks'].values()));req('native_wrapper_regression',read('anchor_regression.json')==read('anchor_regression_optimized.json')and len(read('anchor_regression.json')['rows'])==9)
d=read('final_drc.json');req('actual_alltrack_parity_0_45_0',[len(d[x])for x in ['violations','unconnected_items','schematic_parity']]==[0,45,0]);req('refill_byte_exact',read('final_fill_reload.json')['native_refill_reload_bytes_equal']);req('native_contracts',all(read('final_native_contract.json')['checks'].values()));req('no_exact_collinear_pairs',read('collinear_screen.json')['count']==0)
for i in range(4):
 a=read(f'final_validation/negative_{i}.json');b=read(f'final_validation/negative_optimized_{i}.json');a.pop('normal_or_optimized');b.pop('normal_or_optimized');req('negative_normalO_'+str(i),a==b and a['reversible_raw_native_replay_exact_both_directions']and a['cut']['detected'])
 for mode in ['','optimized_']:
  d=read(f'final_validation/saved_cut_{mode}{i}_drc.json');req('saved_cut_'+mode+str(i),[len(d[x])for x in ['violations','unconnected_items','schematic_parity']]==[1,46,0]and d['violations'][0]['type']==('via_dangling'if i==0 else'track_dangling'))
r=read('final_reference.json');req('exact_reference_characterization',r['all_retained_projections']==2509 and len(r['retained_reference_losses'])==4 and sorted((q['net'],q['reference_layer'],q['lost_mm2'])for q in r['retained_reference_losses'])==sorted([('3V3_AON','In1.Cu',1.889415e-6),('3V3_AON','In1.Cu',.0006174770325),('CAM_D3','In2.Cu',.0929360006185),('CAM_D5','In2.Cu',.19140339425)]));req('AON_island_count_one',len(read('plane_islands_final.json')['baseline']['islands'])==len(read('plane_islands_final.json')['candidate']['islands'])==1);req('AON_outside_via_inventory_unchanged',read('plane_islands_final.json')['baseline']['AON_vias_not_in_plane']==read('plane_islands_final.json')['candidate']['AON_vias_not_in_plane']);req('selected_sha',hashlib.sha256((D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest()=='d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b')
(D/'aggregate_checks.json').write_text(json.dumps({'checks':checks,'scope':'All are static evidence gates only. Real declared reference/PDN/return regressions are characterized, not waived or renamed zero.'},indent=2));print(len(checks),'aggregate gates pass')
