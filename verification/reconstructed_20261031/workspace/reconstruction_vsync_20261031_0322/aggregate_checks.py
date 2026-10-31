from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;checks={}
def read(n):return json.loads((D/n).read_text())
def req(k,v):
 checks[k]=bool(v)
 if not v:raise RuntimeError(k)
a=read('final_verification.json');b=read('final_verification_optimized.json');req('312_native_checks_equal_normalO',a==b and len(a['checks'])==312 and all(a['checks'].values()));req('finite_wholepath_normalO',read('finite_final.json')==read('finite_final_optimized.json')and not read('finite_final.json')['errors']);req('source_roles_normalO',read('source_roles.json')==read('source_roles_optimized.json')and all(read('source_roles.json')['checks'].values()));req('native_wrapper_normalO',read('anchor_regression.json')==read('anchor_regression_optimized.json')and len(read('anchor_regression.json')['rows'])==6)
d=read('final_drc.json');req('actual_alltrack_parity_0_43_0',[len(d[x])for x in ['violations','unconnected_items','schematic_parity']]==[0,43,0]);req('refill_byte_exact',read('final_fill_reload.json')['native_refill_reload_bytes_equal']);req('native_contracts',all(read('final_native_contract.json')['checks'].values()));req('no_exact_collinear_pairs',read('collinear_screen.json')['count']==0)
for i in range(3):
 a=read(f'final_validation/negative_{i}.json');b=read(f'final_validation/negative_optimized_{i}.json');a.pop('normal_or_optimized');b.pop('normal_or_optimized');req('negative_normalO_'+str(i),a==b and a['reversible_raw_native_replay_exact_both_directions']and a['cut']['detected'])
 for mode in ['','optimized_']:
  d=read(f'final_validation/saved_cut_{mode}{i}_drc.json');req('saved_cut_'+mode+str(i),[len(d[x])for x in ['violations','unconnected_items','schematic_parity']]==[1,44,0]and d['violations'][0]['type']=='track_dangling')
r=read('final_reference.json');req('reference_all2765_disclosed11losses',r['all_retained_projections']==2765 and len(r['retained_reference_losses'])==11);req('one_AON_mainland',len(read('plane_islands_final.json')['baseline']['islands'])==len(read('plane_islands_final.json')['candidate']['islands'])==1);req('AON_current_via_plane_inventory_unchanged',read('plane_islands_final.json')['baseline']['AON_vias_not_in_plane']==read('plane_islands_final.json')['candidate']['AON_vias_not_in_plane']);req('selected_sha',hashlib.sha256((D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest()=='5f78698406ba7ab296ff6bdb2d334f2ecab003e92f3258e3c44adceb56b1e433');req('all_power_old_copper_exact',all(q[0]not in['GND','3V3_AON','SENS_VIO_1V8']for q in read('final_verification.json')['removed'].values())and all(q[0]not in['GND','3V3_AON','SENS_VIO_1V8']for q in read('final_verification.json')['added'].values()))
req('bounded_shorter_junction_proposal_rejected',read('local_junction_prefilter/results.json')['status']=='REJECTED_JOINT_PREFLIGHT'and bool(read('local_junction_prefilter/results.json')['errors']))
(D/'aggregate_checks.json').write_text(json.dumps({'checks':checks,'scope':'Static evidence only; nonzero reference/fill changes and long bias path remain explicit engineering gates.'},indent=2));print(len(checks),'aggregate gates pass')
