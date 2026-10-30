import json,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parent;d=json.loads((R/'results.json').read_text());inp=json.loads((R/'input.json').read_text());o=json.loads((R/'options.json').read_text())
def req(ok,msg):
 if not ok:raise RuntimeError(msg)
req(hashlib.sha256(Path(inp['source']).read_bytes()).hexdigest()==inp['sha256'],'Native prelayout changed')
req(inp['sha256']=='f27cd35dcaf51fd33078b60a7029f6f63fba9c58f1d2791488e8a1721330080c','Wrong native revision')
req(inp['count']==79,'Wrong footprint count')
j=next(p for p in inp['parts'] if p['ref']=='J109');req(j['bounds']==[12.3,18.3,13.7,24.9] and j['height_total']==2.,'Native J109 bounds/height assumption changed')
for row in d['rows']:
 for key in ['fixed_prior_Bdatum','optimized']:
  r=row[key];req(math.isclose(r['main_F_y']-r['main_B_y'],.93,abs_tol=1e-10),'Bad B/Fdatum')
  req(math.isclose(r['power_top_y'],r['main_B_y']-1.45-.3,abs_tol=1e-10),'Back clearance not preserved')
  req(not r['passes_19_0p1_screen'],'Unexpected19passing branch: re-review')
# Identity of globaltransform cannot vary withsourceY; eachcase stores oneconstantshift.
req({r['global_X_offset'] for r in d['rows']}=={6.,6.5,7.},'Missing requested transforms')
req(any(r['left_extension'] and r['X_offset']==6.5 and r['passes0p1_screen'] for r in o['axial_power_options']),'Expected conditional axial option absent')
req(all(not r['passes0p1_screen'] for r in o['axial_power_options'] if r['left_extension'] and r['X_offset']==7.),'Left extension negative control')
print('PASS: native79fp identity, J109 height/bounds, single fixed transforms, B-face datum/.93 once, preserved gap, all stacked failures and conditional axial comparisons')
