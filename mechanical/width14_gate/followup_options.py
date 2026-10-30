import math,json
from pathlib import Path
R=Path(__file__).resolve().parent;D=json.loads((R/'input.json').read_text());out=[]
# Axially separate power: main backY-.5 retains nominal.3 above contact topY-.8.
for left in [False,True]:
 for shift in [6.,6.5,7.]:
  for jx in [13.,12.5]:
   my=-.5;cs=[]
   for x in ([0,14,-1] if left else [0,14]):cs.extend((math.hypot(x-shift,y),'outline') for y in [my,my+.93])
   for p in D['parts']:
    if p['dnp']:continue
    a,b,c,d=p['bounds'];h=p['height_total']
    if p['ref']=='J109':a,c=jx-.7,jx+.7
    ys=[my-h,my] if p['side']=='B' else [my+.93,my+.93+h]
    cs.extend((math.hypot(x-shift,y),p['ref']) for x in [a,c] for y in ys)
   rad,lim=max(cs+[(math.hypot(7,2.075),'separate_power')]);clear=8.3-.3-rad
   out.append(dict(left_extension=left,X_offset=shift,J109_x=jx,main_B_y=my,radius=rad,limiting=lim,worst_radial_clearance_OD19=clear,passes0p1_screen=clear>=.1,contact_nominal_gap=.3,contact_after_assumed_relative_loss=.1,power_axial_segment=[192,237],USB_axial_segment=[239,259],length_reference=260))
# Necessary lateral thresholds for19OD/.1residual: radius<=7.9 with existingpower14x4.15.
my=2.24;shift=7;viol=[]
for p in D['parts']:
 if p['dnp']:continue
 a,b,c,d=p['bounds'];h=p['height_total']
 if p['ref']=='J109':a,c=12.25-.7,12.25+.7
 yy=max(abs(my-h),abs(my)) if p['side']=='B' else max(abs(my+.93),abs(my+.93+h));allowed=math.sqrt(max(0,7.9**2-yy**2));rad=max(math.hypot(a-shift,yy),math.hypot(c-shift,yy))
 if rad>7.9:viol.append(dict(ref=p['ref'],source_bbox=p['bounds'],radius=rad,required_min_source_x=shift-allowed,required_max_source_x=shift+allowed,minimum_translate_right=max(0,shift-allowed-a),note='Necessary envelope shift only; electricalspacing/routing/collisions NOT approved'))
result={'status':'NOFAB diagnostic options, no final diameter or arrangement selected','axial_power_options':out,'lateral_adjustment_screen':{'main_B_y':my,'global_X_offset':shift,'J109_trial_x':12.25,'target_radius':7.9,'power_radius':math.hypot(7,my-5.9),'violators':viol,'minimum_main_B_y_from_power':5.9-math.sqrt(7.9**2-7**2),'max_J109_x_from_wire':shift+math.sqrt(7.9**2-(my+.93+2)**2)-.7,'left_extension':'Excluded: optionalleftedge requires separatecheck; these thresholds do not approve it'}}
(R/'options.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
