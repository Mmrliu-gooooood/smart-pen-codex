from pathlib import Path
import os,json,math,collections
os.environ['XDG_CONFIG_HOME']='/tmp/pen-aonplan2318'
import pcbnew as p
from finite_copper import build,L
D=Path(__file__).resolve().parent;R=D.parents[2];a=p.LoadBoard(str(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(R/'hardware/gnd_conservative_recovery_2305/native/mainboard_revD.kicad_pcb'));uid=lambda t:t.m_Uuid.AsString();old={uid(t):t for t in a.GetTracks()if t.GetNetname()=='3V3_AON'};current=list(b.GetTracks());pads=[q for f in b.GetFootprints()for q in f.Pads()];op={uid(q):q for f in a.GetFootprints()for q in f.Pads()};np={uid(q):q for q in pads}
def ps(q):return(q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetLayerSet().FmtHex(),q.GetOrientationDegrees(),q.GetSize().x,q.GetSize().y)
changed={u for u in op if ps(op[u])!=ps(np[u])};nodes=[x for x in build(a)['3V3_AON']if '/'not in x[0]];par=list(range(len(nodes)))
def root(i):
 while par[i]!=i:par[i]=par[par[i]];i=par[i]
 return i
for i,(_,_,si)in enumerate(nodes):
 for j,(_,_,sj)in enumerate(nodes[:i]):
  for l in si.keys()&sj.keys():
   if not si[l].BBox().Intersects(sj[l].BBox()):continue
   q=p.SHAPE_POLY_SET();q.BooleanIntersection(si[l],sj[l])
   if q.Area()>1:par[root(i)]=root(j);break
groups=collections.defaultdict(list)
for i,n in enumerate(nodes):groups[root(i)].append(n[0])
# Full real current pads and routes, not historical conflict table.
cache={}
def shape(t,l,c):
 k=(uid(t),l,c)
 if k not in cache:
  q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,c,100,p.ERROR_OUTSIDE);cache[k]=q
 return cache[k]
def hit(t,q,c=150000):
 for l in L:
  if not t.IsOnLayer(l)or not q.IsOnLayer(l):continue
  x=shape(t,l,c);y=shape(q,l,0)
  if not x.BBox().Intersects(y.BBox()):continue
  z=p.SHAPE_POLY_SET();z.BooleanIntersection(x,y)
  if z.Area()>1:return True
 return False
# pad names can duplicate, map via uuid-disambiguated suffix.
names=collections.Counter(q.GetParentFootprint().GetReference()+'.'+q.GetNumber()for q in op.values())
label={q.GetParentFootprint().GetReference()+'.'+q.GetNumber()+('#'+u if names[q.GetParentFootprint().GetReference()+'.'+q.GetNumber()]>1 else ''):u for u,q in op.items()}
hazards=set()
for v in json.loads((R/'hardware/j202_low_speed_reference_candidate/preflight.native_drc.json').read_text())['violations']:
 for x in v['items']:hazards.add(x['uuid'])
conf={}
for u,t in old.items():
 bad=[]
 if u in hazards:bad.append(dict(kind='original_DRC_hazard'))
 for q in current+pads:
  if t.GetNetname()!=q.GetNetname()and hit(t,q):bad.append(dict(kind='current_copper_clearance',other=uid(q),net=q.GetNetname()))
  if uid(q)in changed and q.GetNetname()=='3V3_AON'and hit(t,q,0):bad.append(dict(kind='changed_AON_pad_contact',other=uid(q)))
 if isinstance(t,p.PCB_VIA):
  for q in current:
   if not isinstance(q,p.PCB_VIA):continue
   gap=math.hypot(t.GetPosition().x-q.GetPosition().x,t.GetPosition().y-q.GetPosition().y)-(t.GetDrillValue()+q.GetDrillValue())/2
   if gap<250000-1:bad.append(dict(kind='current_hole_clearance',other=uid(q),gap_mm=gap/1e6))
  for q in pads:
   # conservative no new via-in-pad, including same-net. Old intentional EP vias rejected for this bounded block.
   center=t.GetPosition();bb=q.GetBoundingBox();r=t.GetWidth(p.F_Cu)//2
   if hit(t,q,0):bad.append(dict(kind='via_annulus_pad_overlap',other=uid(q)))
 if bad:conf[u]=bad
rows=[]
for g in groups.values():
 tracks=sorted(set(g)&old.keys());term=sorted(n for n in g if n in label)
 if not tracks:continue
 reasons=[]
 if not term:reasons.append('no_original_pad_terminal')
 if any(label[n]in changed for n in term):reasons.append('changed_original_pad_terminal')
 if any(label[n]in hazards for n in term):reasons.append('original_pad_DRC_hazard')
 if any(u in conf for u in tracks):reasons.append('current_conflict_or_old_hazard')
 if not any(isinstance(old[u],p.PCB_VIA)for u in tracks):reasons.append('no_plane_via')
 rows.append(dict(id=len(rows),objects=tracks,pads=term,accepted_preflight=not reasons,rejection=reasons,conflicting_objects={u:conf[u]for u in tracks if u in conf}))
print(json.dumps(dict(current_board_objects=len(current),current_physical_pads=len(pads),current_sha=__import__('hashlib').sha256((R/'hardware/gnd_conservative_recovery_2305/native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),status='WHOLE_OLD_AON_COMPONENT_SCREEN_ONLY',old_AON_objects=len(old),components=rows,accepted_components=sum(x['accepted_preflight']for x in rows),accepted_objects=sum(len(x['objects'])for x in rows if x['accepted_preflight']),rules=['whole track+pad connected subgraphs without zones','reject any changed old terminal','all current pad/copper layers checked via IsOnLayer','original width/drill kept; no trims','full native DRC and fresh core connectivity still required']),indent=2))
