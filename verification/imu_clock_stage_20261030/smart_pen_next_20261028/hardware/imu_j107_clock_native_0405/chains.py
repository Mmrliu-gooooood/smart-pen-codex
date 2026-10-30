from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));import pcbnew as p
from finite_copper import build,components
board=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));nodes=build(board);c={n:components(v)for n,v in nodes.items()};out=[]
def req(c,m):
 if not c:raise RuntimeError(m)
nets=json.loads((R/'hardware/complete_net_restore_independent_review_2020/restoration.json').read_text())['restored_nets']
for n in nets:req(len(c[n])==1,'19net '+n);out.append({'net':n,'pads':c[n][0]})
rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows'];chains=[]
for row in rows:
 a=row['translator_pin'];b='J202.'+row['J202_pin'];n=row['net'];req(any(a in group and b in group for group in c[n]),'12chain '+n);chains.append({'net':n,'start':a,'end':b})
print(json.dumps({'nineteen_complete_nets':out,'twelve_DVP_chains':chains,'clock_extra':c['SENS_EXTCLK'],'not_timing_or_strobe_function_qualification':True},indent=2))
