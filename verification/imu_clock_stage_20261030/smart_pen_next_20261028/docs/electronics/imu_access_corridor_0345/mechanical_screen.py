import os,sys,json,hashlib,math
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/mech-dvp-two-ref'
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/docs/electronics/imu_access_corridor_0345');W=Path('/workspace/scratch/fe148e758944');M=W/'smart_pen_mechanics_next_20261028/mechanical';P=W/'smart_pen_mechanics_dvp_joint_audit_20261029_1950';J=json.loads((P/'screen_results_normal.json').read_text());V=A.Vector;B=2.264793176328504
poses={'J107':[(3.2,88),(5.2,84)]}
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
 for k,q in c['contracts'].items():
  bb=q['bounds'];S[k]=Part.makeBox(bb[3]-bb[0],bb[4]-bb[1],bb[5]-bb[2],V(*bb[:3]))
 for k,q in c['contracts'].items():
  if q['ref']=='R206':S[k].translate(V(9-q['new_pose'][0],0,-(46-q['new_pose'][1])))
 rows=[]
 for ref,ps in poses.items():
  ks=[k for k,q in c['contracts'].items()if q['ref']==ref];oldxy=c['contracts'][ks[0]]['new_pose'][:2]
  for x,y in ps:
   new={}
   for k in ks:
    z=S[k].copy();z.translate(V(x-oldxy[0],0,-(y-oldxy[1])));new[k]=z
   others={k:s for k,s in S.items()if k not in ks and k not in ['Context_ONLY','REF_Context_ONLY']};hits=[];near=[]
   for k,s in new.items():
    for kk,t in others.items():
     if kk.endswith('main_board'):continue # intentional mounted-face contact excluded from free clearance
     v=hit(s,t)
     if v>1e-7:hits.append({'moved':k,'other':kk,'volume_mm3':v})
     if gap(s,t)<3:
      dd=s.distToShape(t)[0];near.append({'moved':k,'other':kk,'distance_mm':dd})
   near.sort(key=lambda r:r['distance_mm']);rows.append({'ref':ref,'pose':[x,y],'translation_mm':math.hypot(x-oldxy[0],y-oldxy[1]),'hits':hits,'nearest_non_board':near[:6],'moved_bounds':{k:bounds(s)for k,s in new.items()}})
 out.append({'context':name,'source_sha256':c['source_sha256'],'rows':rows});print(name,'done',flush=True)
(R/'mechanical_screen.json').write_text(json.dumps({'status':'TWO_J107_POSE_SCREEN_NOFAB','source_review_manifest_sha256':hashlib.sha256((P/'manifest.json').read_bytes()).hexdigest(),'contexts':out,'scope':'exact retained envelopes, only two refs individually varied; combine selected disjoint groups and recheck before acceptance'},indent=2)+'\n')
for ref,ps in poses.items():
 for xy in ps:
  rr=[next(r for r in c['rows']if r['ref']==ref and r['pose']==list(xy))for c in out];print(ref,xy,'hits',sum(len(r['hits'])for r in rr),'minimum',min(r['nearest_non_board'][0]['distance_mm']for r in rr),flush=True)
