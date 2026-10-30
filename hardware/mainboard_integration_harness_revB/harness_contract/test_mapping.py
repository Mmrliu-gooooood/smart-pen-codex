from pathlib import Path
import json,copy,subprocess,sys
from verify_mapping import validate,ContractError,check_locks,ROOT
D=Path(__file__).resolve().parent;c=json.loads((D/'power_mode_mapping.json').read_text());rows=[]
def case(name,fn,accept):
 try:result=fn();ok=accept;detail=result
 except ContractError as e:ok=not accept;detail=str(e)
 if not ok:raise RuntimeError('Unexpected case result '+name)
 rows.append({'case':name,'expected_accept':accept,'passed':ok,'detail':detail})
case('latest_exact_three_wire_mapping',lambda:validate(c),True)
case('legacy_four_pin_one_to_one_target_rejected',lambda:validate(c,target=c['explicitly_incompatible_legacy']),False)
case('original_three_pin_same_logic_wrong_board_version_rejected',lambda:validate(c,target=c['historical_original_14x45']),False)
# Demonstrate why legacy 1:1 is electrically different, without approving any legacy harness.
old=check_locks(ROOT,c['explicitly_incompatible_legacy'])
if old.get('3')!='/CE_PERMISSION_EXTERNAL' or old.get('4')!='/GND':raise RuntimeError('Legacy evidence changed')
x=copy.deepcopy(c);x['wires'][2]['target']['pin']='2';case('ground_miswire_rejected',lambda:validate(x),False)
x=copy.deepcopy(c);x['wires'][0],x['wires'][1]=copy.deepcopy(x['wires'][1]),copy.deepcopy(x['wires'][1]);case('duplicate_wire_rejected',lambda:validate(x),False)
x=copy.deepcopy(c);x['mainboard']['files'][0]['sha256']='0'*64;case('changed_source_hash_rejected',lambda:validate(x),False)
x=copy.deepcopy(c);x['target']['pins']['3']='CE_PERMISSION_EXTERNAL';case('injected_ce_semantics_rejected',lambda:validate(x),False)
x=copy.deepcopy(c);x['wires']=x['wires'][:2];case('missing_ground_rejected',lambda:validate(x),False)
print(json.dumps({'mode':'optimized' if not __debug__ else 'normal','cases':rows,'legacy_native_J5':old,'NOFAB':True},indent=2))
