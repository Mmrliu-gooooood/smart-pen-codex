from pathlib import Path
import os,json,math,re,hashlib,shutil,collections
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'gate_control_output_candidate';src=S/'mainboard_revD.kicad_pcb'
if hashlib.sha256(src.read_bytes()).hexdigest()!='508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35':raise RuntimeError('Input changed')
N=D/'native';N.mkdir(exist_ok=True)
for q in S.iterdir():
 if q.is_dir()and(q.name.endswith('.pretty')or q.name=='schematic'):
  if not(N/q.name).exists():shutil.copytree(q,N/q.name)
 elif q.is_file()and(q.suffix in ['.kicad_sch','.kicad_sym','.kicad_pro','.kicad_dru']or q.name in ['fp-lib-table','sym-lib-table']):shutil.copy2(q,N/q.name)
b=p.LoadBoard(str(src));xy=lambda q:(q.x,q.y);pt=lambda q:p.VECTOR2I(*q)
tr={t.m_Uuid.AsString():t for t in b.GetTracks()if t.GetNetname()=='CAM_ON'and not isinstance(t,p.PCB_VIA)};via=[t for t in b.GetTracks()if t.GetNetname()=='CAM_ON'and isinstance(t,p.PCB_VIA)]
if len(tr)!=44 or len(via)!=3:raise RuntimeError('Scope changed')
branch=(8400000,67950000);g=collections.defaultdict(list);edgeids={}
def on(q,a,z):return(q[0]-a[0])*(z[1]-a[1])==(q[1]-a[1])*(z[0]-a[0])and min(a[0],z[0])<=q[0]<=max(a[0],z[0])and min(a[1],z[1])<=q[1]<=max(a[1],z[1])
for uid,t in tr.items():
 l=int(t.GetLayer());a,z=xy(t.GetStart()),xy(t.GetEnd());points=[a,z]
 if l==p.F_Cu and branch not in points and on(branch,a,z):points.append(branch)
 points.sort(key=lambda q:math.dist(a,q))
 for u,v in zip(points,points[1:]):
  ka,kz=(l,*u),(l,*v);g[ka].append(kz);g[kz].append(ka);edgeids[frozenset([ka,kz])]=uid
anchors={k for k in g if len(g[k])!=2};anchors|={k for k in g if k[1:]in [xy(v.GetPosition())for v in via]};anchors.add((p.F_Cu,*branch))
seen=set();chains=[]
for a in sorted(anchors):
 for z in g[a]:
  e=frozenset([a,z])
  if e in seen:continue
  path=[a,z];seen.add(e)
  while path[-1]not in anchors:
   nxt=next(k for k in g[path[-1]]if k!=path[-2]);seen.add(frozenset([path[-1],nxt]));path.append(nxt)
  chains.append(path)
if len(chains)!=6:raise RuntimeError('Unexpected branch graph '+str(len(chains)))
# Native finite-polygon clearance screen, 0.15mm default plus 4um numerical margin.
obstacles={p.F_Cu:[],p.B_Cu:[]}
for l in obstacles:
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.IsOnLayer(l)and a.GetNetname()!='CAM_ON':
    q=p.SHAPE_POLY_SET();a.TransformShapeToPolygon(q,l,154000,250,p.ERROR_OUTSIDE);obstacles[l].append((f.GetReference()+'.'+a.GetNumber(),q))
 for t in b.GetTracks():
  if t.IsOnLayer(l)and t.GetNetname()!='CAM_ON':
   q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,154000,250,p.ERROR_OUTSIDE);obstacles[l].append((t.m_Uuid.AsString(),q))
def visible(a,z):
 l=a[0];t=p.PCB_TRACK(b);t.SetStart(pt(a[1:]));t.SetEnd(pt(z[1:]));t.SetLayer(l);t.SetWidth(150000);q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,0,250,p.ERROR_OUTSIDE)
 for name,o in obstacles[l]:
  if not q.BBox().Intersects(o.BBox()):continue
  ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(q,o)
  if ix.Area()>1:return False,name
 return True,None
results=[];paths=[]
for chain in chains:
 keep_original=(p.B_Cu,10800000,67950000)in [chain[0],chain[-1]]
 out=[chain[0]];i=0;rejects=[]
 while i<len(chain)-1:
  if keep_original:j=i+1
  else:
   j=len(chain)-1
   while j>i+1:
    ok,hit=visible(chain[i],chain[j])
    if ok:break
    rejects.append({'from':chain[i],'to':chain[j],'blocked_by':hit});j-=1
  # Existing adjacent segment may fail stricter4um safety margin; no geometry change there.
  out.append(chain[j]);i=j
 paths.append(out);results.append({'before':chain,'after':out,'before_segments':len(chain)-1,'after_segments':len(out)-1,'rejected_visibility_candidates':rejects,'original_U301_stub_preserved':keep_original})
# Keep unchanged original tracks by exact identity; split branch edge is intentionally versioned.
oldgeom={(int(t.GetLayer()),xy(t.GetStart()),xy(t.GetEnd())):u for u,t in tr.items()};keep=set();add=[]
for path in paths:
 for a,z in zip(path,path[1:]):
  key=(a[0],tuple(a[1:]),tuple(z[1:]));rev=(a[0],tuple(z[1:]),tuple(a[1:]));uid=oldgeom.get(key,oldgeom.get(rev))
  if uid:keep.add(uid)
  else:add.append((a,z))
removed=set(tr)-keep;raw=re.sub(r'\n\t\(segment\n.*?\n\t\)',lambda m:''if any(u in m[0]for u in removed)else m[0],src.read_text(),flags=re.S);dest=N/'mainboard_revD.kicad_pcb';dest.write_text(raw);outb=p.LoadBoard(str(dest));new=[]
for a,z in add:
 t=p.PCB_TRACK(outb);t.SetStart(pt(a[1:]));t.SetEnd(pt(z[1:]));t.SetWidth(150000);t.SetLayer(a[0]);t.SetNet(outb.FindNet('CAM_ON'));outb.Add(t);new.append({'uuid':t.m_Uuid.AsString(),'net':'CAM_ON','type':'track','a':[v/1e6 for v in a[1:]],'z':[v/1e6 for v in z[1:]],'width':.15,'layer':outb.GetLayerName(a[0])})
p.ZONE_FILLER(outb).Fill(outb.Zones());p.SaveBoard(str(dest),outb)
rows=json.loads((S/'new_routes.json').read_text());newrows=[r for r in rows if r['uuid']not in removed]+new;(D/'new_routes.json').write_text(json.dumps(newrows,indent=2))
def geometry(t):return{'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'width':p.ToMM(t.GetWidth()),'a':[v/1e6 for v in xy(t.GetStart())],'z':[v/1e6 for v in xy(t.GetEnd())]}
report={'source_pcb_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_pcb_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'scope':'CAM_ON only, changed copper path NOT equivalent merging; all3via/pads/trueFbranch kept','chains':results,'removed':[geometry(tr[u])for u in sorted(removed)],'added':new,'unchanged_via_UUIDs':[t.m_Uuid.AsString()for t in via],'before_tracks':44,'after_tracks':len(keep)+len(add),'before_length_mm':sum(t.GetLength()/1e6 for t in tr.values()),'after_length_mm':sum(math.dist(a[1:],z[1:])/1e6 for path in paths for a,z in zip(path,path[1:]))}
(D/'maintenance_delta.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ['chains','removed','added']},indent=2))
