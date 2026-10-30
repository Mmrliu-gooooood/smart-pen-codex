from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parent;d=json.loads((R/'tolerance_sweep.json').read_text());cases={c['case']:c for c in d['cases']}
def require(c,m):
 if not c:raise RuntimeError(m)
for c in cases.values():
 rows=c['rows'];require([r['OD'] for r in rows]==[18.,18.5,19.],'OD order')
 for a,b in zip(rows,rows[1:]):require(math.isclose(b['worst_radial_clearance']-a['worst_radial_clearance'],.25,abs_tol=1e-10),'Diameter gain must be exactly0.25radial')
 require(all(math.isclose(r['worst_interboard_clearance'],c['nominal_interboard_gap']-.2,abs_tol=1e-10) for r in rows),'Spacing budget')
require(not any(r['passes_stated_screen'] for r in cases['existing_213_height1p3']['rows']),'Wider OD must not hide interboard overlap')
require(cases['respaced_0p1_residual_screen']['rows'][1]['passes_stated_screen'],'18.5 conditional screen')
require(all(r['passes_0p1_residual'] for r in d['axial_separation']['rows']),'Axial screen')
S=R.parent/'flex_power_revD_study';m=json.loads((S/'manifest.json').read_text())
for f in m['files']:require(hashlib.sha256((S/f['path']).read_bytes()).hexdigest()==f['sha256'],'Original frozen file changed: '+f['path'])
print('PASS: diameter/spacing arithmetic, negative-control overlap, axial cases, and29 frozen source hashes')
