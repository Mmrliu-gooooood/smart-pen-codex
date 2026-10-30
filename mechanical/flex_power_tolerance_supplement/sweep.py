import math,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'flex_power_revD_study';source=S/'inputs/href3_board_extract.json';D=json.loads(source.read_text())['mainboard']
# No changes to source CAD or frozen input; source identity included in result.
P={'wall_nominal':1.2,'wall_tolerance_plus_minus':.1,'radial_assembly_or_bow_allowance':.2,'relative_board_spacing_loss':.2,'solder_allowance':.15,'power_total_thickness_conditional':4.15,'passive_height_worstcase':1.3,'OD_tolerance':0.,'OD_tolerance_note':'Not specified: swept OD treated exact; this prevents production qualification.'}
def main_radius(y,passive):
 candidates=[(math.hypot(6,y),'board'),(math.hypot(6,y+.8),'board')]
 for p in D['parts']:
  if p['dnp']:continue
  h=(passive if p['height_basis'].startswith('ASSUMED') else p['height'])+.15;a,b,c,d=p['bounds'];ys=[y-h,y] if p['back'] else [y+.8,y+.8+h]
  candidates.extend((math.hypot(x,yy),p['ref']) for x in [a-6,c-6] for yy in ys)
 return max(candidates)
def stack(y,gap,passive):
 bottom=y-(passive+.15)-gap-4.15
 pr=max(math.hypot(7,bottom),math.hypot(7,bottom+4.15));mr,item=main_radius(y,passive)
 return max(pr,mr),bottom,('power' if pr>=mr else item)
def optimize(gap,passive):
 best=None
 # 0.001mm search granularity is numerical sampling, NOT manufacturing precision.
 for i in range(10001):
  y=-2+i*.001;r,b,item=stack(y,gap,passive)
  if best is None or r<best['radius']:best={'main_y':y,'power_y':b,'radius':r,'limiting':item}
 return best
cases=[]
# Baseline actual stacking gap collapses as passive height rises.
for label,gap,passive,optimized,reserve in [('existing_213_nominal_1p0',.3,1.,False,0),('existing_213_height1p3',0.,1.3,False,0),('respaced_no_overlap_threshold',.2,1.3,True,0),('respaced_0p1_residual_screen',.3,1.3,True,.1)]:
 best=optimize(gap,passive) if optimized else dict(zip(['radius','power_y','limiting'],stack(2.9,gap,passive)),main_y=2.9)
 rows=[]
 for od in [18.,18.5,19.]:
  available=od/2-(1.2+.1)-.2
  radial=available-best['radius'];axialgap=gap-.2
  rows.append({'OD':od,'nominal_inner_radius':od/2-1.2,'worst_radial_clearance':radial,'worst_interboard_clearance':axialgap,'required_residual_screen':reserve,'passes_stated_screen':radial>=reserve-1e-10 and axialgap>=reserve-1e-10})
 cases.append({'case':label,'passive_height':passive,'nominal_interboard_gap':gap,'optimized_position':optimized,**best,'theoretical_min_OD_radial_only':2*(best['radius']+1.2+.1+.2+reserve),'rows':rows,'caveat':'No-overlap at zero clearance is a boundary only, not an assembly recommendation.'})
# Axial board separation: maintain mainboard Y1.0 original axial case and compare height worstcase.
mr,item=main_radius(1.,1.3);pr=math.hypot(7,4.15/2);ur=math.hypot(6,2.5);rad=max(mr,pr,ur,6.1)
axial=[]
for od in [18,18.5,19]:
 clear=od/2-1.2-.1-.2-rad
 axial.append(dict(OD=od,worst_radial_clearance=clear,passes_noninterference=clear>=0,passes_0p1_residual=clear>=.1))
result={'status':'NOFAB conditional numerical supplement, not selecting OD','source_sha256':D['sha256'],'input_file_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'assumptions':P,'cases':cases,'axial_separation':{'length':260,'compared_213_length_increase':47,'main_y':1.,'power_y':-2.075,'main_radius':mr,'main_limiting':item,'power_radius':pr,'max_radius':rad,'rows':axial,'note':'No interboard overlap, so no stacked-component gap problem. Board-to-pack/RF axial gaps still placeholders. Electrical wire paths,16missingparts,and complete supports not modeled.'}}
(R/'tolerance_sweep.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
