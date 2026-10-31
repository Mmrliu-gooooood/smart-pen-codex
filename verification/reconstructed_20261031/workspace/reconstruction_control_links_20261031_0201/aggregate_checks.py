from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;checks={}
def req(k,v):
 checks[k]=bool(v)
 if not v:raise RuntimeError(k)
def read(n):return json.loads((D/n).read_text())
a=read('final_verification.json');b=read('final_verification_optimized.json');req('305_native_checks_equal_normal_optimized',a==b and len(a['checks'])==305 and all(a['checks'].values()));d=read('final_drc.json');req('actual_DRC_alltrack_schematic_parity_0_49_0',[len(d[x])for x in ['violations','unconnected_items','schematic_parity']]==[0,49,0]);req('refill_bytes_exact',read('final_fill_reload.json')['native_refill_reload_bytes_equal']);req('native_contracts',all(read('final_native_contract.json')['checks'].values()))
for i in range(2):
 a=read(f'final_validation/negative_{i}.json');b=read(f'final_validation/negative_optimized_{i}.json');a.pop('normal_or_optimized');b.pop('normal_or_optimized');req('negative_normalO_'+str(i),a==b and a['reversible_raw_native_replay_exact_both_directions']);d=read(f'final_validation/saved_cut_{i}_drc.json');req('saved_cut_detected_'+str(i),[len(d[x])for x in ['violations','unconnected_items','schematic_parity']]==[1,50,0]and d['violations'][0]['type']=='track_dangling')
req('reference_all_old_other_nets_preserved',len(read('final_reference.json')['retained_reference_losses'])==1 and read('final_reference.json')['retained_reference_losses'][0]['net']=='CAM_SCL');req('sole_retained_loss_own_via_causal',read('causal_final.json')['remaining_loss_mm2']==0);req('AON_island_count_preserved',len(read('plane_islands_final.json')['baseline']['islands'])==len(read('plane_islands_final.json')['candidate']['islands'])==1);req('final_hash',hashlib.sha256((D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest()=='c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855');r={'checks':checks,'scope':'Static tests only. Own antipad attribution and one island do not establish SI/PDN/assembly/process qualification.'};(D/'aggregate_checks.json').write_text(json.dumps(r,indent=2));print(r)
