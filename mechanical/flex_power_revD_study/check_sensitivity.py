import json,math
from pathlib import Path
R=Path(__file__).resolve().parent;d=json.loads((R/'inputs/bias4_board_extract.json').read_text())['mainboard'];rows=[]
for passive in [1.,1.3,1.6]:
 worst=(7.8-math.hypot(7,2.7),'Power')
 for p in d['parts']:
  if p['dnp']:continue
  h=(passive if p['height_basis'].startswith('ASSUMED') else p['height'])+.15;a,b,c,dd=p['bounds'];ys=[2.9-h,2.9] if p['back'] else [3.7,3.7+h];margin=7.8-max(math.hypot(x,y) for x in [a-6,c-6] for y in ys)
  if margin<worst[0]:worst=margin,p['ref']
 rows.append(dict(assumed_passive_height=passive,min_radial_margin=worst[0],limiting_item=worst[1],worstcase_after_hypothetical_wall_plus0p1_and_radial_assembly_shift0p2=worst[0]-.3,backpart_to_power_gap=2.9-(passive+.15)-1.45))
(R/'tolerance_sensitivity.json').write_text(json.dumps({'qualification':'Sensitivity inputs only, not supplier tolerances or completed tolerance chain','rows':rows},indent=2))
best=None
for i in range(2001):
 y=-10+i*.01;r=max(math.hypot(7,y),math.hypot(7,y+4.15),math.hypot(6,y+4.45),math.hypot(6,y+6.6))
 if best is None or r<best['r']:best=dict(y=y,r=r,OD=2*r+2.4,margin_ID15p6=7.8-r)
p=R/'dimensional_limits.json';d=json.loads(p.read_text());d['stacked_board_ideal_screen']={'power_width':14,'power_thickness_budget':4.15,'main_width':12,'main_thickness_assumed':2.15,'gap':.3,'best':best,'status':'Ideal constant rectangles only. Actual latest mainboard has back parts; 2.15 thickness invalid as whole-board max at overlapping back parts. Actual-component CAD supersedes this screen;16parts remain missing.'};p.write_text(json.dumps(d,indent=2));print('Sensitivity and explicitly non-authoritative ideal screen saved')
