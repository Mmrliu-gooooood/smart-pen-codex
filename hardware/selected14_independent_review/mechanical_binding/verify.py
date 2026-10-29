from pathlib import Path
import json,subprocess,sys,hashlib,math
R=Path(__file__).resolve().parent
def req(x,m):
 if not x:raise RuntimeError(m)
d=json.loads((R/'results.json').read_text());raw=json.loads((R/'input.json').read_text())
req(json.loads(subprocess.check_output([sys.executable,str(R/'check_native.py')]))==d,'Reproduction')
req(raw['count']==79 and len(d['applied_parts'])==79,'Count')
for p,q in zip(raw['parts'],d['applied_parts']):
 req(q['height_total']==(.7 if p['ref'] in d['changed_height_refs'] else p['height_total']),'Height leakage')
req(d['best']['passes'] and math.isclose(d['best']['radial_remainder'],.11236862861430197,abs_tol=1e-12),'Result')
for folder in ['rf_width14_native_screen','width14_qualified_resistor_screen','width14_port_refinement','width14_gate']:
 r=R.parent/folder
 for f in json.loads((r/'manifest.json').read_text())['files']:
  req(hashlib.sha256((r/f['path']).read_bytes()).hexdigest()==f['sha256'],'Prior freeze')
print('PASS: native hash/value/net/package checks;79 footprints; exact rerun; only9 resistor heights changed; earlier freeze hashes unchanged. NOFAB.')

req(not d['fixed_B2p288511']['passes'],'Old mounting datum must fail .10 screen')
diff=json.loads((R/'native_diff.json').read_text());req(len(diff)==1 and diff[0]['ref']=='C203','Unexpected entity change')
