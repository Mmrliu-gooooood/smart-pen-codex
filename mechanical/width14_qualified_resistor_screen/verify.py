import json,math,subprocess,sys,hashlib
from pathlib import Path
import screen
R=Path(__file__).resolve().parent
c=json.loads((R/'contract_snapshot.json').read_text());d=json.loads((R/'results.json').read_text())
def req(x,m):
 if not x:raise RuntimeError(m)
req(json.loads(subprocess.check_output([sys.executable,str(R/'screen.py'),str(R/'contract_snapshot.json')]))==d,'Reproduction')
ps=screen.make_parts(c,12,{})
covered=set(c['scope_refs']);req(len(covered)==9,'Contract count')
for old,new in zip(screen.D['parts'],ps):
 req(new['height_total']==(.7 if old['ref'] in covered else old['height_total']),'Height leakage')
 if old['ref']!='J109':req(old['bounds']==new['bounds'],'Unexpected movement')
req(set(d['necessary_left_translations_at_minimum_Bdatum'])=={'C103','C203','C201','C205'},'Minimal set')
req(all(not r['optimized']['passes'] for r in d['rows']),'No move baseline')
req(all(r['optimized']['passes'] for r in d['refined_rows']),'Refinement')
def pairs(parts):
 out=set()
 for i,p in enumerate(parts):
  if p['dnp']:continue
  a,b,cc,d=p['bounds']
  for q in parts[i+1:]:
   if q['dnp'] or q['side']!=p['side']:continue
   aa,bb,c2,d2=q['bounds']
   if min(cc,c2)>max(a,aa)+1e-8 and min(d,d2)>max(b,bb)+1e-8:out.add(tuple(sorted((p['ref'],q['ref']))))
 return out
base=pairs(screen.make_parts(c,13,{}))
for row in d['refined_rows']:
 req(not pairs(screen.make_parts(c,12,row['moves']))-base,'New XY overlap')
for folder in ['width14_gate','width14_port_refinement']:
 prior=R.parent/folder
 for f in json.loads((prior/'manifest.json').read_text())['files']:
  req(hashlib.sha256((prior/f['path']).read_bytes()).hexdigest()==f['sha256'],'Prior freeze changed')
print('PASS: exact reproduction; only9height changes;4caps minimal under stated fixed transform;8 cases; no new same-side envelope overlaps; prior freezes unchanged. NOFAB.')
