#!/usr/bin/python3
"""Read actual native XML/PCB. Validate source delta, all pads, real tracks/vias/filled-zone contacts."""
from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,math,hashlib
D=Path(__file__).resolve().parents[1];base=D.parents[2]/'smart_pen_rebuild_20261028/hardware/power_core/power_core_NOFAB.xml'
# Resolve baseline from persistent scratch, never regenerate/fake yesterday files.
base=D/'source_baseline.xml'
t=E.parse(D/'power_core_NOFAB.xml');old=E.parse(base);b=p.LoadBoard(str(D/'power_core_NOFAB.kicad_pcb'));checks=[]
def check(ok,msg):checks.append({'check':msg,'pass':bool(ok)});assert ok,msg
def nodes(tree):return {(a.attrib['ref'],a.attrib['pin']):n.attrib['name'].lstrip('/') for n in tree.findall('./nets/net') for a in n}
nn=nodes(t);oo=nodes(old);extra={('J2','1'):'VBUS_5V',('J2','2'):'GND',('J3','1'):'3V3_AON',('J3','2'):'GND',('J4','1'):'PACK_PLUS_PROTECTED',('J4','2'):'GND',('J5','1'):'USB_EN1',('J5','2'):'USB_EN2',('J5','3'):'CE_PERMISSION_EXTERNAL',('J5','4'):'GND'}
for k,val in oo.items():check(nn[k]==('CE_PERMISSION_EXTERNAL' if k==('JP1','2') else val),'baseline endpoint '+'.'.join(k))
check(set(nn)-set(oo)==set(extra),'only ten additional interface pins')
for k,val in extra.items():check(nn[k]==val,'new interface '+'.'.join(k))
co={c.attrib['ref']:c for c in old.findall('./components/comp')};cn={c.attrib['ref']:c for c in t.findall('./components/comp')}
for r,c in co.items():check(cn[r].findtext('value')==('XFL4015-471MEC 0.47uH' if r=='L1' else c.findtext('value')),'source value '+r)
check(cn['JP1'].find("property[@name='dnp']") is not None,'commissioning link true DNP')
for f in b.GetFootprints():
 r=f.GetReference();check(f.GetValue()==cn[r].findtext('value'),'PCB value '+r);check(f.IsDNP()==(cn[r].find("property[@name='dnp']") is not None),'PCB DNP '+r)
 for a in f.Pads():check(a.GetNetname().lstrip('/')==nn[r,a.GetNumber()],'PCB pad '+r+'.'+a.GetNumber())
# Independent graph: pad copper hit-tests, track centreline containment, through vias,
# and ACTUAL filled polygons. No ratsnest or design-route script used.
results=[];plane_checks=[]
for name in sorted(set(nn.values())):
 pads=[(f.GetReference(),a) for f in b.GetFootprints() for a in f.Pads() if a.GetNetname().lstrip('/')==name]
 if len(pads)<2:continue
 tracks=[q for q in b.GetTracks() if q.GetNetname().lstrip('/')==name and not isinstance(q,p.PCB_VIA)];vias=[q for q in b.GetTracks() if q.GetNetname().lstrip('/')==name and isinstance(q,p.PCB_VIA)];points=set();pp={}
 for r,a in pads:
  q=a.GetPosition();k=(p.F_Cu,q.x,q.y);points.add(k);pp[r,a.GetNumber()]=k
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
  poly=z.GetFilledPolysList(z.GetLayer());check(poly.OutlineCount()==1,'single actual filled '+name+' '+b.GetLayerName(z.GetLayer()))
  ids=[i for i,(l,x,y) in enumerate(pts) if l==z.GetLayer() and poly.Contains(p.VECTOR2I(x,y))];join(ids)
  plane_checks.append({'net':name,'layer':b.GetLayerName(z.GetLayer()),'actual_filled_polygons':poly.OutlineCount(),'area_mm2':poly.Area()/1e12,'actual_contact_points':len(ids)})
 roots={root(pts.index(k)) for k in pp.values()};check(len(roots)==1,'actual copper contacts connected '+name)
 results.append({'net':name,'pad_nodes':sorted(r+'.'+n for r,n in pp),'connected':True,'track_segments':len(tracks),'vias':len(vias)})
# Ground plane exclusion and genuine contacts at all drilled vias.
g=next(z.GetFilledPolysList(p.In1_Cu) for z in b.Zones() if z.GetLayer()==p.In1_Cu)
for q in b.GetTracks():
 if isinstance(q,p.PCB_VIA):check(g.Contains(q.GetPosition())==(q.GetNetname().lstrip('/')=='GND'),'actual In1 via contact/antipad '+str(q.m_Uuid))
pro=json.loads((D/'power_core_NOFAB.kicad_pro').read_text());ds=pro['board']['design_settings'];check(not ds.get('drc_exclusions'),'no DRC exclusions');check(ds['rules']['min_copper_edge_clearance']==.5,'0.5mm board edge rule unchanged')
widths={};powerstats={}
for q in b.GetTracks():
 if isinstance(q,p.PCB_VIA):continue
 n=q.GetNetname().lstrip('/');w=p.ToMM(q.GetWidth());length=p.ToMM(q.GetLength());widths[str(w)]=widths.get(str(w),0)+length
 if n in ['VBUS_5V','SYS_RAW','PACK_PLUS_PROTECTED','3V3_AON','SW_L1','SW_L2']:
  powerstats.setdefault(n,[]).append({'width_mm':w,'length_mm':length,'layer':b.GetLayerName(q.GetLayer())})
(D/'design_checks.json').write_text(json.dumps({'status':'Connectivity/geometry checks only; NOFAB, no battery charging permission','baseline_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'pcb_sha256':hashlib.sha256((D/'power_core_NOFAB.kicad_pcb').read_bytes()).hexdigest(),'assertions':checks,'actual_copper_graph':results,'filled_plane_contacts':plane_checks,'trace_length_by_width_mm':widths,'power_trace_segments':powerstats},indent=2));print('PASS',len(checks),'checks, actual copper graph',len(results),'multi-pad nets; source delta and all pads verified')
