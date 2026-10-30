#!/usr/bin/env python3
"""Validate recorded manufacturer candidate; does not solve impedance."""
import copy,json,pathlib
P=pathlib.Path(__file__).resolve().parent

def check(c):
    if c['status']!='RESEARCH_CANDIDATE_NOFAB' or c['manufacturing_approved'] is not False:
        raise ValueError('not a qualified manufacturing contract')
    if c['template']!='JLC06081H-2116' or c['dielectric_mm']!=[.1164,.13,.2028,.13,.1164]:
        raise ValueError('unobserved template / physical table')
    if c['copper_mm']!=[.035,.0152,.0152,.0152,.0152,.035]:
        raise ValueError('unobserved copper table')
    if len(c['layer_roles'])!=6 or c['finished_thickness_mm']!=.83 or c['finished_thickness_tolerance_mm']!=.1:
        raise ValueError('unobserved board envelope')
    if len(c['models'])!=2 or c['impedance_target_ohms']!=50:
        raise ValueError('model count or target mismatch')
    for m,typ,width in zip(c['models'],['Single Ended (Non coplanar)','Coplanar Single Ended'],[.1814,.1707]):
        if m['type']!=typ or m['width_mm']!=width or m['soldermask']!='included model' or m['signal_layer']!='L1' or m['bottom_reference']!='L2':
            raise ValueError('model / reference / width mismatch')
    if c['models'][1]['input_same_layer_ground_gap_mm']!=.2 or c['factory_standard_tolerance_percent']!=10:
        raise ValueError('gap or tolerance mismatch')
    return {'copper_dielectric_sum_mm':round(sum(c['copper_mm'])+sum(c['dielectric_mm']),7),
            'finished_max_mm':round(c['finished_thickness_mm']+c['finished_thickness_tolerance_mm'],7),
            'delta_vs_old_0p8_mm':round(c['finished_thickness_mm']+c['finished_thickness_tolerance_mm']-.8,7),
            'cpwg_center_gap_corridor_mm':round(.1707+2*.2,7),
            'impedance_independently_solved':False,'manufacturing_approved':False}

c=json.loads((P/'candidate_contract.json').read_text());result=check(c)
observed=(P/'jlc_coplanar_6L_08_observed.txt').read_text()
for token in ['0.1707','0.1999','0.2028','0.83±0.10mm']:
    if token not in observed: raise ValueError('missing observed UI result '+token)
mutations=[lambda q:q['dielectric_mm'].__setitem__(2,.2104),lambda q:q['models'][1].__setitem__('soldermask','none'),lambda q:q['models'][0].__setitem__('bottom_reference','L3'),lambda q:q.__setitem__('manufacturing_approved',True),lambda q:q.__setitem__('factory_standard_tolerance_percent',.5)]
for mutate in mutations:
    q=copy.deepcopy(c);mutate(q)
    try:check(q)
    except ValueError:pass
    else:raise RuntimeError('negative regression accepted')
result['negative_cases_rejected']=len(mutations)
print(json.dumps(result,indent=2))
