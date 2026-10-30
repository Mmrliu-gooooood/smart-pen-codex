import json,math
r_nom=10000.0;r_tol=0.01;r_max=r_nom*(1+r_tol)
coefficient=math.log(0.7/0.3)
rows=[]
for f,tr in [(100000,1e-6),(400000,300e-9)]:
 rows.append({'frequency_hz':f,'rise_limit_ns':tr*1e9,'capacitance_ceiling_pF_initial_tolerance_only':tr/coefficient/r_max*1e12})
sensitivity=[{'total_C_pF':c,'rise_ns_at_10k_plus_1pct':coefficient*r_max*c*1e-3} for c in [20,35,50,100,117,150]]
if not rows[0]['capacitance_ceiling_pF_initial_tolerance_only']>rows[1]['capacitance_ceiling_pF_initial_tolerance_only']>0:raise RuntimeError('invalid budget')
print(json.dumps({'status':'ANALYTICAL_BUDGET_NOT_MEASURED_BUS_QUALIFICATION','formula':'tr(30%-70%)=ln(0.7/0.3)*Rp*Cb','r_nom_ohm':r_nom,'initial_tolerance':r_tol,'r_max_ohm_excludes_TCR_aging':r_max,'coefficient':coefficient,'budgets':rows,'sensitivity':sensitivity,'proposed_initial_test_hz':100000,'actual_bus_C_pF':None,'temperature_aging_resistor_margin':None},indent=2))
