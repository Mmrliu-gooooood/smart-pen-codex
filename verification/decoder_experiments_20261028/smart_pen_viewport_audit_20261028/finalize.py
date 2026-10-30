from pathlib import Path
p=Path(__file__).resolve().parent
# Reuse renderer and image-only filter definitions without rerunning sweep.
namespace={'__file__':str(p/'boundary_diagnostic.py')};exec((p/'boundary_diagnostic.py').read_text().split('for old in original:')[0],namespace)
import json,hashlib
rows=json.loads((p/'boundary_results.json').read_text()); selected=[]
for fov in (5,6,7):
 for size in (200,96,80,64):
  r=next(r for r in rows if r['fov_mm']==fov and r['size']==size);full=namespace['render'](fov,r['ox_cells'],r['oy_cells']);start=(200-size)//2;im,_=namespace['edge_filter'](full[start:start+size,start:start+size]);assert hashlib.sha256(im.tobytes()).hexdigest()==r['image_sha256'];name=f'edge_filtered_fov{fov}_roi{size}_phase0.pgm';(p/name).write_bytes(f'P5\n{size} {size}\n255\n'.encode()+im.tobytes());selected.append(dict(r,fixture=name))
(p/'boundary_fixture_oracles.json').write_text(json.dumps(selected,indent=2))
summary=json.loads((p/'boundary_summary.json').read_text())
with (p/'REPORT.md').open('a') as f:
 f.write('\n## Diagnostic edge-component removal results (NOT production)\n\n36 views per cell. Cold and sequential-prior status counts are identical in this finite sweep. Sequential prior comes only from previous actual image decoding within each FOV/ROI group; failures clear it.\n\n| FOV | 200 px | 96 px | 80 px | 64 px |\n|---|---:|---:|---:|---:|\n')
 for fov in (5,6,7):
  f.write(f'| {fov} mm | '+' | '.join(str(next(r for r in summary if r['fov_mm']==fov and r['roi']==size)['cold'].get('0',0))+'/36' for size in (200,96,80,64))+' |\n')
 from collections import Counter
 counts=Counter();warm=0
 for r in summary:counts.update({int(k):v for k,v in r['cold'].items()});warm+=r['used_warm']
 f.write(f'\nAcross 432 filtered cold calls: **{counts[0]} OK ({counts[0]/432:.2%}), {counts[-2]} detection rejects ({counts[-2]/432:.2%}), {counts[-3]} no-grid ({counts[-3]/432:.2%}), {counts[-4]} ambiguity**. False successes: **0/{counts[0]}**. A separate 432-call sequential-prior pass has the same status totals, **{warm} actual warm-path successes**, and zero false successes. No no-grid case was converted into a wrong-coordinate OK.\n')
 f.write('\nAfter removing edge components, full 200px images still contain **256–281 / 364–400 / 506–533** interior accepted-size components at 5/6/7 mm. All 108 full-field cases still fail detection, isolating the >128-dot incompatibility independently of border clipping. At 5 mm, 64px contains only 22–27 interior dots (below required 36); at 6 mm it contains 33–38 and remains phase-sensitive. At 7 mm, 96px contains 101–121 dots, yet 6/36 clean crops still have no fit, so removal plus cap compliance is not sufficient. Source quantization/residual/model gates remain; this audit does not assign an unproven single cause for those six cases.\n\n`boundary_summary.json` and `boundary_results.json` contain the complete results; `boundary_fixture_oracles.json` names representative filtered PGM files with status/coordinate oracle. **These filtered success rates are a diagnostic upper opportunity under ideal synthetic optics, not production coverage claims.**\n')
print(counts, 'warm=',warm)
