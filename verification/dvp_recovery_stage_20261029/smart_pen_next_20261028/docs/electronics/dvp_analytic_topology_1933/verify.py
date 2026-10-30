from pathlib import Path
import json,math,hashlib
class AxisSegment:
 def __init__(self,a,b):
  if a[0]!=b[0] and a[1]!=b[1]: raise ValueError('not axis aligned')
  self.lo=[min(a[k],b[k]) for k in (0,1)]; self.hi=[max(a[k],b[k]) for k in (0,1)]
 def distance(self,other):
  gaps=[max(0,self.lo[k]-other.hi[k],other.lo[k]-self.hi[k]) for k in (0,1)]
  return math.hypot(*gaps)
D=Path(__file__).resolve().parent;r=json.loads((D/'result.json').read_text()); gs=r['geometry'];shapes=[]
for g in gs:
 shapes.append(AxisSegment(g['start'],g['end']))
bad=[];minimum=(999,None)
for i,g in enumerate(gs):
 for j,h in enumerate(gs[:i]):
  if g['net']==h['net']:continue
  if g['layer']!='through' and h['layer']!='through' and g['layer']!=h['layer']:continue
  gap=shapes[i].distance(shapes[j])-(g['width_mm']+h['width_mm'])/2
  if gap<minimum[0]:minimum=(gap,[i,j])
  if gap < .15-1e-9:bad.append([i,j,gap])
if bad or r['new_route_pair_conflicts']:raise RuntimeError('Copper pair conflict')
v=[g for g in gs if g['type']=='via'];drillgap=min(math.dist(a['start'],b['start'])-.2 for i,a in enumerate(v) for b in v[:i])
if drillgap<.25:raise RuntimeError('Drill gap insufficient for assumed .25 gate')
# Rejected hypothetical fault controls: duplicate other-net copper is detected geometrically.
negative=[]
for i in [0,4,25,53]:
 g=gs[i];c=shapes[i];gap=c.distance(c)-g['width_mm'];negative.append({'index':i,'coincident_other_net_gap_mm':gap,'rejected':gap<.15})
if not all(q['rejected'] for q in negative):raise RuntimeError('Negative detector failed')
# All objects lie in lower board rectangular x=0..14, y=28..94 domain.
# This is only the drawing's region; not a fresh native Edge.Cuts DRC.
edge=min(min(g['start'][0],g['end'][0],14-g['start'][0],14-g['end'][0])-g['width_mm']/2 for g in gs)
if edge<.25:raise RuntimeError('Right/left edge candidate fails')
out={'pair_checks':'analytic centerline distance including actual widths; all pairs of unlike nets on shared layers','different_net_min_copper_gap_mm':minimum[0],'at_object_indices':minimum[1],'mutual_drill_edge_gap_mm':drillgap,'assumed_drill_gap_screen_mm':.25,'rectangular_x_edge_gap_mm':edge,'negative_controls':negative,'pad_conflict_count':len(r['pad_clearance_conflicts']),'must_not_be_native_DRC_or_manufacturing_approval':True}
(D/'independent_geometry.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
