#!/usr/bin/env python3
import os,sys,json,math,hashlib,pathlib,xml.etree.ElementTree as ET
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=pathlib.Path(__file__).resolve().parent
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else D/'native_snapshot/mainboard_revD.kicad_pcb'
b=p.LoadBoard(str(path))
L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def require(x,msg):
 if not x:raise RuntimeError(msg)
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

nb=build(b); cb={n:components(v) for n,v in nb.items() if sum(x[1] for x in v)>1}
require(all(len(c)==1 for c in cb.values()),'Disconnected actual pads '+str({n:c for n,c in cb.items() if len(c)!=1}))
keep=p.SHAPE_POLY_SET();keep.NewOutline()
for x,y in [(5.5,-6.5),(12,-6.5),(12,0),(5.5,0)]:keep.Append(p.FromMM(x),p.FromMM(y))
viol=[]
for net,nodes in nb.items():
 for label,ispad,ss in nodes:
  for l,s in ss.items():
   q=p.SHAPE_POLY_SET();q.BooleanIntersection(s,keep)
   if q.Area()<=1:continue
   if ispad and label.startswith('AE101.'):continue
   # Only the explicitly classified antenna-terminal line may enter its radiator region.
   t=next((t for t in b.GetTracks()if t.m_Uuid.AsString()==label),None)
   allowed=t is not None and not isinstance(t,p.PCB_VIA)and net=='RF_ANT'and l==p.F_Cu and t.GetStart().x==p.FromMM(9.5)and t.GetEnd().x==p.FromMM(9.5)and min(t.GetStart().y,t.GetEnd().y)>=p.FromMM(-1.9)and max(t.GetStart().y,t.GetEnd().y)<=p.FromMM(.9)
   if not allowed:viol.append([net,label,l,q.Area()/1e12])
require(not viol,'Unexpected finite copper in keepout '+str(viol))
z=[z for z in b.Zones()if z.GetIsRuleArea()and 'RF_RADIATOR_CLEARANCE' in z.GetZoneName()];require(len(z)==1,'RF rule area missing')
require(set(z[0].GetLayerSet().Seq())==set(L)and z[0].GetDoNotAllowCopperPour()and z[0].GetDoNotAllowVias(),'Six-layer keepout incomplete')

fps={f.GetReference():f for f in b.GetFootprints()}
require(next(x for x in fps['AE101'].Pads() if x.GetNumber()=='2').GetNetname().startswith('unconnected-'),'Antenna NC grounded')
x=ET.parse(D/'fresh.xml'); cs={c.get('ref'):c for c in x.findall('./components/comp')}; ns={(n.get('ref'),n.get('pin')):net.get('name') for net in x.findall('./nets/net') for n in net}
require(len(cs)==83 and len(ns)==303 and len(fps)==79,'Source counts changed')
require(set(cs)-set(fps)=={'J103','J104','J105','J202'},'Missing handoff set changed')
for r,f in fps.items():
 c=cs[r]; require(f.GetValue()==c.findtext('value'),'Value mismatch '+r); require(f.GetFPIDAsString()==c.findtext('footprint'),'Footprint mismatch '+r)
 require(f.GetPath().AsString()=='/cebe562b-54ce-58d7-a4f0-094e70dd7d0a'+c.find('sheetpath').get('tstamps')+c.findtext('tstamps'),'Symbol path mismatch '+r)
 for pad in f.Pads():require(pad.GetNetname()==ns.get((r,pad.GetNumber()),''),'Actual pad net mismatch '+r)
ref=p.SHAPE_POLY_SET()
for z in b.Zones():
 if not z.GetIsRuleArea() and z.IsOnLayer(p.In1_Cu) and z.GetNetname()=='GND':ref.BooleanAdd(z.GetFilledPolysList(p.In1_Cu))
clip=p.SHAPE_POLY_SET();clip.NewOutline()
for xx,yy in [(0,0),(14,0),(14,95),(0,95)]:clip.Append(p.FromMM(xx),p.FromMM(yy))
metrics={}
for t in b.GetTracks():
 net=t.GetNetname()
 if net not in ['RF_SIP','RF_ANT','USB_DP_MCU','USB_DM_MCU','USB_DP','USB_DM','USB_EN1']:continue
 metrics.setdefault(net,{'length_mm':0,'vias':0,'layers':set()})
 if isinstance(t,p.PCB_VIA):metrics[net]['vias']+=1;require(net=='USB_EN1','RF/USB via');continue
 metrics[net]['length_mm']+=t.GetLength()/1e6;metrics[net]['layers'].add(b.GetLayerName(t.GetLayer()))
 if net=='USB_EN1':continue
 require(t.GetLayer()==p.F_Cu,'RF/USB wrong layer')
 if net.startswith('RF_'):require(abs(t.GetWidth()/1e6-.1814)<1e-8,'RF width mismatch')
 q=shape(t,p.F_Cu); clipped=p.SHAPE_POLY_SET();clipped.BooleanIntersection(q,clip);bad=p.SHAPE_POLY_SET();bad.BooleanSubtract(clipped,ref)
 require(bad.Area()<=1,'Missing actual reference '+net)
for v in metrics.values():v['layers']=sorted(v['layers'])
print(json.dumps({'status':'FINITE_COPPER_AND_SOURCE_ACCEPTED_NOFAB','pcb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'components':len(cs),'endpoints':len(ns),'nets':len(x.findall('./nets/net')),'footprints':len(fps),'pad_partitions':cb,'route_metrics':metrics},indent=2))
