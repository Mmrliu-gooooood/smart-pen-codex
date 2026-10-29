from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,math,hashlib
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'power_integrated_study.kicad_pcb'));t=E.parse(D/'power_integrated_study.xml');checks=[]
baseboard=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));corerefs={f.GetReference() for f in baseboard.GetFootprints()}
nn={(a.attrib['ref'],a.attrib['pin']):n.attrib['name'].lstrip('/') for n in t.findall('./nets/net') for a in n}
def check(ok,msg):checks.append({'check':msg,'pass':bool(ok)})
# Independent graph: pad copper hit-tests, track centreline containment, through vias,
# and ACTUAL filled polygons. No ratsnest or design-route script used.
results=[];plane_checks=[]
baseboard=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));corerefs={f.GetReference() for f in baseboard.GetFootprints()}
for name in sorted(set(nn.values())):
 pads=[(f.GetReference(),a) for f in b.GetFootprints() for a in f.Pads() if a.GetNetname().lstrip('/')==name]
 if len(pads)<2:continue
 tracks=[q for q in b.GetTracks() if q.GetNetname().lstrip('/')==name and not isinstance(q,p.PCB_VIA)];vias=[q for q in b.GetTracks() if q.GetNetname().lstrip('/')==name and isinstance(q,p.PCB_VIA)];points=set();pp={}
 for r,a in pads:
  q=a.GetPosition();k=(p.F_Cu if a.IsOnLayer(p.F_Cu) else p.B_Cu,q.x,q.y);points.add(k);pp[r,a.GetNumber()]=k
 for q in tracks:
  for pt in [q.GetStart(),q.GetEnd()]:points.add((q.GetLayer(),pt.x,pt.y))
 for q in vias:
  for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:points.add((l,q.GetPosition().x,q.GetPosition().y))
 pts=list(points);parent=list(range(len(pts)))
 def root(i):
  while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def join(ids):
  if ids:
   for i in ids[1:]:parent[root(i)]=root(ids[0])
 for r,a in pads:join([i for i,(l,x,y) in enumerate(pts) if a.IsOnLayer(l) and a.HitTest(p.VECTOR2I(x,y))])
 for q in tracks:
  a=q.GetStart();z=q.GetEnd();dx=z.x-a.x;dy=z.y-a.y;ll=dx*dx+dy*dy;ids=[]
  for i,(l,x,y) in enumerate(pts):
   if l!=q.GetLayer():continue
   u=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/ll));distance=math.hypot(x-(a.x+u*dx),y-(a.y+u*dy))
   if distance<=2:ids.append(i) # exact endpoint/centreline; does not invent fringe contact
  join(ids)
 for q in vias:join([i for i,(l,x,y) in enumerate(pts) if x==q.GetPosition().x and y==q.GetPosition().y])
 for z in b.Zones():
  if z.GetNetname().lstrip('/')!=name:continue
  poly=z.GetFilledPolysList(z.GetLayer());check(poly.OutlineCount()>=1,'actual filled '+name+' '+b.GetLayerName(z.GetLayer()))
  ids=[]
  for oi in range(poly.OutlineCount()):
   sub=[i for i,(l,x,y) in enumerate(pts) if l==z.GetLayer() and poly.Contains(p.VECTOR2I(x,y),oi)];join(sub);ids.extend(sub)
  plane_checks.append({'net':name,'layer':b.GetLayerName(z.GetLayer()),'actual_filled_polygons':poly.OutlineCount(),'area_mm2':poly.Area()/1e12,'actual_contact_points':len(ids)})
 roots={root(pts.index(k)) for k in pp.values()};check(len(roots)==1,'actual copper contacts connected '+name)
 results.append({'net':name,'pad_nodes':sorted(r+'.'+n for r,n in pp),'connected':len(roots)==1,'core_pad_subset_connected':len({root(pts.index(k)) for (r,pin),k in pp.items() if r in corerefs})<=1,'track_segments':len(tracks),'vias':len(vias)})

(D/'copper_graph.json').write_text(json.dumps({'status':'PASS' if all(c['pass'] for c in checks) else 'INCOMPLETE','actual_copper_graph':results,'plane_contacts':plane_checks,'checks':checks,'pcb_sha256':hashlib.sha256((D/'power_integrated_study.kicad_pcb').read_bytes()).hexdigest()},indent=2));print('Connected',sum(x['connected'] for x in results),'of',len(results),'physical multi-pad nets')
