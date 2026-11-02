"""Read-only native binding and intended-conductor topology checks. No PCB saves."""
import argparse, copy, hashlib, json, os
from pathlib import Path
os.environ['HOME']='/tmp/power_return_tree_home'
Path(os.environ['HOME']).mkdir(exist_ok=True)
os.environ['XDG_CONFIG_HOME']='/tmp/power_return_tree_home/.config'
import pcbnew
HERE=Path(__file__).resolve().parent
EXPECTED={'main':'617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5','power':'94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc'}
def require(condition, message):
    if not condition: raise RuntimeError(message)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def native(p, refs):
    board=pcbnew.LoadBoard(str(p))
    return {f.GetReference():{'value':f.GetValue(),'pads':{pad.GetNumber():pad.GetNetname() for pad in f.Pads()}} for f in board.GetFootprints() if f.GetReference() in refs}
def components(nodes, edges):
    pending=set(nodes); result=[]
    while pending:
        todo=[min(pending)]; seen=set()
        while todo:
            v=todo.pop()
            if v in seen: continue
            seen.add(v)
            for a,b in edges:
                if a==v and b not in seen: todo.append(b)
                if b==v and a not in seen: todo.append(a)
        result.append(sorted(seen));pending-=seen
    return sorted(result)
def is_tree(nodes,edges):
    # Edge count includes duplicate physical conductors: these create parallel paths.
    return len(edges)==len(nodes)-1 and len(components(nodes,edges))==1 and all(a!=b and a in nodes and b in nodes for a,b in edges)
EXPECTED_ENDPOINT_CONTRACT = {'status': 'DESIGN_CANDIDATE_ONLY_NOFAB_NO_POWER', 'ground_edges': [{'id': 'G_TP', 'nodes': ['T', 'P'], 'from': 'tail TP104 (not re-read in this work)', 'to': 'power J2.2', 'role': 'Complete USB input return; current and joint qualification pending'}, {'id': 'G_PM', 'nodes': ['P', 'M'], 'from': 'power J3.2', 'to': 'main J106.3 logical existing endpoint', 'role': 'Complete mainboard load/inrush return; physical replacement site pending'}], 'externally_unwired_ground_pads': ['main J109.3', 'main J107.3', 'power J5.3'], 'externally_unwired_non_ground_pads': ['main J106.1'], 'other_intended_wires': [['tail VBUS', 'power J2.1', 'VBUS_5V'], ['tail USB_DP', 'main J109.1', 'USB_DP'], ['tail USB_DM', 'main J109.2', 'USB_DM'], ['power J3.1', 'main J106.2 logical existing endpoint', '3V3_AON'], ['main J107.1', 'power J5.1', 'USB_EN1'], ['main J107.2', 'power J5.2', 'USB_EN2']], 'pack_and_thermal': {'pack_positive': 'power J4.1; protected pack only', 'pack_negative': 'power J4.2; protected output negative only', 'ntc1': 'power J1.1/J1.2; separate thermistor, configuration not inferred from blue lead', 'ntc2': 'power J104.1/J104.2; separate thermistor; not mainboard J104', 'ban': 'No bare CELL- connection, no shared third-wire interpretation without manufacturer schematic'}}

def validate_contract(c):
    for field, expected in EXPECTED_ENDPOINT_CONTRACT.items():
        require(c.get(field)==expected, "Endpoint/role contract mismatch: "+field)
    require(c['nodes']==['T','P','M'],'Unexpected network boundary')
    require([e['id'] for e in c['ground_edges']]==['G_TP','G_PM'],'Missing/extra/reordered physical ground edge')
    edges=[e['nodes'] for e in c['ground_edges']]
    require(edges==[['T','P'],['P','M']],'Changed physical ground topology')
    require(is_tree(c['nodes'],edges),'Not a ground tree')
    require(set(c['externally_unwired_ground_pads'])=={'main J109.3','main J107.3','power J5.3'},'Unwired-ground obligations changed')
    return edges
args=argparse.ArgumentParser(description='Read-only candidate harness contract bound to the exact current main and power native files.')
args.add_argument('--main',required=True,type=Path,help='Path to exact 617a99 mainboard native .kicad_pcb')
args.add_argument('--power',required=True,type=Path,help='Path to exact 94ced2 power-board native .kicad_pcb')
args.add_argument('--output',required=True,type=Path,help='Result JSON path; caller chooses a writable output location')
opt=args.parse_args();MAIN=opt.main.resolve();POWER=opt.power.resolve()
c=json.loads((HERE/'contract.json').read_text());edges=validate_contract(c)
for k,p in [('main',MAIN),('power',POWER)]:require(digest(p)==EXPECTED[k],k+' native hash mismatch')
current_board=pcbnew.LoadBoard(str(MAIN))
current_j107=next(f for f in current_board.GetFootprints()if f.GetReference()=='J107')
current_lands={p.GetNumber():{'net':p.GetNetname(),'xy_mm':[p.GetPosition().x/1e6,p.GetPosition().y/1e6],'angle_deg':p.GetOrientationDegrees(),'size_mm':[p.GetSize().x/1e6,p.GetSize().y/1e6],'mask_margin_mm':p.GetLocalSolderMaskMargin()/1e6}for p in current_j107.Pads()}
expected_lands={'1':{'net':'USB_EN1','xy_mm':[5.22,34.31],'angle_deg':270.0,'size_mm':[1.5,2.0],'mask_margin_mm':.04},'2':{'net':'USB_EN2','xy_mm':[7.2,25.38],'angle_deg':270.0,'size_mm':[1.5,2.0],'mask_margin_mm':.04},'3':{'net':'GND','xy_mm':[6.4,31.66],'angle_deg':180.0,'size_mm':[1.5,2.0],'mask_margin_mm':.04}}
require(current_lands==expected_lands,'Current non-linear J107 land binding mismatch')
require(current_j107.GetLayerName()=='B.Cu','Current J107 side mismatch')
n={'main':native(MAIN,['J106','J107','J109']), 'power':native(POWER,['J1','J2','J3','J4','J5','J104','JP1'])}
checks={
 'main':{'J106':{'1':'VBUS_5V','2':'3V3_AON','3':'GND'},'J107':{'1':'USB_EN1','2':'USB_EN2','3':'GND'},'J109':{'1':'USB_DP','2':'USB_DM','3':'GND'}},
 'power':{'J1':{'1':'/core/PACK_NTC','2':'GND'},'J2':{'1':'VBUS_5V','2':'GND'},'J3':{'1':'/core/3V3_AON','2':'GND'},'J4':{'1':'/core/PACK_PLUS_PROTECTED','2':'GND'},'J5':{'1':'/core/USB_EN1','2':'/core/USB_EN2','3':'GND'},'J104':{'1':'/thermal/NTC_NODE','2':'GND'}}}
for board,refs in checks.items():
 for ref,pads in refs.items():require(n[board][ref]['pads']==pads,board+' '+ref+' pad mismatch')
require(n['power']['JP1']['value']=='OPEN / DO NOT BRIDGE','JP1 open contract mismatch')
faults=[]
for i,e in enumerate(c['ground_edges']):
 remaining=edges[:i]+edges[i+1:]; cc=components(c['nodes'],remaining)
 require(len(cc)==2,'Removing a tree edge must split intended ground network')
 faults.append({'opened_edge':e['id'],'components':cc,'intended_ground_alternate_path':False,'signal_clamp_or_external_return_hazard':'NOT MODELLED; remains a release blocker'})
negative={}
for name,ee in [('extra_tail_main',edges+[['T','M']]),('extra_mode_ground',edges+[['P','M']]),('missing_tp',edges[1:]),('missing_pm',edges[:1]),('self_loop',edges+[['M','M']])]:
 require(not is_tree(c['nodes'],ee),'Negative topology accepted: '+name);negative[name]='REJECTED'
# Deliberately corrupt each physically important contract category, then call
# the SAME validator used for the live contract, under normal Python and -O.
mutations = []
def mutation(name, change):
    altered=copy.deepcopy(c);change(altered);mutations.append((name,altered))
mutation('ground_to_positive_swap',lambda x:x['ground_edges'][1].__setitem__('to','main J106.2 logical existing endpoint'))
mutation('ground_source_wrong_pad',lambda x:x['ground_edges'][1].__setitem__('from','power J3.1'))
mutation('positive_to_ground_swap',lambda x:x['other_intended_wires'][3].__setitem__(1,'main J106.3 logical existing endpoint'))
mutation('en1_en2_destination_swap',lambda x:x['other_intended_wires'][4].__setitem__(1,'power J5.2'))
mutation('usb_dp_dm_destination_swap',lambda x:x['other_intended_wires'][1].__setitem__(1,'main J109.2'))
mutation('wrong_wire_role',lambda x:x['other_intended_wires'][1].__setitem__(2,'GND'))
mutation('missing_signal_wire',lambda x:x['other_intended_wires'].pop())
mutation('extra_signal_wire',lambda x:x['other_intended_wires'].append(['main J109.3','power J5.3','GND']))
mutation('wrong_thermal_board',lambda x:x['pack_and_thermal'].__setitem__('ntc2','main J104.1/J104.2'))
mutation('bare_cell_negative',lambda x:x['pack_and_thermal'].__setitem__('pack_negative','bare CELL-'))
mutation('unwired_vbus_omitted',lambda x:x['externally_unwired_non_ground_pads'].clear())
mutation('extra_unwired_positive',lambda x:x['externally_unwired_non_ground_pads'].append('main J106.2'))
mutation('unwired_ground_omitted',lambda x:x['externally_unwired_ground_pads'].pop())
mutation('extra_ground_edge',lambda x:x['ground_edges'].append({'id':'G_TM','nodes':['T','M'],'from':'tail TP104','to':'main J109.3','role':'signal only'}))
mutation('changed_power_role',lambda x:x['ground_edges'][1].__setitem__('role','signal only'))
mutation('removed_no_power_status',lambda x:x.__setitem__('status','READY'))
contract_negatives={}
for name, altered in mutations:
    rejected=False
    try:validate_contract(altered)
    except RuntimeError:rejected=True
    require(rejected,'Corrupted endpoint contract accepted: '+name)
    contract_negatives[name]='REJECTED_BY_LIVE_VALIDATOR'
# Symbolic KCL: positive I_usb returns P->T, positive I_main returns M->P.
# A battery-only transfer at P leaves G_TP=0 in this explicitly reduced model.
examples=[]
for name,iu,im in [('usb_only_normalized',1,1),('charging_and_main_normalized',2,1),('battery_only_normalized',0,1)]:
 gtp=iu;gpm=im
 node_injections={'T':-iu,'P':iu-im,'M':im}
 residual={'T':node_injections['T']+gtp,'P':node_injections['P']-gtp+gpm,'M':node_injections['M']-gpm}
 require(all(abs(x)<1e-12 for x in residual.values()),'KCL failure')
 examples.append({'name':name,'arbitrary_units_not_amperes':True,'injections':node_injections,'P_to_T':gtp,'M_to_P':gpm,'residual':residual})
for k,p in [('main',MAIN),('power',POWER)]:require(digest(p)==EXPECTED[k],'Native modified during inspection')
r={'status':'PASS_READ_ONLY_CONTRACT_NOT_HARDWARE','source_hashes':EXPECTED,'contract_sha256':digest(HERE/'contract.json'),'native':n,'current_J107_lands':current_lands,'physical_harness_adopted':False,'ground_cycle_rank':len(edges)-len(c['nodes'])+1,'single_open':faults,'negative_tests':negative,'endpoint_negative_tests':contract_negatives,'normalized_kcl':examples,'limits':c['gates']}
opt.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
print('PASS: exact 2 native hashes, 3-node/2-edge tree, 2 cut sets, 5 topology negatives, 16 endpoint/role mutations, 3 normalized KCL examples. NOFAB / NO POWER.')
