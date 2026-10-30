from pathlib import Path
import os,sys,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/tail100';sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part,pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;I=W/'assembly_context_audit_0818_20261030';j=json.load(open(I/'inventory.json'));L=json.load(open(I/'all103_sync.json'))['rows'];out=[]
def box(bb):return Part.makeBox(*(bb[i+3]-bb[i]for i in range(3)),A.Vector(*bb[:3]))
def hit(a,b):
 x,y=a.BoundBox,b.BoundBox
 if not all(min(getattr(x,t+'Max'),getattr(y,t+'Max'))-max(getattr(x,t+'Min'),getattr(y,t+'Min'))>1e-8 for t in 'XYZ'):return 0
 return a.common(b).Volume
for c in j['contexts']:
 q=Path(c['path']);assert hashlib.sha256(q.read_bytes()).hexdigest()==c['sha256'];d=A.openDocument(str(q));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and o.TypeId!='App::DocumentObjectGroup'};A.closeDocument(d.Name);pre='CTX_'if c['context']=='RevC'else'REF_CTX_'
 for k in list(S):
  if k.startswith(pre)and k!=pre+'main_board':del S[k]
 missing=[]
 for r in L:
  es=next(t['entities']for t in r['contexts']if t['context']==c['context'])
  if not es and r['ref'] not in ['U205','C209']:missing.append(r['ref'])
  if r['ref']in ['U205','C209']:
   dx,dz,h=(3.7,2.7,1.25)if r['ref']=='U205'else(1.52,.62,.70)
   x,y,ang,side=r['current_pose'];a=math.radians(ang);wx=abs(dx*math.cos(a))+abs(dz*math.sin(a));wz=abs(dx*math.sin(a))+abs(dz*math.cos(a));cx=x-7;cz=127-y
   S[pre+r['ref']]=box([cx-wx/2,3.194793176328504,cz-wz/2,cx+wx/2,3.194793176328504+h,cz+wz/2])
  for e in es:S[e['label']]=box(e['projected_current_bounds_not_final_assembly'])
 S[pre+'J202_open'].translate(A.Vector(0,0,1.7))
 changed={}
 for ref,xy in [('R240',(11.0,70.5)),('R241',(11.85,73.35)),('C207',(10.85,65.0))]:
  key=pre+ref;row=next(r for r in L if r['ref']==ref);old=row['current_pose'];s=S[key].copy();s.translate(A.Vector(xy[0]-old[0],0,old[1]-xy[1]));
  if ref=='R241':s.rotate(A.Vector(xy[0]-7,0,127-xy[1]),A.Vector(0,1,0),90)
  S[key]=s;changed[key]=s
 hits=[];near=[]
 for key,s in changed.items():
  for k,t in S.items():
   if k in [key,pre+'main_board','Context_ONLY','REF_Context_ONLY']:continue
   v=hit(s,t)
   if v>1e-7:hits.append({'moved':key,'other':k,'volume_mm3':v})
   near.append({'moved':key,'other':k,'gap_mm':s.distToShape(t)[0]})
 neg=S[pre+'R240'].copy();neg.translate(A.Vector(0,0,-1.));negative=hit(neg,S[pre+'R203'])
 if negative<=1e-7:raise RuntimeError('negative movement must collide')
 out.append({'R240_negative_move_plus1Y_overlap_R203_mm3':negative,'context':c['context'],'poses':{'R240':[11.0,70.5,180,'F.Cu'],'R241':[11.85,73.35,90,'F.Cu'],'C207':[10.85,65.0,-90,'F.Cu']},'hits':hits,'nearest':sorted(near,key=lambda x:x['gap_mm'])[:10],'missing_refs':missing,'source_cad_sha256':c['sha256']})
(O/'geometry_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
