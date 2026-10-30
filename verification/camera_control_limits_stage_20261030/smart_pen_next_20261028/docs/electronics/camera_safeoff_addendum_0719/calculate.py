from pathlib import Path
import json,math,hashlib,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;R=D.parents[2];N=R/'hardware/camera_isolation_control_native_0628';P=N/'native/mainboard_revD.kicad_pcb'
def req(c,m):
 if not c:raise RuntimeError(m)
req(hashlib.sha256(P.read_bytes()).hexdigest()=='63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c','frozenPCB')
req(hashlib.sha256((N/'manifest.json').read_bytes()).hexdigest()=='be6b0eabfd477ab6c3a932204f4b9f05b9e6cab9f8b7c5a41f79514e745f06c3','frozenmanifest')
r=E.parse(N/'checks/candidate/netlist.xml');cs={c.get('ref'):c for c in r.findall('.//components/comp')};expected={'Q201':'PMV30UN2','R107':'100k 1%','R201':'1k 1%','R202':'100k 1%','R203':'10k 1%'}
for k,v in expected.items():req(cs[k].findtext('value')==v,k)
def gate(v,ru=45000,r107=100000,r201=1000,r202=100000):
 rd=1/(1/r107+1/(r201+r202));pad=v*rd/(ru+rd);return {'supply_V':v,'assumed_internal_pullup_ohms':ru,'pad_V':pad,'gate_V':pad*r202/(r201+r202)}
rows=[gate(v)for v in[3.,3.3,3.6]];req(abs(rows[1]['gate_V']-1.7236876469051972)<1e-12,'divider')
rc=[]
for v in[3.,3.3,3.6]:
 C=22.5e-12;t=10000*C*math.log((v-.8)/(v-2));rc.append({'supply_V':v,'assumed_C_F':C,'R_ohms':10000,'time_0p8_to_2V_ns':t*1e9,'average_ns_per_V':t/1.2*1e9,'Rmax_ohms_at_10ns_per_V_with_this_typical_C_only':10e-9*1.2/(C*math.log((v-.8)/(v-2)))})
req(all(x['average_ns_per_V']>10 for x in rc),'modelredflag')
req(gate(3.3,ru=1e30)['gate_V']<1e-20,'no_pullup_limit')
print(json.dumps({'status':'SOURCE_ONLY_RESEARCH_NO_RELEASE','source_values':expected,'GPIO42_reset_pullup_claim':'NOT_SUPPORTED: documented after-reset RST=1 IE only; MTCK special pull-up must not be generalized','hypothetical_pullup_divider':rows,'pullup_value_is_typical_not_worst_case':True,'RC_typical_screen_not_max_or_measurement':rc,'OE_control_leakage_budget':{'five_OE_max_uA_at_125C_valid_II_conditions':5,'five_OE_max_uA_at_85C_valid_II_conditions':2.5,'R203_max_ohms':10100,'total_sink_budget_uA_at_AON3V_OE2V':1/10100*1e6,'remaining_budget_uA_after_five_controls_125C':1/10100*1e6-5,'not_proven':['Q201 hot leakage','board contamination','II bounds in partial-power state','input current away from stated VI test endpoints']},'Q201':{'actual_value':'PMV30UN2','Vth_min_max_V_at_25C_250uA':[.4,.9],'Rds_max_ohms_at_25C_Vgs1p5V_Id0p1A':.1,'IDSS_max_A_at25C_Vds20V_Vgs0':1e-6,'IGSS_absmax_A_at25C_Vgs12V':1e-7,'Coss_typ_F_at10V_only':70e-12,'not_proven':['Vth off-current criterion','low-gate-drive hot Rds max','hot IDSS','actual3V Coss and route parasitics']},'frozen_native_unmodified':True,'all_jumpers_remain_OPEN':True,'provider_still_NULL':True},indent=2))
