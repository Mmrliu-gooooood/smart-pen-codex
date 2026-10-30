import json,subprocess,sys,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parent
def req(x,m):
 if not x:raise RuntimeError(m)
d=json.loads((R/'results.json').read_text());again=json.loads(subprocess.check_output([sys.executable,str(R/'check.py')]))
req(d==again,'Reproduction');req(d['count']==84 and d['old79_equal'],'Entity count')
req(len(d['new_wire_solder_envelopes'])==11,'Wire count');req(not d['local_collision_hits'] and not d['open_sweep_hits'],'Local collision')
req(all(p['connector_closed_overlap_mm3']>10 for p in d['rejected_straight_routes']),'Unsafe direct crossing regression')
req(all(w['radius']<7.9 for w in d['new_wire_solder_envelopes']),'Radial budget')
prior=R.parent/'rf_width14_mixed_final_screen'
for f in json.loads((prior/'manifest.json').read_text())['files']:req(hashlib.sha256((prior/f['path']).read_bytes()).hexdigest()==f['sha256'],'Prior freeze changed')
print('PASS:84native; unchanged79;11unreduced solder envelopes; local/open zero collision; same-height direct crossing rejected; priorfreeze. NO FULL HARNESS APPROVAL.')
