from pathlib import Path
import os,json,hashlib,math,collections,time
os.environ['XDG_CONFIG_HOME']='/tmp/pen-recovery2005-config'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';N=R/'hardware/dvp_mechanical_clearance_successor_1957/native/mainboard_revD.kicad_pcb'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
if sha(S)!='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038' or sha(N)!='f92c7517b40466208d907d30b076ccd80d40bb3c298c162b40891f86b5070f19':raise RuntimeError('SOURCE HASH')
a=p.LoadBoard(str(S));b=p.LoadBoard(str(N));L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def pose(f):return(f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer())
fa={f.GetReference():f for f in a.GetFootprints()};fb={f.GetReference():f for f in b.GetFootprints()};changed={r for r in fa if pose(fa[r])!=pose(fb[r])};old=list(a.GetTracks());new=list(b.GetTracks());uid=lambda t:t.m_Uuid.AsString()
def meta(t):return{'uuid':uid(t),'net':t.GetNetname(),'type':'via'if isinstance(t,p.PCB_VIA)else'track','layer':'through'if isinstance(t,p.PCB_VIA)else a.GetLayerName(t.GetLayer()),'start_mm':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end_mm':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'width_mm':(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6}
def poly(t,l,clear=0):
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,clear,50,p.ERROR_OUTSIDE);return q
cache={}
def cached(t,l,clear=0):
 k=(uid(t),l,clear)
 if k not in cache:cache[k]=poly(t,l,clear)
 return cache[k]
def overlaps(t,q,l,clear=150000):
 v=p.SHAPE_POLY_SET();v.BooleanIntersection(cached(t,l,clear),cached(q,l,0));return v.Area()>1
cell=1000000
def cells(t,margin=0):
 z=t.GetBoundingBox();return[(x,y)for x in range(math.floor((z.GetX()-margin)/cell),math.floor((z.GetRight()+margin)/cell)+1)for y in range(math.floor((z.GetY()-margin)/cell),math.floor((z.GetBottom()+margin)/cell)+1)]
newidx=collections.defaultdict(list)
for t in new:
 for c in cells(t):newidx[c].append(t)
movedpads=[(r,q)for r in sorted(changed) for q in fb[r].Pads()];padidx=collections.defaultdict(list)
for r,q in movedpads:
 for c in cells(q):padidx[c].append((r,q))
conf=collections.defaultdict(list);same_net_contacts=collections.defaultdict(list);drillconf=[]
for i,t in enumerate(old):
 seen=set()
 for c in cells(t,150000):
  for q in newidx.get(c,[]):
   if uid(q)in seen:continue
   seen.add(uid(q));common=[l for l in L if t.IsOnLayer(l)and q.IsOnLayer(l)]
   if t.GetNetname()==q.GetNetname():
    if any(overlaps(t,q,l,1)for l in common):same_net_contacts[uid(t)].append(uid(q))
   elif any(overlaps(t,q,l)for l in common):conf[uid(t)].append({'kind':'new_route_copper_clearance','other_uuid':uid(q),'other_net':q.GetNetname()})
 seen=set()
 for c in cells(t,150000):
  for r,q in padidx.get(c,[]):
   if uid(q)in seen:continue
   seen.add(uid(q))
   if t.GetNetname()==q.GetNetname():continue
   common=[l for l in L if t.IsOnLayer(l)and q.IsOnLayer(l)]
   if any(overlaps(t,q,l)for l in common):conf[uid(t)].append({'kind':'relocated_pad_clearance','ref':r,'pin':q.GetNumber(),'other_net':q.GetNetname()})
 if isinstance(t,p.PCB_VIA):
  for q in new:
   if not isinstance(q,p.PCB_VIA):continue
   d=math.hypot(t.GetPosition().x-q.GetPosition().x,t.GetPosition().y-q.GetPosition().y)-(t.GetDrillValue()+q.GetDrillValue())/2
   if d<250000-1:conf[uid(t)].append({'kind':'old_new_drill_clearance','other_uuid':uid(q),'edge_distance_mm':d/1e6});drillconf.append([uid(t),uid(q),d/1e6])
  # Include same-net relocated pad drill intersection, no via-in-pad exemption.
  h=p.PCB_VIA(a);h.SetPosition(t.GetPosition());h.SetWidth(p.F_Cu,t.GetDrillValue());h.SetDrill(t.GetDrillValue());h.SetLayerPair(p.F_Cu,p.B_Cu);h.SetViaType(p.VIATYPE_THROUGH)
  for r,q in movedpads:
   if any(overlaps(h,q,l,0)for l in L if q.IsOnLayer(l)):
    conf[uid(t)].append({'kind':'drill_relocated_pad_overlap_including_same_net','ref':r,'pin':q.GetNumber()})
 if i%1000==0:print('screen',i,len(conf),flush=True)
# Native original violations are explicit hazards, not erased by candidate clearances.
rpt=json.loads((R/'hardware/j202_low_speed_reference_candidate/preflight.native_drc.json').read_text());hazards=collections.defaultdict(list)
for v in rpt['violations']:
 for it in v['items']:hazards[it['uuid']].append({'type':v['type'],'description':v['description']})
hazard_nets=set()
for t in list(a.GetTracks())+[q for f in a.GetFootprints()for q in f.Pads()]:
 if uid(t)in hazards:hazard_nets.add(t.GetNetname())
# Quantify exclusion of new vias in OLD reference fill; no claim these fills remain valid.
plane=[]
for zi,z in enumerate(a.Zones()):
 if z.GetIsRuleArea():continue
 for l in L:
  if not z.IsOnLayer(l):continue
  filled=z.GetFilledPolysList(l);union=p.SHAPE_POLY_SET();rows=[]
  for q in new:
   if not isinstance(q,p.PCB_VIA):continue
   cut=poly(q,l,max(150000,z.GetLocalClearance()));cut.BooleanIntersection(filled)
   if cut.Area()>1:rows.append({'via_uuid':uid(q),'net':q.GetNetname(),'xy_mm':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'old_fill_exclusion_area_mm2':cut.Area()/1e12});union.BooleanAdd(cut)
  plane.append({'zone_index':zi,'net':z.GetNetname(),'layer':a.GetLayerName(l),'old_fill_area_mm2':filled.Area()/1e12,'new_via_exclusion_union_mm2':union.Area()/1e12,'vias':rows,'not_refilled':True})
# Build original track-only graph with ALL zones removed in memory. Pads that moved are not accepted terminal bridges.
for z in list(a.Zones()):a.Remove(z)
a.BuildConnectivity();cn=a.GetConnectivity();alltracks={uid(t):t for t in old};parent={k:k for k in alltracks}
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
def join(x,y):
 x,y=find(x),find(y)
 if x!=y:parent[y]=x
fixedpadlinks=collections.defaultdict(list);oldpadlinks={};safe={k for k in alltracks if k not in conf and k not in hazards}
for t in old:
 k=uid(t);links=[]
 for q in cn.GetConnectedPads(t):
  r=q.GetParentFootprint().GetReference();name=r+'.'+q.GetNumber();links.append(name)
  if k in safe and r not in changed:fixedpadlinks[uid(q)].append(k)
 oldpadlinks[k]=sorted(links)
 if k in safe:
  for q in cn.GetConnectedTracks(t):
   u=uid(q)
   if u in safe and q.GetNetname()==t.GetNetname():join(k,u)
for ids in fixedpadlinks.values():
 for k in ids[1:]:join(ids[0],k)
groups=collections.defaultdict(list)
for k in safe:groups[find(k)].append(k)
components=[]
for ids in groups.values():
 net=alltracks[ids[0]].GetNetname();fixed=sorted({q for k in ids for q in oldpadlinks[k]if q.rsplit('.',1)[0]not in changed});moved=sorted({q for k in ids for q in oldpadlinks[k]if q.rsplit('.',1)[0]in changed})
 components.append({'net':net,'objects':len(ids),'uuids':sorted(ids),'fixed_pad_contacts':fixed,'old_moved_pad_contacts_not_retained':moved,'new_same_net_route_contact_objects':sorted({q for k in ids for q in same_net_contacts[k]}),'candidate_role':'fixed_terminal_subgraph'if len(fixed)>=2 else'one_fixed_terminal_fragment'if fixed else'floating_or_plane_dependent_fragment'})
components.sort(key=lambda x:(x['net'],-x['objects'],x['uuids'][0]));netrows=[]
for net in sorted({t.GetNetname()for t in old}):
 ids={uid(t)for t in old if t.GetNetname()==net};terms=sorted(f.GetReference()+'.'+q.GetNumber()for f in b.GetFootprints()for q in f.Pads()if q.GetNetname()==net);move=sorted(t for t in terms if t.rsplit('.',1)[0]in changed);comps=[x for x in components if x['net']==net];whole=net not in hazard_nets and len(comps)==1 and not(ids-set(safe)) and not move and set(comps[0]['fixed_pad_contacts'])==set(terms) and len(terms)>=2
 netrows.append({'net':net,'original_objects':len(ids),'new_geometry_conflict_objects':len(ids&set(conf)),'original_violation_objects':len(ids&set(hazards)),'retained_geometry_candidate_objects':len(ids&safe),'fixed_terminal_subgraphs':sum(len(c['fixed_pad_contacts'])>=2 for c in comps),'original_net_violation_hazard':net in hazard_nets,'all_current_terminals':terms,'relocated_terminals':move,'whole_track_net_candidate':whole,'components':[i for i,c in enumerate(components)if c['net']==net]})
conflict_count=sum(bool(v) for v in conf.values());hazard_track_count=sum(bool(hazards.get(k))for k in alltracks)
objects=[dict(meta(t),new_conflicts=conf[uid(t)],original_violations=hazards[uid(t)],old_pad_contacts=oldpadlinks[uid(t)],geometry_candidate=uid(t)in safe)for t in old]
out={'status':'READ_ONLY_RECOVERY_PLAN_NOFAB_NO_NATIVE_OUTPUT','baseline_sha':sha(S),'target_sha':sha(N),'changed_refs':sorted(changed),'original_objects':len(old),'target_objects':len(new),'new_conflict_object_count':conflict_count,'original_violation_track_object_count':hazard_track_count,'candidate_object_count':len(safe),'whole_track_net_candidates':[n['net']for n in netrows if n['whole_track_net_candidate']],'net_summary':netrows,'components':components,'old_fill_new_via_antipad_exclusions':plane,'old_new_drill_conflicts':drillconf,'objects':objects,'limits':['No old copper added to target or saved native.','Whole-net candidates are track-only nominal connectivity/clearance, not full-board DRC or return qualification.','Old-old violations remain hazards; filled planes removed from graph, not inherited.','New 16 through-via antipad area measured against historical fill only; fresh fill and core/neck tests mandatory.','Changed-footprint bodies/installation mechanical envelope remains separate from copper screening.']}
(D/'recovery_plan.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['original_objects','target_objects','new_conflict_object_count','original_violation_track_object_count','candidate_object_count','whole_track_net_candidates']},indent=2));print('input hash unchanged',sha(S),sha(N))
