from pathlib import Path
import sys,json,hashlib,math
D=Path(__file__).resolve().parent;R=D.parents[2];S=D;import geometry as g
p=g.p;F=p.F_Cu;m=json.loads((S/'strategy2.json').read_text());g.old=[t for t in g.old if t.m_Uuid.AsString()not in m['removed']]
def make(t):
 if t['type']=='via':q=g.via(t['net'],t['a']);q.SetWidth(F,round(t['width']*1e6));q.SetDrill(round(t['drill']*1e6));return q
 return g.track(t['net'],g.b.GetLayerID(t['layer']),t['a'],t['b'],t['width'])
parts={tag:[make(t)for t in ts]for tag,ts in m['parts'].items()};original={k:list(v)for k,v in parts.items()};reports=[];attempts=0

def overlap(a,b,l):
 if not a.IsOnLayer(l)or not b.IsOnLayer(l):return False
 if not g.geom(a,l).BBox().Intersects(g.geom(b,l).BBox()):return False
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(g.geom(a,l),g.geom(b,l));return q.Area()>1

def ends(t):return[(t.GetStart().x,t.GetStart().y),(t.GetEnd().x,t.GetEnd().y)]
def spec(t):
 v=isinstance(t,p.PCB_VIA)
 return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else g.b.GetLayerName(t.GetLayer()),a=[t.GetStart().x/1e6,t.GetStart().y/1e6],b=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
# Only grid-generated long/branch paths; all analytic local escapes, AON and every via stay exact.
for tag in [tag for tag in parts if tag!='r203_supply']:
 ts=parts[tag];net=ts[0].GetNetname();external=[q for k,qs in parts.items()if k!=tag for q in qs if q.GetNetname()==net]+[q for q in g.pads if q.GetNetname()==net]+[q for q in g.old if q.GetNetname()==net];fixed=set();contacts={}
 for i,t in enumerate(ts):
  if isinstance(t,p.PCB_VIA):fixed.add(i);continue
  hit=[j for j,q in enumerate(external)if overlap(t,q,t.GetLayer())]
  if hit:fixed.add(i);contacts[str(i)]=hit
 # Explicit geometric same-path centerline crossing/branch is conservatively anchored.
 def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 def intersects(t,u):
  a,b=ends(t);c,d=ends(u)
  if max(min(a[0],b[0]),min(c[0],d[0]))>min(max(a[0],b[0]),max(c[0],d[0]))or max(min(a[1],b[1]),min(c[1],d[1]))>min(max(a[1],b[1]),max(c[1],d[1])):return False
  return cross(a,b,c)*cross(a,b,d)<=0 and cross(c,d,a)*cross(c,d,b)<=0
 for i,t in enumerate(ts):
  if isinstance(t,p.PCB_VIA):continue
  for j in range(i-2):
   q=ts[j]
   if not isinstance(q,p.PCB_VIA)and q.GetLayer()==t.GetLayer()and intersects(t,q):fixed.update([i,j])
 g.objs=sum(parts.values(),[]);out=[];changes=[];i=0
 while i<len(ts):
  t=ts[i]
  if i in fixed:out.append(t);i+=1;continue
  end=i
  while end+1<len(ts)and end+1 not in fixed and not isinstance(ts[end+1],p.PCB_VIA)and ts[end+1].GetLayer()==t.GetLayer()and ts[end+1].GetWidth()==t.GetWidth()and ts[end].GetEnd()==ts[end+1].GetStart():end+=1
  selected=i;new=t
  for j in range(end,i,-1):
   a=[t.GetStart().x/1e6,t.GetStart().y/1e6];b=[ts[j].GetEnd().x/1e6,ts[j].GetEnd().y/1e6]
   if a==b:continue
   trial=g.track(net,t.GetLayer(),a,b,t.GetWidth()/1e6);attempts+=1;g.alltemps.append(trial)
   # New contact to any external same-net object would create a new real branch: reject.
   if any(overlap(trial,q,t.GetLayer())for q in external):continue
   if g.errors([trial]):continue
   # Prevent shortcuts crossing another remaining segment of the same path.
   others=[q for k,q in enumerate(ts)if k<i or k>j]
   bad=False
   for q in others:
    if isinstance(q,p.PCB_VIA)or q.GetLayer()!=trial.GetLayer():continue
    if intersects(trial,q)and not(set(ends(trial))&set(ends(q))):bad=True;break
   if bad:continue
   selected=j;new=trial;break
  out.append(new)
  if selected>i:changes.append({'first_segment':i,'last_segment':selected,'replacement':spec(new),'old_length_mm':sum(math.dist(spec(q)['a'],spec(q)['b'])for q in ts[i:selected+1]),'new_length_mm':math.dist(spec(new)['a'],spec(new)['b'])})
  i=selected+1
 parts[tag]=out;reports.append({'tag':tag,'before':len(ts),'after':len(out),'fixed_segment_indices':sorted(fixed),'external_contact_anchors':contacts,'changes':changes});print(tag,len(ts),'->',len(out),'attempts',attempts,flush=True)
# Every result checked jointly against original physical board and all other result nets.
g.objs=[];allnew=sum(parts.values(),[]);errors=g.errors(allnew)
if errors:raise RuntimeError(str(errors[:10]))
out={'status':'EXACT_VISIBILITY_COMPLETE_MODEL_NOT_NATIVE','parent_sha':m['parent_sha'],'removed':m['removed'],'original_model_sha256':hashlib.sha256((S/'strategy2.json').read_bytes()).hexdigest(),'complete_all':True,'parts':{k:[spec(t)for t in ts]for k,ts in parts.items()}}
(D/'model.json').write_text(json.dumps(out,indent=2)+'\n');(D/'simplification.json').write_text(json.dumps({'single_deterministic_pass':True,'attempts':attempts,'reports':reports,'finite_errors':errors,'constraints':['Fixed actual contact segments, all analytical local parts, exact vias and widths retained','No additional external same-net branch contact permitted','Actual finite copper clearance, board edge and MEMS rule areas checked; no raster-only acceptance','No full-length re-search or native board generated']},indent=2)+'\n')
