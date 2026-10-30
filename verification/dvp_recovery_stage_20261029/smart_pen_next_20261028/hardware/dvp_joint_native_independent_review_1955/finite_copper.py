import pcbnew as p, math
L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def shape(x,l):
 q=p.SHAPE_POLY_SET();x.TransformShapeToPolygon(q,l,0,250,p.ERROR_INSIDE)
 if isinstance(x,p.PCB_VIA):
  h=p.SHAPE_POLY_SET();h.NewOutline();c=x.GetPosition();r=x.GetDrillValue()/2
  for n in range(256):h.Append(round(c.x+r*math.cos(n*2*math.pi/256)),round(c.y+r*math.sin(n*2*math.pi/256)))
  q.BooleanSubtract(h)
 return q
def build(board):
 nets={}
 for f in board.GetFootprints():
  for x in f.Pads():nets.setdefault(x.GetNetname(),[]).append((f.GetReference()+'.'+x.GetNumber(),True,{l:shape(x,l)for l in L if x.IsOnLayer(l)}))
 for x in board.GetTracks():nets.setdefault(x.GetNetname(),[]).append((x.m_Uuid.AsString(),False,{l:shape(x,l)for l in L if x.IsOnLayer(l)}))
 for z in board.Zones():
  if z.GetIsRuleArea():continue
  for l in L:
   if not z.IsOnLayer(l):continue
   q=z.GetFilledPolysList(l)
   for i in range(q.OutlineCount()):nets.setdefault(z.GetNetname(),[]).append((z.m_Uuid.AsString()+'/'+str(l)+'/'+str(i),False,{l:q.UnitSet(i)}))
 return nets
def components(nodes):
 par=list(range(len(nodes)))
 def root(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 for i,(_,_,si) in enumerate(nodes):
  for j,(_,_,sj) in enumerate(nodes[:i]):
   for l in si.keys()&sj.keys():
    if not si[l].BBox().Intersects(sj[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(si[l],sj[l])
    if q.Area()>1:par[root(i)]=root(j);break
 out={}
 for i,(name,pad,_)in enumerate(nodes):
  if pad:out.setdefault(root(i),[]).append(name)
 return sorted(sorted(x)for x in out.values())

