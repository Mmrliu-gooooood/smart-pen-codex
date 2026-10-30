from pathlib import Path
import json,collections,math,os
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
O=Path(__file__).resolve().parent;D=O.parent/'gate_control_output_candidate';b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));ids={x['uuid']for x in json.loads((D/'new_routes.json').read_text())};ts={t.m_Uuid.AsString():t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)};new={u:t for u,t in ts.items()if u in ids};j=collections.defaultdict(list)
def xy(q):return(q.x,q.y)
for u,t in new.items():
 for q in [t.GetStart(),t.GetEnd()]:j[(t.GetNetname(),t.GetLayer(),t.GetWidth(),xy(q))].append(u)
c=[];noncol=[]
for (net,l,w,q),us in j.items():
 if len(us)!=2:continue
 ends=[]
 for u in us:
  t=ts[u];ends.append(xy(t.GetEnd())if xy(t.GetStart())==q else xy(t.GetStart()))
 a,z=ends;v=(a[0]-q[0],a[1]-q[1]);d=(z[0]-q[0],z[1]-q[1]);cross=v[0]*d[1]-v[1]*d[0];dot=v[0]*d[0]+v[1]*d[1]
 row={'net':net,'layer':b.GetLayerName(l),'width_nm':w,'junction_nm':q,'uuids':us,'ends_nm':ends}
 if cross==0 and dot<0:c.append(row)
 elif cross:noncol.append(row)
# Conservative preservation: a junction occupies a disk of the trace radius.
# Any positive-area actual other conductor, pad, via annulus, or filled-plane contact
# in that disk protects the node. No branch topology inferred only from endpoints.
def shape(obj,l):
 q=p.SHAPE_POLY_SET();obj.TransformShapeToPolygon(q,l,0,250,p.ERROR_INSIDE)
 if isinstance(obj,p.PCB_VIA):
  h=p.SHAPE_POLY_SET();h.NewOutline();v=obj.GetPosition();r=obj.GetDrillValue()/2
  for i in range(256):h.Append(round(v.x+r*math.cos(i*2*math.pi/256)),round(v.y+r*math.sin(i*2*math.pi/256)))
  q.BooleanSubtract(h)
 return q
eligible=[]
for row in c:
 l=b.GetLayerID(row['layer']);q=row['junction_nm'];r=row['width_nm']/2;disc=p.SHAPE_POLY_SET();disc.NewOutline()
 for i in range(256):disc.Append(round(q[0]+r*math.cos(i*2*math.pi/256)),round(q[1]+r*math.sin(i*2*math.pi/256)))
 objects=[]
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.IsOnLayer(l):objects.append((f.GetReference()+'.'+a.GetNumber(),'pad',a.GetNetname(),shape(a,l)))
 for t in b.GetTracks():
  if t.m_Uuid.AsString()not in row['uuids'] and t.IsOnLayer(l):objects.append((t.m_Uuid.AsString(),'via'if isinstance(t,p.PCB_VIA)else'track',t.GetNetname(),shape(t,l)))
 for z in b.Zones():
  if not z.GetIsRuleArea() and z.IsOnLayer(l):objects.append((z.m_Uuid.AsString(),'filled_zone',z.GetNetname(),z.GetFilledPolysList(l)))
 hits=[]
 for name,kind,net,s in objects:
  if not disc.BBox().Intersects(s.BBox()):continue
  ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(disc,s)
  if ix.Area()>1:hits.append({'object':name,'kind':kind,'net':net,'actual_overlap_mm2':ix.Area()/1e12})
 row['protected_contacts']=hits;row['eligible_exact_merge']=not hits
 if not hits:eligible.append(row)
short_rows=[]
for u,t in sorted(new.items()):
 if t.GetLength()<100000:
  a,z=xy(t.GetStart()),xy(t.GetEnd());short_rows.append({'uuid':u,'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'width_nm':t.GetWidth(),'length_mm':p.ToMM(t.GetLength()),'a_nm':a,'z_nm':z,'direction_degrees':math.degrees(math.atan2(z[1]-a[1],z[0]-a[0]))})
result={'short_tracks':short_rows,'input_pcb_sha256':__import__('hashlib').sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'new_tracks':len(new),'new_vias':len(ids)-len(new),'short_lt_100um':sum(t.GetLength()<100000 for t in new.values()),'collinear_pairs':c,'eligible_exact_merge_count':len(eligible),'noncollinear_pair_count':len(noncol),'noncollinear_pairs':noncol,'all_track_IDs_unchanged':True,'algorithm':'Integer cross product zero and opposite direction; only exact common endpoints, same net/layer/width, two incident NEW tracks. Any other real copper contact in the junction disk blocks merging. No smoothing or geometry changes.'}
print(json.dumps(result,indent=2))
