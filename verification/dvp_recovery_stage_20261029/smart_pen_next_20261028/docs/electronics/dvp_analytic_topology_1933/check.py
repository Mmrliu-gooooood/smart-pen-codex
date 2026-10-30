from pathlib import Path
import os
os.environ["XDG_CONFIG_HOME"]="/tmp/pen-analytic"
import pcbnew as p,json,hashlib,math
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/dvp_rotated_group_placement_1835/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S)); rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows']; routes=[];objs=[]
V=lambda xy:p.VECTOR2I(*(round(x*1e6) for x in xy))
def line(net,layer,points):
 for a,c in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(V(a));t.SetEnd(V(c));t.SetWidth(150000);t.SetLayer(layer);t.SetNetCode(b.GetNetcodeFromNetname(net));objs.append((net,t))
def via(net,xy):
 t=p.PCB_VIA(b);t.SetPosition(V(xy));t.SetWidth(p.F_Cu,450000);t.SetDrill(200000);t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNetCode(b.GetNetcodeFromNetname(net));objs.append((net,t))
for i,r in enumerate(rows):
 n=r['net'];x,y=r['rotated_unselected_xy'];hx,hy=r['J202_xy']; layer=p.F_Cu if i<4 else p.In3_Cu if i<8 else p.B_Cu; lane=13.5-.3*(i%4); startY=38.0+.65*(i%4) if i<8 else y+1+.65*((i-8)%3); headY=88.6-.65*i if i<8 else 83.4-.65*(i-8)
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
   for l in [p.F_Cu,p.In3_Cu,p.B_Cu]:
    if t.IsOnLayer(l) and pad.IsOnLayer(l) and overlap(t,pad,l):pads.append(dict(route=n,object_index=idx,ref=f.GetReference(),pad=pad.GetNumber(),net=pad.GetNetname(),layer=b.GetLayerName(l)))
 for j,(nn,tt) in enumerate(objs[:idx]):
  if nn==n:continue
  for l in [p.F_Cu,p.In3_Cu,p.B_Cu]:
   if t.IsOnLayer(l) and tt.IsOnLayer(l) and overlap(t,tt,l):pair.append(dict(a=n,b=nn,i=idx,j=j,layer=b.GetLayerName(l)))
out=dict(source_sha=hashlib.sha256(S.read_bytes()).hexdigest(),scope='analytical topology proposal only; no native board changed; power/return not assessed',routes=routes,pad_clearance_conflicts=pads,new_route_pair_conflicts=pair,objects=len(objs),geometry=[dict(net=n,type='via' if isinstance(t,p.PCB_VIA) else 'track',start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],layer='through' if isinstance(t,p.PCB_VIA) else b.GetLayerName(t.GetLayer()),width_mm=.45 if isinstance(t,p.PCB_VIA) else .15) for n,t in objs])
(D/'result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'objects':len(objs),'pad_conflicts':pads,'pair_conflicts':pair},indent=2))
