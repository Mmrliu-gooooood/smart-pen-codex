from pathlib import Path
import json
D=Path(__file__).resolve().parent
# Warning entries are violations too. Never filter by severity.
def check(x):
 if len(x['violations'])!=0 or len(x['unconnected_items'])!=19 or len(x['schematic_parity'])!=0:raise RuntimeError('DRC complete gate rejected')
x=json.loads((D/'native_drc.json').read_text());check(x)
fixtures=[]
for key in ['violations','schematic_parity','unconnected_items']:
 q=json.loads(json.dumps(x));q[key].append({'severity':'warning','description':'explicit negative fixture'})
 try:check(q)
 except RuntimeError:fixtures.append({'case':key,'rejected':True})
 else:raise RuntimeError('negative not rejected')
old=json.loads((D/'warning_predecessor_drc.json').read_text())
try:check(old)
except RuntimeError:fixtures.append({'case':'actual_4ab628_two_warnings','rejected':True})
else:raise RuntimeError('old warnings silently accepted')
(D/'strict_drc_gate.json').write_text(json.dumps({'counts':{'all_violations_including_warnings':0,'unconnected_items':19,'schematic_parity':0},'negative_checks':fixtures},indent=2))
