#!/usr/bin/env python3
"""Arithmetic only: no SPICE, no proven load or all-temperature GPIO guarantee."""
import json
rmin,rmax=9900,10100
out={
 'status':'PROPOSED_COMPONENTS_ARITHMETIC_ONLY_NO_NATIVE_CHANGE_NOFAB_NOPOWER',
 'input_open_II5uA_Rmax_V':5e-6*rmax,
 'engineering_0p2V_input_total_leak_budget_uA':.2/rmax*1e6,
 'engineering_0p2V_input_remaining_after_II_uA':.2/rmax*1e6-5,
 'output_low_R203_and_5OE_uA':3.6/rmin*1e6+5,
 'output_high_100uA_budget_remaining_after_5OE_uA':95,
 'IBIS_LVC_slow_ramp_ns_per_V_NOT_circuit_rise':.605/1.85,
 'IBIS_LVC_slow_ramp_ns_per_V_NOT_circuit_fall':.496/1.79,
 'IBIS_5OE_Ccomp_envelope_pF_NOT_guaranteed_max':5*2.13619,
 'IBIS_5OE_package_plus_Ccomp_envelope_pF_NOT_guaranteed_max':5*2.13619+4*.24+.56494,
 'datasheet_5OE_Ci_typical_pF_NOT_maximum':5*4.5,
 'provisional_VOH_loaded_input_screen_NOT_GPIO_guarantee':[
 {'VDD':v,'assumed_MCU_VOH':.8*v,'gate_V':(.8*v/1010-5e-6)/(1/1010+1/9900)} for v in [3.,3.3,3.6]
 ]
}
print(json.dumps(out,indent=2,sort_keys=True))
