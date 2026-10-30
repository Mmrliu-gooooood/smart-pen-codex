from pathlib import Path
import os,sys,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/tail100';sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part,pcbnew as p
O=Path(__file__).resolve().parent;W=O.parents[1];I=W/'assembly_context_audit_0818_20261030';j=json.load(open(I/'inventory.json'));L=json.load(open(I/'all103_sync.json'))['rows'];out=[]
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
 key=pre+'J202_open'
 for shift in [0,1.5,1.7,2.0]:
  s=S[key].copy();s.translate(A.Vector(0,0,shift));hits=[];dist=[]
  for k,t in S.items():
   if k in [key,pre+'main_board','Context_ONLY','REF_Context_ONLY']:continue
   v=hit(s,t)
   if v>1e-7:hits.append({'other':k,'volume_mm3':v})
   dist.append((s.distToShape(t)[0],k))
  out.append({'context':c['context'],'shift_toward_RF_mm':shift,'J202_origin_y':90.5-shift,'hits':hits,'nearest':sorted(dist)[:6],'missing_refs':missing})
(O/'geometry_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
