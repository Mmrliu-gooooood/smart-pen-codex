import json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'flex_power_revD_study/inputs/href3_board_extract.json';D=json.loads(S.read_text())['mainboard']
# Datum: mainboard bottom/B-side substrate face is Y; thickness grows toward +Y only.
# Front component base follows Y+thickness; back component base is unchanged.
def main_radius(y,t):
 cand=[(math.hypot(6,y),'board_back'),(math.hypot(6,y+t),'board_front')]
 for p in D['parts']:
  if p['dnp']:continue
  h=(1.3 if p['height_basis'].startswith('ASSUMED') else p['height'])+.15;a,b,c,d=p['bounds'];ys=[y-h,y] if p['back'] else [y+t,y+t+h]
  cand.extend((math.hypot(x,yy),p['ref']) for x in [a-6,c-6] for yy in ys)
 return max(cand)
def geometry(y,t):
 py=y-1.45-.3-4.15;pr=max(math.hypot(7,py),math.hypot(7,py+4.15));mr,item=main_radius(y,t)
 return dict(main_back_y=y,main_front_y=y+t,power_bottom_y=py,power_top_y=py+4.15,radius=max(pr,mr),limiting='power' if pr>=mr else item,main_radius=mr,back_part_lower_y=y-1.45,nominal_interboard_gap=.3,front_component_max_y=y+t+1.45,two_sided_passive_envelope_thickness=t+2*1.45)
def optimize(t):
 best=None
 for i in range(10001):
  g=geometry(-2+i*.001,t)
  if best is None or g['radius']<best['radius']:best=g
 return best
cases=[]
for thickness in [.8,.83,.93]:
 for mode in ['fixed_previous_2p820','reoptimized']:
  g=geometry(2.82,thickness) if mode.startswith('fixed') else optimize(thickness)
  g.update(thickness=thickness,position=mode,minimum_OD_for0p1_radial_residual=2*(g['radius']+1.3+.2+.1),rows=[])
  for od in [18,18.5,19]:
   rem=od/2-1.3-.2-g['radius'];g['rows'].append(dict(OD=od,worst_radial_remainder=rem,worst_interboard_remainder=.3-.2,passes0p1_screen=rem>=.1-1e-10))
  cases.append(g)
# Separate axial board position originalY1.0; power conditional total4.15unchanged.
ax=[]
for t in [.8,.83,.93]:
 mr,item=main_radius(1.,t);rad=max(mr,math.hypot(7,2.075),6.5,6.1)
 ax.append(dict(thickness=t,main_radius=mr,main_limiting=item,overall_radius=rad,OD18_worst_radial_remainder=9-1.3-.2-rad))
result=dict(status='NOFAB conditional mainboard thickness study only',source_board_sha256=D['sha256'],input_file_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),stackup_candidate='JLC06081H-2116 Standard, finished0.83±0.10mm',datum='B-side substrate face fixed; F-side moves outward by thickness delta, no double addition',assumptions=dict(passive_body=1.3,solder_each_side=.15,wall_nominal=1.2,wall_worst=1.3,radial_assembly_or_bow=.2,relative_interboard_spacing_loss=.2,residual_screen=.1,power_thickness_budget=4.15,OD_tolerance='unspecified'),cases=cases,axial260=ax)
(R/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
