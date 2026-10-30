from pathlib import Path
import os,json,math,hashlib,heapq,xml.etree.ElementTree as E
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));old=p.LoadBoard(str(D.parent/'gate_input_local_routing/mainboard_revD.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()};xy=lambda q:(q.x/1e6,q.y/1e6)
S=D.parent/'gate_supply_native_mpn_source';contract=json.loads((S/'native_mpn_contract.json').read_text());cs={c.get('ref'):c for c in E.parse(D/'fresh.xml').findall('./components/comp')}
for r,v in contract['parts'].items():
 fields={f.get('name'):f.text for f in cs[r].findall('./fields/field')}
 for key,k in [('Manufacturer','manufacturer'),('MPN','mpn'),('ProcurementStatus','status')]:
  if fields.get(key)!=v[k]:raise RuntimeError('MPN source mismatch '+r)
for f in (S/'mainboard_projection').rglob('*.kicad_sch'):
 if (D/f.relative_to(S/'mainboard_projection')).read_bytes()!=f.read_bytes():raise RuntimeError('Source sheet changed '+str(f))
# Metric centreline graph: split at exact segment endpoints/vias and at pad projections.
# Zero cost across pad copper and via barrel; filled planes not modelled as geometric paths.
def pad(label):
 r,n=label.split('.');return next(q for q in fps[r].Pads()if q.GetNumber()==n)
def path_between(a,z=None,to_via=False):
 startpad=pad(a);net=startpad.GetNetname();ts=[t for t in b.GetTracks()if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)];vs=[t for t in b.GetTracks()if t.GetNetname()==net and isinstance(t,p.PCB_VIA)]
 pads=[startpad]+([pad(z)]if z else[]);pts=set(xy(t.GetStart())for t in ts)|set(xy(t.GetEnd())for t in ts)|set(xy(t.GetPosition())for t in vs)
 def project(q,a,z):
  dx=z[0]-a[0];dy=z[1]-a[1];den=dx*dx+dy*dy;u=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den))if den else 0
  return(a[0]+u*dx,a[1]+u*dy)
 for pp in pads:
  for t in ts:
   if pp.IsOnLayer(t.GetLayer()):pts.add(project(xy(pp.GetPosition()),xy(t.GetStart()),xy(t.GetEnd())))
 graph={};edgeinfo={};radii={}
 def key(q,l):return(round(q[0],6),round(q[1],6),int(l))
 def edge(a,z,w,info):graph.setdefault(a,[]).append((z,w,info));graph.setdefault(z,[]).append((a,w,info))
 for t in ts:
  aa,zz=xy(t.GetStart()),xy(t.GetEnd());on=sorted((math.dist(aa,q),q)for q in pts if math.dist(q,project(q,aa,zz))<.000002)
  for (_,u),(_,v)in zip(on,on[1:]):
   ku,kv=key(u,t.GetLayer()),key(v,t.GetLayer());radii[ku]=max(radii.get(ku,0),t.GetWidth()//2);radii[kv]=max(radii.get(kv,0),t.GetWidth()//2);edge(ku,kv,math.dist(u,v),{'uuid':t.m_Uuid.AsString(),'width':p.ToMM(t.GetWidth()),'layer':b.GetLayerName(t.GetLayer())})
 goals=set()
 for v in vs:
  kk=[k for k in graph if math.dist(k[:2],xy(v.GetPosition()))<.000002]
  for k in kk[1:]:edge(kk[0],k,0,{'via':v.m_Uuid.AsString(),'xy':xy(v.GetPosition())})
  if to_via:goals.update(kk)
 def inside(pp,k):return pp.IsOnLayer(k[2])and pp.HitTest(p.VECTOR2I(round(k[0]*1e6),round(k[1]*1e6)),radii.get(k,0))
 starts=[k for k in graph if inside(startpad,k)]
 if z:goals={k for k in graph if inside(pad(z),k)}
 heap=[(0,k)for k in starts];heapq.heapify(heap);dist={k:0 for k in starts};prev={};end=None
 while heap:
  d,k=heapq.heappop(heap)
  if d>dist[k]:continue
  if k in goals:end=k;break
  for v,w,info in graph[k]:
   if d+w<dist.get(v,float('inf')):dist[v]=d+w;prev[v]=(k,info,w);heapq.heappush(heap,(d+w,v))
 if end is None:return {'from':a,'to':z or'first_via','explicit_track_path_found':False,'note':'May connect via filled plane; do not invent a path length.'}
 steps=[];q=end
 while q in prev:
  v,info,w=prev[q];steps.append(dict(info,a=v,z=q,length=w));q=v
 return {'from':a,'to':z or'first_via','explicit_track_path_found':True,'length_mm':dist[end],'end':end,'steps':steps[::-1]}
paths=[path_between(a,z)for a,z in [('C303.1','U301.4'),('R301.1','U301.3'),('R302.2','U301.3'),('R303.2','U301.5'),('R303.1','U301.6'),('U301.6','C302.1'),('U301.6','JP301.1'),('JP301.2','J301.1')]]+[path_between(a,to_via=True)for a in ['C303.2','C302.2','R301.2','U301.2']]
def lengths(board):
 out={}
 for t in board.GetTracks():
  if isinstance(t,p.PCB_VIA):continue
  out[t.GetNetname()]=out.get(t.GetNetname(),0)+math.dist(xy(t.GetStart()),xy(t.GetEnd()))
 return out
la,lb=lengths(old),lengths(b)
# CT-to-SCCB conservative exact segment centreline minimum minus both radii, same layer.
def segdist(a,z,c,d):
 def pointseg(q,a,z):
  dx=z[0]-a[0];dy=z[1]-a[1];den=dx*dx+dy*dy;u=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den))if den else 0
  return math.dist(q,(a[0]+u*dx,a[1]+u*dy))
 return min(pointseg(a,c,d),pointseg(z,c,d),pointseg(c,a,z),pointseg(d,a,z))
ct=[t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='CAM_CT'];near={}
for net in ['CAM_SCL','CAM_SDA','SENS_SCL','SENS_SDA']:
 pairs=[]
 for a in ct:
  for z in b.GetTracks():
   if isinstance(z,p.PCB_VIA)or z.GetNetname()!=net or z.GetLayer()!=a.GetLayer():continue
   gap=segdist(xy(a.GetStart()),xy(a.GetEnd()),xy(z.GetStart()),xy(z.GetEnd()))-(a.GetWidth()+z.GetWidth())/2e6;pairs.append((gap,a.m_Uuid.AsString(),z.m_Uuid.AsString(),b.GetLayerName(a.GetLayer())))
 near[net]=min(pairs)if pairs else None
result={'pcb_sha256':hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'source_manifest_sha256':hashlib.sha256((S/'manifest.json').read_bytes()).hexdigest(),'native_MPN_refs_verified':sorted(contract['parts']),'exact_source_sheets_match':True,'paths':paths,'CT_SCCB_same_layer_min_track_edge_gap_mm':near,'net_total_trace_length_delta_mm':{n:{'before':la.get(n,0),'after':lb.get(n,0),'delta':lb.get(n,0)-la.get(n,0)}for n in sorted(set(la)|set(lb))if abs(lb.get(n,0)-la.get(n,0))>.000001},'notes':['Path graph allows endpoint contact within pad plus trace half-width tolerance. Lengths exclude pad-current spreading, barrel length and filled-plane paths; not loop inductance. Finite polygon audit, not this metric graph, proves connectivity.','Same-layer CT track gaps do not prove crosstalk immunity; pad/via clearance is checked by native DRC and dynamic qualification remains open.','U204 independent 0.30 mm branch is a robustness change, not evidence the prior low-current 0.15 mm branch was unsafe.','No camera load, discharge thermal, effective CIN/CL, PI or IO-backfeed qualification. JP301 OPEN.']}
print(json.dumps(result,indent=2))
