from pathlib import Path
import json,collections
D=Path(__file__).resolve().parent
files=[D.parent/'imu_i2c_completed_candidate/preflight.native_drc.json',D/'preflight.native_drc.json'];xs=[json.loads(f.read_text())for f in files]
def mult(x):
 rows=[]
 for v in x['violations']:
  z=dict(v);z['items']=sorted(z.get('items',[]),key=lambda a:json.dumps(a,sort_keys=True));rows.append(json.dumps(z,sort_keys=True))
 return collections.Counter(rows)
a,b=map(mult,xs)
if a!=b:raise RuntimeError('Native full violation multiset changed')
counts=[[len(x[k])for k in['violations','unconnected_items','schematic_parity']]for x in xs]
if counts!=[[17,33,0],[17,26,0]]:raise RuntimeError('Unexpected full DRC counts')
print(json.dumps({'full_counts_before_after':counts,'complete_violation_multiset_unchanged':True,'retained_findings':sum(a.values()),'added_findings':[],'airwire_change_evidence':'Only J202 seven GND pads merge into core, independently checked by finite copper graph; airwire representatives are not electrical graph evidence'},indent=2))
