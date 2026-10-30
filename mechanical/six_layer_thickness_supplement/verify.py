from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parent;d=json.loads((R/'results.json').read_text())
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
lookup={(c['thickness'],c['position']):c for c in d['cases']}
a=lookup[(.8,'fixed_previous_2p820')];b=lookup[(.93,'fixed_previous_2p820')]
require(math.isclose(b['main_front_y']-a['main_front_y'],.13,abs_tol=1e-10),'Front face delta')
for key in ['main_back_y','back_part_lower_y','power_top_y','nominal_interboard_gap']:require(math.isclose(a[key],b[key],abs_tol=1e-10),'B datum unexpectedly changed: '+key)
require(math.isclose(b['two_sided_passive_envelope_thickness']-a['two_sided_passive_envelope_thickness'],.13,abs_tol=1e-10),'Thickness double-counted')
for c in d['cases']:
 for r in c['rows']:require(math.isclose(r['worst_interboard_remainder'],.1,abs_tol=1e-10),'Interboard residual changed')
require(not lookup[(.93,'reoptimized')]['rows'][1]['passes0p1_screen'],'18.5 must fail current worstcase residual screen')
require(lookup[(.93,'reoptimized')]['rows'][2]['passes0p1_screen'],'19 conditional screen')
require(lookup[(.93,'reoptimized')]['minimum_OD_for0p1_radial_residual']>lookup[(.8,'reoptimized')]['minimum_OD_for0p1_radial_residual'],'Thickness should worsen minimum diameter')
for sub in ['flex_power_revD_study','flex_power_tolerance_supplement']:
 base=R.parent/sub;m=json.loads((base/'manifest.json').read_text())
 for f in m['files']:require(hashlib.sha256((base/f['path']).read_bytes()).hexdigest()==f['sha256'],'Prior freeze changed: '+str(base/f['path']))
print('PASS: correct B-face datum, F-face+.13 once, two-sided height delta, unchanged spacing, OD threshold/negative control, prior34 hashes intact')

e=json.loads((R/'source_evidence.json').read_text())
require(math.isclose(e['finished_thickness_mm']+e['finished_thickness_tolerance_mm'],.93,abs_tol=1e-10),'Official candidate maximum changed')
print('PASS: observed candidate finished maximum0.93; mask inclusion remains unknown')
