import os,sys,json,hashlib,math
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/mech-dvp-two-ref'
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;W=R.parent;M=W/'smart_pen_mechanics_next_20261028/mechanical';P=W/'smart_pen_mechanics_dvp_joint_audit_20261029_1950';J=json.loads((P/'screen_results_normal.json').read_text());V=A.Vector;B=2.264793176328504
poses={'R206':[(8,47),(9,45.5),(8,45.5),(7,47),(9,46)],'J107':[(3.2,84),(3.7,84),(2.7,83.5),(2.7,84.5)]}
def bounds(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def gap(a,b):
 x,y=a.BoundBox,b.BoundBox;return math.sqrt(sum(max(0,getattr(x,t+'Min')-getattr(y,t+'Max'),getattr(y,t+'Min')-getattr(x,t+'Max'))**2 for t in 'XYZ'))
def hit(a,b):
 x,y=a.BoundBox,b.BoundBox
 if not all(min(getattr(x,t+'Max'),getattr(y,t+'Max'))-max(getattr(x,t+'Min'),getattr(y,t+'Min'))>1e-8 for t in 'XYZ'):return 0
 return a.common(b).Volume
out=[]
for c in J['contexts']:
 name=c['context'];path=M/'gate508e_joint_screen_0247'/('RevC_gate508e.FCStd'if name=='RevC'else'RevD_gate508e.FCStd')if name in ['RevC','RevD_BENCH']else M/f'compliant_retainer_longarc_0415/access_revision/ACCESS_retainer_OD{name[-2:]}_t0p93_NOFAB.FCStd'
 if hashlib.sha256(path.read_bytes()).hexdigest()!=c['source_sha256']:raise ValueError('source changed')
 d=A.openDocument(str(path));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and o.TypeId!='App::DocumentObjectGroup'};A.closeDocument(d.Name)
 changed={}
 for k,q in c['contracts'].items():
  bb=q['bounds'];z=Part.makeBox(bb[3]-bb[0],bb[4]-bb[1],bb[5]-bb[2],V(*bb[:3]));S[k]=z
  if q['ref']=='R206':z.translate(V(0,0,1));changed[k]=z
  if q['ref']=='J107':z.translate(V(.5,0,0));changed[k]=z
 collisions=[];nearest=[];all_changed_hits=[]
 for k,s in S.items():
  if k not in c['contracts']:continue
  for kk,t in S.items():
   if kk==k or kk in ['Context_ONLY','REF_Context_ONLY']or kk.endswith('main_board'):continue
   v=hit(s,t)
   if v>1e-7:all_changed_hits.append({'moved':k,'other':kk,'volume_mm3':v})
   if k not in changed:continue
   if v>1e-7:collisions.append({'moved':k,'other':kk,'volume_mm3':v})
   if gap(s,t)<3:nearest.append({'moved':k,'other':kk,'distance_mm':s.distToShape(t)[0]})
 if collisions:raise ValueError('selected combined collision')
 negatives=[]
 for ref,shift,target,minimum in [('R206',V(0,0,-1),'HousingRight',.18),('J107',V(-.5,0,0),'Lower_common_datum_STUDY',.019)]:
  if ref=='J107'and not name.startswith('ACCESS'):continue
  kk=next(k for k,q in c['contracts'].items()if q['ref']==ref and(ref!='J107'or k[-1]=='2'));s=changed[kk].copy();s.translate(shift);tt=next(v for k,v in S.items()if k.endswith(target));v=hit(s,tt)
  if v<minimum:raise ValueError('negative predecessor missed')
  negatives.append({'ref':ref,'restored_predecessor_collision_mm3':v})
 nearest.sort(key=lambda x:x['distance_mm']);out.append({'context':name,'two_ref_collisions':collisions,'nearest_non_board':nearest[:12],'all29_ref_remaining_collisions':all_changed_hits,'negative_controls':negatives})
result={'status':'TWO_REF_NOMINAL_CLEARANCE_CANDIDATE_ONLY_NOFAB','R206_pose':[9,46,0,'B.Cu'],'J107_pose':[3.2,84,180,'B.Cu'],'J107_pads':[[2,81.5],[2,83.9],[2,86.3]],'contexts':out,'scope':'full budgets retained; no real hardware/process/tolerance qualification; external bench R222 remains blocked'}
(R/('selection_optimized.json'if sys.flags.optimize else 'selection.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
