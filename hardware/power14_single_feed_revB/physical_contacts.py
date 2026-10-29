"""Read-only physical copper graph using native filled islands and copper shapes.
Polygon approximation <=0.5um. Via drills removed explicitly. No same-net island union.
"""
import pcbnew as p,math,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1];C=D;fn=C/'power_integrated_study.kicad_pcb'
if hashlib.sha256(fn.read_bytes()).hexdigest()!='94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc':raise RuntimeError('Frozen candidate changed')
b=p.LoadBoard(str(fn));orig=p.LoadBoard(str(ROOT/'hardware/power_core_layout_candidate/power_core_NOFAB.kicad_pcb'))
oldids={x.m_Uuid.AsString() for x in orig.GetTracks()};oldrefs={f.GetReference() for f in orig.GetFootprints()}
LAYERS=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu];nodes=[]
def polygon(obj,l):
 poly=p.SHAPE_POLY_SET();obj.TransformShapeToPolygon(poly,l,0,500,p.ERROR_INSIDE)
 if isinstance(obj,p.PCB_VIA):
  rad=obj.GetDrillValue()/2;pos=obj.GetPosition();hole=p.SHAPE_POLY_SET();h=hole.NewOutline()
  for i in range(192):hole.Append(round(pos.x+rad*math.cos(i*2*math.pi/192)),round(pos.y+rad*math.sin(i*2*math.pi/192)),h)
  poly.BooleanSubtract(hole)
 elif isinstance(obj,p.PAD) and obj.HasHole():
  hole=p.SHAPE_POLY_SET();obj.TransformHoleToPolygon(hole,0,500,p.ERROR_OUTSIDE);poly.BooleanSubtract(hole)
 return poly
for f in b.GetFootprints():
 for a in f.Pads():
  if not a.GetNetname():continue
  shapes={l:polygon(a,l) for l in LAYERS if a.IsOnLayer(l)}
  nodes.append(dict(id=f.GetReference()+'.'+a.GetNumber(),net=a.GetNetname(),kind='pad',old=f.GetReference() in oldrefs,shapes=shapes))
for t in b.GetTracks():
 ls=LAYERS if isinstance(t,p.PCB_VIA) else [t.GetLayer()]
 nodes.append(dict(id=t.m_Uuid.AsString(),net=t.GetNetname(),kind='via' if isinstance(t,p.PCB_VIA) else 'track',old=t.m_Uuid.AsString() in oldids,shapes={l:polygon(t,l) for l in ls}))
for z in b.Zones():
 polys=z.GetFilledPolysList(z.GetLayer())
 for i in range(polys.OutlineCount()):nodes.append(dict(id=z.m_Uuid.AsString()+'/'+str(i),net=z.GetNetname(),kind='fill',old=False,shapes={z.GetLayer():polys.UnitSet(i)}))
parent=list(range(len(nodes)))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
edges=[]
for i,a in enumerate(nodes):
 for j in range(i):
  z=nodes[j]
  if z['net']!=a['net']:continue
  for l in a['shapes'].keys()&z['shapes'].keys():
   aa=a['shapes'][l];zz=z['shapes'][l]
   if not aa.BBox().Intersects(zz.BBox()):continue
   inter=p.SHAPE_POLY_SET();inter.BooleanIntersection(aa,zz)
   if inter.Area()>1:
    parent[root(i)]=root(j);edges.append((i,j,l,inter));break
nets=[]
for name in sorted({n['net'] for n in nodes}):
 pads=[i for i,n in enumerate(nodes) if n['net']==name and n['kind']=='pad']
 if len(pads)>1:nets.append({'net':name,'pads':len(pads),'components':len({root(i) for i in pads}),'connected':len({root(i) for i in pads})==1})
# Do all physical contacts between added VBUS copper and original core copper occur
# inside C1.1? This catches finite-width fringe contacts missed by centerline tests.
anchor=next(n for n in nodes if n['id']=='C1.1')['shapes'][p.F_Cu]
contacts=[]
for i,j,l,inter in edges:
 a,z=nodes[i],nodes[j]
 if a['net']!='VBUS_5V' or a['old']==z['old']:continue
 outside=p.SHAPE_POLY_SET(inter);outside.BooleanSubtract(anchor)
 contacts.append({'a':a['id'],'b':z['id'],'layer':b.GetLayerName(l),'intersection_mm2':inter.Area()/1e12,'outside_C1_pad_mm2':outside.Area()/1e12})
result={'pcb_sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'method':'Native track/pad polygon expansion (0.5um inward approximation), explicit via drill removal, each actual filled island independent node; positive-area same-layer copper contact. Same-net labels alone do not join. Not electromagnetic simulation.','node_count':len(nodes),'physical_edges':len(edges),'nets':nets,'VBUS_core_added_contacts':contacts,'all_core_added_contacts_confined_to_C1_pad':all(q['outside_C1_pad_mm2']<1e-10 for q in contacts)}
(D/'physical_contacts.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'connected_nets':sum(q['connected'] for q in nets),'total_nets':len(nets),'contacts':contacts,'single_C1_only':result['all_core_added_contacts_confined_to_C1_pad']},indent=2))
# Render actual F.Cu polygon geometry around the unexpected annular contacts.
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="6.1 4.0 2.7 3.4" width="810" height="1020"><rect x="6.1" y="4" width="2.7" height="3.4" fill="white"/>']
def path(poly):
 parts=[]
 for oi in range(poly.OutlineCount()):
  chains=[poly.COutline(oi)]+[poly.CHole(oi,h) for h in range(poly.HoleCount(oi))]
  for chain in chains:
   pts=[chain.CPoint(i) for i in range(chain.PointCount())]
   if pts:parts.append('M'+' L'.join(f'{q.x/1e6},{q.y/1e6}' for q in pts)+' Z')
 return ' '.join(parts)
for n in nodes:
 if n['net']=='VBUS_5V' and p.F_Cu in n['shapes']:
  color='#2675c9' if n['old'] else '#36a867'
  svg.append(f'<path d="{path(n["shapes"][p.F_Cu])}" fill="{color}" fill-rule="evenodd" opacity="0.6"/>')
for i,j,l,inter in edges:
 a,z=nodes[i],nodes[j]
 if a['net']=='VBUS_5V' and a['old']!=z['old']:
  outside=p.SHAPE_POLY_SET(inter);outside.BooleanSubtract(anchor)
  if outside.Area()>1:svg.append(f'<path d="{path(outside)}" fill="#e62c2c" fill-rule="evenodd"/>')
svg.append('<text x="6.2" y="4.18" font-size="0.09">Blue: core / Green: thermal / Red: unintended contact</text>')
svg.append('<text x="6.2" y="7.25" font-size="0.09">Actual F.Cu polygon geometry; units mm. NOFAB</text></svg>')
(D/'unintended_contacts.svg').write_text(''.join(svg))
if not all(q['connected'] for q in nets):raise RuntimeError('Physical net disconnected')
if not result['all_core_added_contacts_confined_to_C1_pad']:raise RuntimeError('Extra physical core/thermal contact outside C1')
