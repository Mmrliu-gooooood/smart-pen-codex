from pathlib import Path
import os
os.environ["XDG_CONFIG_HOME"]="/tmp/pen-analytic"
import pcbnew as p,json,hashlib,math
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/dvp_rotated_group_placement_1835/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S)); rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows']; routes=[];objs=[]
fs={f.GetReference():f for f in b.GetFootprints()}; before={r:{'xy':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],'angle':f.GetOrientationDegrees(),'layer':b.GetLayerName(f.GetLayer()),'pads':sorted((q.GetNumber(),q.GetNetname()) for q in f.Pads())} for r,f in fs.items()}
for ref,x,y,flip in [('R225',4.5,43.3,True),('R226',7.5,44,True),('R227',10.5,44,True),('R206',9,47,True),('J105',2,77.5,False),('J107',2.7,84,True)]:
 f=fs[ref]
 if flip:f.Flip(f.GetPosition(),False)
 f.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)))
 if ref.startswith('R'):f.SetOrientationDegrees(0)
after={r:{'xy':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],'angle':f.GetOrientationDegrees(),'layer':b.GetLayerName(f.GetLayer()),'pads':sorted((q.GetNumber(),q.GetNetname()) for q in f.Pads())} for r,f in fs.items()}
for ref in before:
 if before[ref]['pads']!=after[ref]['pads']:raise RuntimeError('pad net drift')
if before['J103']!=after['J103'] or before['J106']!=after['J106']:raise RuntimeError('critical port moved')
changed={ref:{'before':before[ref],'after':after[ref]} for ref in before if before[ref]!=after[ref]}
(D/'placement_delta.json').write_text(json.dumps(changed,indent=2)+'\n')
V=lambda xy:p.VECTOR2I(*(round(x*1e6) for x in xy))
def line(net,layer,points):
 for a,c in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(V(a));t.SetEnd(V(c));t.SetWidth(150000);t.SetLayer(layer);t.SetNetCode(b.GetNetcodeFromNetname(net));objs.append((net,t))
def via(net,xy):
 t=p.PCB_VIA(b);t.SetPosition(V(xy));t.SetWidth(p.F_Cu,450000);t.SetDrill(200000);t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNetCode(b.GetNetcodeFromNetname(net));objs.append((net,t))
for i,r in enumerate(rows):
 n=r['net'];x,y=r['rotated_unselected_xy'];hx,hy=r['J202_xy']; layer=p.F_Cu if i<4 else p.In3_Cu if i<8 else p.B_Cu; lane=13.5-.3*(i%4); startY=38.0+.65*(i%4) if i<8 else [49.9,50.4,50.9,59.8625][i-8]; headY=89.35-.5*i if i<4 else 88.6-.65*i if i<8 else 83.4-.65*(i-8)
 if i>=4:
  line(n,p.F_Cu,[(x,y),(x,startY)]);via(n,(x,startY))
 else:line(n,p.F_Cu,[(x,y),(x,startY)])
 # clocks have common channel entry but stagger from distinct packages
 pts=[(x,startY),(lane,startY),(lane,headY),(hx,headY)]
 line(n,layer,pts)
 if i<8:via(n,(hx,headY))
 line(n,p.B_Cu,[(hx,headY),(hx,hy)])
 routes.append(dict(net=n,layer=b.GetLayerName(layer),source=[x,y],source_via=[x,startY] if i>=4 else None,trunk=lane,trunk_entry_y=startY,head_exit_y=headY,head_via=[hx,headY] if i<8 else None))
def shape(o,l,clear=0):
 q=p.SHAPE_POLY_SET();o.TransformShapeToPolygon(q,l,clear,50,p.ERROR_OUTSIDE);return q
def overlap(a,c,l):
 s=shape(a,l,150000);s.BooleanIntersection(shape(c,l));return s.Area()>1
pads=[];pair=[]
for idx,(n,t) in enumerate(objs):
 for f in b.GetFootprints():
  for pad in f.Pads():
   if pad.GetNetname()==n:continue
   for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
    if t.IsOnLayer(l) and pad.IsOnLayer(l) and overlap(t,pad,l):pads.append(dict(route=n,object_index=idx,ref=f.GetReference(),pad=pad.GetNumber(),net=pad.GetNetname(),layer=b.GetLayerName(l)))
 for j,(nn,tt) in enumerate(objs[:idx]):
  if nn==n:continue
  for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
   if t.IsOnLayer(l) and tt.IsOnLayer(l) and overlap(t,tt,l):pair.append(dict(a=n,b=nn,i=idx,j=j,layer=b.GetLayerName(l)))
courtyard=[]
for f in fs.values():f.BuildCourtyardCaches()
for i,f in enumerate(fs.values()):
 for g in list(fs.values())[:i]:
  if f.GetLayer()!=g.GetLayer():continue
  q=p.SHAPE_POLY_SET();q.BooleanIntersection(f.GetCourtyard(f.GetLayer()),g.GetCourtyard(g.GetLayer()))
  if q.Area()>1:courtyard.append(dict(a=f.GetReference(),b=g.GetReference(),overlap_mm2=q.Area()/1e12))
rule_conflicts=[]
for z in b.Zones():
 if not z.GetIsRuleArea():continue
 for idx,(n,t) in enumerate(objs):
  blocked=z.GetDoNotAllowVias() if isinstance(t,p.PCB_VIA) else z.GetDoNotAllowTracks()
  if not blocked:continue
  for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
   if z.IsOnLayer(l) and t.IsOnLayer(l):
    q=shape(t,l);q.BooleanIntersection(z.Outline())
    if q.Area()>1:rule_conflicts.append(dict(zone=z.GetZoneName(),object_index=idx,net=n,layer=b.GetLayerName(l)))
# Actual board polygon, not just x=0..14 rectangle.
outline=p.SHAPE_POLY_SET();ok=b.GetBoardPolygonOutlines(outline)
if not ok:raise RuntimeError('Cannot derive board outline')
edge_conflicts=[]
for idx,(n,t) in enumerate(objs):
 l=p.F_Cu if isinstance(t,p.PCB_VIA) else t.GetLayer();q=shape(t,l,250000);q.BooleanSubtract(outline)
 if q.Area()>1:edge_conflicts.append(dict(object_index=idx,net=n,outside_area_mm2=q.Area()/1e12))
placed_pad_conflicts=[]
for ref in changed:
 for pad in fs[ref].Pads():
  for other,f in fs.items():
   if other==ref:continue
   for q in f.Pads():
    for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
     if pad.IsOnLayer(l) and q.IsOnLayer(l) and overlap(pad,q,l):placed_pad_conflicts.append(dict(a=ref+'.'+pad.GetNumber(),b=other+'.'+q.GetNumber(),layer=b.GetLayerName(l)))
same_net_annulus_pad_overlap=[];drill_pad_overlap=[];existing_drilled_pads=[]
for f in fs.values():
 for pad in f.Pads():
  if pad.GetDrillSize().x or pad.GetDrillSize().y:existing_drilled_pads.append(f.GetReference()+'.'+pad.GetNumber())
for idx,(n,t) in enumerate(objs):
 if not isinstance(t,p.PCB_VIA):continue
 hole=p.PCB_VIA(b);hole.SetPosition(t.GetPosition());hole.SetWidth(p.F_Cu,200000);hole.SetDrill(200000);hole.SetViaType(p.VIATYPE_THROUGH);hole.SetLayerPair(p.F_Cu,p.B_Cu)
 for f in fs.values():
  for pad in f.Pads():
   for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
    if not pad.IsOnLayer(l):continue
    q=shape(hole,l);q.BooleanIntersection(shape(pad,l))
    if q.Area()>1:drill_pad_overlap.append(dict(via_index=idx,pad=f.GetReference()+'.'+pad.GetNumber(),net=pad.GetNetname(),layer=b.GetLayerName(l)))
    if pad.GetNetname()==n:
     q=shape(t,l);q.BooleanIntersection(shape(pad,l))
     if q.Area()>1:same_net_annulus_pad_overlap.append(dict(via_index=idx,pad=f.GetReference()+'.'+pad.GetNumber(),layer=b.GetLayerName(l)))
out=dict(same_net_annulus_pad_overlap=same_net_annulus_pad_overlap,drill_pad_overlap=drill_pad_overlap,existing_drilled_pads=existing_drilled_pads,via_inner_plane_antipads_and_return_unassessed=True,missing_native_courtyards=[f.GetReference() for f in fs.values() if f.GetCourtyard(f.GetLayer()).OutlineCount()==0], moved_pad_positions={ref:[dict(pin=q.GetNumber(),net=q.GetNetname(),xy=[q.GetPosition().x/1e6,q.GetPosition().y/1e6]) for q in fs[ref].Pads()] for ref in changed},rule_area_conflicts=rule_conflicts,native_outline_clearance_conflicts=edge_conflicts,placed_pad_clearance_conflicts=placed_pad_conflicts,courtyard_overlaps=courtyard,changed_refs=list(changed),critical_ports_unchanged=['J103','J106'],source_sha=hashlib.sha256(S.read_bytes()).hexdigest(),scope='analytical topology proposal only; no native board changed; power/return not assessed',routes=routes,pad_clearance_conflicts=pads,new_route_pair_conflicts=pair,objects=len(objs),geometry=[dict(net=n,type='via' if isinstance(t,p.PCB_VIA) else 'track',start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],layer='through' if isinstance(t,p.PCB_VIA) else b.GetLayerName(t.GetLayer()),width_mm=.45 if isinstance(t,p.PCB_VIA) else .15) for n,t in objs])
(D/'result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'objects':len(objs),'pad_conflicts':pads,'pair_conflicts':pair},indent=2))
