import json,math
from pathlib import Path
R=Path(__file__).resolve().parent;D=json.loads((R/'input.json').read_text())
# Fixed global transform X=pcb_x-shift, Z=127-pcb_y, B-side substrate datum Y=my.
def evaluate(my,shift,jx,left):
 candidates=[];py=my-1.45-.3-4.15
 candidates.extend((math.hypot(7,y),'power') for y in [py,py+4.15])
 # Existing actualoutline x0..14 at somez; optionalleftx-1occursy1..7.
 for x in ([0,14,-1] if left else [0,14]):
  for y in [my,my+.93]:candidates.append((math.hypot(x-shift,y),'outline_left_addition' if x==-1 else 'outline'))
 for p in D['parts']:
  if p['dnp']:continue
  a,b,c,d=p['bounds']
  if p['ref']=='J109':a,c=jx-.7,jx+.7
  ys=[my-p['height_total'],my] if p['side']=='B' else [my+.93,my+.93+p['height_total']]
  candidates.extend((math.hypot(x-shift,y),p['ref']) for x in [a,c] for y in ys)
 rad,item=max(candidates)
 # Fullpowerrectangleoverlapz82..127; allbackpassivebound1.45=>.3gap.
 return dict(main_B_y=my,main_F_y=my+.93,power_bottom_y=py,power_top_y=py+4.15,radius=rad,limiting=item,nominal_radial_clearance_OD19=8.3-rad,worst_radial_clearance_OD19=8.3-.3-rad,worst_interboard_clearance=.1,minimum_OD_no_radial_interference=2*(rad+1.5),minimum_OD_for0p1_residual=2*(rad+1.6),passes_19_0p1_screen=rad<=7.9+1e-10)
def opt(shift,jx,left):
 best=None
 for i in range(5001):
  r=evaluate(i*.001,shift,jx,left)
  if best is None or r['radius']<best['radius']:best=r
 return best
rows=[]
for left in [False,True]:
 for shift in [6.,6.5,7.]:
  for jx in [13.,12.5]:
   rows.append(dict(left_extension=left,global_X_offset=shift,J109_x=jx,fixed_prior_Bdatum=evaluate(2.74,shift,jx,left),optimized=opt(shift,jx,left)))
# Diagnostic allowableJ109inwardposition: allothergeometrysame; NOT electricallyapprovedmovement.
solutions=[]
for shift in [6.,6.5,7.]:
 for jx in [12.,11.5,11.,10.5]:solutions.append(dict(global_X_offset=shift,J109_x=jx,left_extension=False,optimized=opt(shift,jx,False)))
result={'status':'NOFAB mechanical gate only; no electricalroutingapproval','source_sha256':D['sha256'],'assumptions':{'thickness_max':.93,'wall_nominal':1.2,'wall_worst':1.3,'radial_assembly':.2,'back_body_plus_solder':1.45,'interboard_nominal_gap':.3,'interboard_relative_loss':.2,'power_total_thickness':4.15,'J109_wire_plus_solder_fromFface':2.,'OD_tolerance':'unspecified','screen_residual':.1},'rows':rows,'diagnostic_inward_pad_positions':solutions}
(R/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
