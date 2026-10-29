#!/usr/bin/env python3
import os,pathlib,hashlib,json,heapq,math
os.environ['XDG_CONFIG_HOME']='/tmp/pen-rf-check/config';os.environ['XDG_CACHE_HOME']='/tmp/pen-rf-check/cache';os.environ['XDG_DATA_HOME']='/tmp/pen-rf-check/data'
import pcbnew as p
D=pathlib.Path(__file__).resolve().parent;src=D/'source_before.kicad_pcb'
if hashlib.sha256(src.read_bytes()).hexdigest()!='af7ea5488de178176dded49c9130ccca6c76334c7df96e80d869338406449714':raise RuntimeError('Source changed')
import sys,copy
sys.path.insert(0,str(D/'tools'));from sexpr import parse,child,children,prop,q,val,dump
raw=parse(src.read_text());lib=parse(pathlib.Path('/usr/share/kicad/footprints/Capacitor_SMD.pretty/C_0402_1005Metric.kicad_mod').read_text())
for f in children(raw,'footprint'):
 name=val(prop(f,'Reference')[2])
 if name not in ['C106','C107']:continue
 new=copy.deepcopy(lib);new[1]=q('Capacitor_SMD:C_0402_1005Metric')
 for key in ['version','generator','at','uuid','path','sheetname','sheetfile','attr']:
  for old in children(new,key):new.remove(old)
  if child(f,key)is not None and key not in ['version','generator']:new.append(copy.deepcopy(child(f,key)))
 prop(new,'Reference')[2]=q(name);prop(new,'Value')[2]=prop(f,'Value')[2]
 for pad in children(new,'pad'):
  old=next(x for x in children(f,'pad')if x[1]==pad[1])
  for key in ['net','uuid','pinfunction','pintype']:
   if child(old,key)is not None:pad.append(copy.deepcopy(child(old,key)))
 raw[raw.index(f)]=new
(D/'prepared_source.kicad_pcb').write_text('('+raw[0]+'\n'+'\n'.join(dump(c) if isinstance(c,list) else c for c in raw[1:])+')\n')
import shutil
shutil.copyfile(src.with_suffix('.kicad_pro'),D/'prepared_source.kicad_pro')
shutil.copyfile(src.with_suffix('.kicad_pro'),D/'blocked_placement.kicad_pro')
b=p.LoadBoard(str(D/'prepared_source.kicad_pcb'));F={f.GetReference():f for f in b.GetFootprints()}
def xy(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def track(a,c,net,w=.1814):
 t=p.PCB_TRACK(b);t.SetStart(xy(*a));t.SetEnd(xy(*c));t.SetWidth(p.FromMM(w));t.SetLayer(p.F_Cu);t.SetNet(b.FindNet(net));b.Add(t);return t
for name,pos,ang in [('C106',(6.65,1.38),270),('L101',(8.05,.9),0),('C107',(9.5,1.38),270)]:F[name].SetOrientationDegrees(ang);F[name].SetPosition(xy(*pos))
# Remove old C107 ground stub ONLY; original components no longer use this endpoint.
remove={'f6a948ca-6e08-47a7-ab7a-ce3f9ceb3a3e','086214b7-55ea-4cb7-8a24-8ef6b3dc69cb'}
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString()in remove:b.RemoveNative(t)
# Keep GPIO45 pull-down on front; relocate toward its existing MCU-side via.
F['R104'].SetOrientationDegrees(0);F['R104'].SetPosition(xy(3.5,1.7))
keepstrap={'2210cdef-cbd7-49ce-9f85-6d753d42d806','e71f2bf8-e0af-4fde-a7aa-d5b9c22a44b9'}
removegnd={'f7f1df25','b115cf15','dbfa48b9','d8d8ed0b','b0f398c0','f44ae591','e60b94a7','da887086','54ade1a5','9cd67432','fd810108','d94bcce9','e6c27bec','ed0dcdf2','e71d47f2','af21d86e','8f03e545','554e0938','ed7d13d5','c4ebfc20','45b3c2b6','478e2b92','2f8e1a6c','79d10b77','a9b69c41','20fbd6a8','0c5c971e','2acf399a-c8aa-4162-978a-1b4bf85cd1a8','ed129594','ba4b737f-41f3-4412-b599-71e801ae5ff0','9f2bd49d'}
for t in list(b.GetTracks()):
 if (t.GetNetname()=='STRAP_GPIO45' and t.m_Uuid.AsString()not in keepstrap)or any(t.m_Uuid.AsString().startswith(u)for u in removegnd):b.RemoveNative(t)
track((2.675,1.7),(3.1,2.7),'STRAP_GPIO45',.15)
track((4.325,1.7),(4.1,1),'GND',.25)
for name in ['C106','C107']:F[name].Reference().SetLayer(p.F_Fab)
# Move only a low-speed CAM_SDA transition to widen the return-plane corridor.
for t in b.GetTracks():
 if t.GetNetname()!='CAM_SDA':continue
 if isinstance(t,p.PCB_VIA):
  if t.GetPosition()==xy(2.3,5.05):t.SetPosition(xy(2.65,5.25))
 else:
  if t.GetStart()==xy(2.3,5.05):t.SetStart(xy(2.65,5.25))
  if t.GetEnd()==xy(2.3,5.05):t.SetEnd(xy(2.65,5.25))
for zone in list(b.Zones()):
 if not zone.GetIsRuleArea() and zone.GetLayer()==p.F_Cu and zone.GetNetname()=='GND':b.RemoveNative(zone)
# Native rule: full antenna area still forbids all planes and vias. Tracks
# are forbidden by a second, notched polygon except for explicit feed aperture.
for z in b.Zones():
 if z.GetIsRuleArea():z.SetDoNotAllowTracks(False)
 if z.GetNetname()=='GND' and z.GetLayer()==p.In1_Cu:
  o=z.Outline();o.RemoveAllContours();o.NewOutline()
  for a in [(.3,-6.25),(5.25,-6.25),(5.25,0),(11.7,0),(11.7,94.7),(.3,94.7)]:o.Append(*[p.FromMM(q) for q in a])
z=p.ZONE(b);z.SetIsRuleArea(True);z.SetZoneName('RF_CLEARANCE_TRACKS_EXCEPT_TERMINAL');z.SetLayerSet(b.GetEnabledLayers() & p.LSET.AllCuMask() if False else next(z for z in b.Zones() if z.GetIsRuleArea()).GetLayerSet());z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
o=z.Outline();o.NewOutline()
for a in [(5.5,-6.5),(12,-6.5),(12,0),(9.61,0),(9.61,-2),(9.39,-2),(9.39,0),(5.5,0)]:o.Append(*[p.FromMM(q)for q in a])
b.Add(z)
# Local shunt returns use existing ground vias; no unreviewed through-via shorts.
track((6.65,1.86),(7.6,2.1),'GND',.25)
v=p.PCB_VIA(b);v.SetPosition(xy(7.6,2.1));v.SetFrontWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetViaType(p.VIATYPE_THROUGH);v.SetNet(b.FindNet('GND'));b.Add(v)
track((9.5,1.86),(9.275,3),'GND',.25)
track((6.65,.9),(7.565,.9),'RF_SIP');track((8.535,.9),(9.5,.9),'RF_ANT');track((9.5,.9),(9.5,0),'RF_ANT');track((9.5,0),(9.5,-1.9),'RF_ANT')
# Solve only RF_SIP pin-to-matching on F.Cu. Search is geometry proposal, not RF approval.
obs=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.IsOnLayer(p.F_Cu) and pad.GetNetname()!='RF_SIP':
   sh=p.SHAPE_POLY_SET();pad.TransformShapeToPolygon(sh,p.F_Cu,0,500,p.ERROR_OUTSIDE)
   if pad.GetNetname()=='GND' and sh.BBox().GetBottom()<p.FromMM(4.8):sh.Inflate(p.FromMM(.2),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
   obs.append(sh)
for t in b.GetTracks():
 if t.GetNetname()=='RF_SIP' or not (isinstance(t,p.PCB_VIA) or t.GetLayer()==p.F_Cu):continue
 sh=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(sh,p.F_Cu,0,500,p.ERROR_OUTSIDE)
 if t.GetNetname()=='GND' and sh.BBox().GetBottom()<p.FromMM(4.8):sh.Inflate(p.FromMM(.2),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 obs.append(sh)
p.ZONE_FILLER(b).Fill(b.Zones())
reference=p.SHAPE_POLY_SET()
for zone in b.Zones():
 if not zone.GetIsRuleArea()and zone.GetNetname()=='GND'and zone.GetLayer()==p.In1_Cu:reference.BooleanAdd(zone.GetFilledPolysList(p.In1_Cu))
reference.Deflate(p.FromMM(.35+.1814/2),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
def reference_safe(v):
 return reference.Contains(v) or math.hypot(v.x-p.FromMM(2.575),v.y-p.FromMM(7.4))<=p.FromMM(.6)
# Grid .025 mm, clearance .15 mm plus half-width. Bound to original top area.
step=.025;start=(103,296);goal=(266,36);dirs=[(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)];cache={};clear=p.FromMM(.15+.1814/2)
boxes=[(q,q.BBox().GetLeft()-clear,q.BBox().GetTop()-clear,q.BBox().GetRight()+clear,q.BBox().GetBottom()+clear) for q in obs if q.BBox().GetTop()<p.FromMM(8)]
def free(pt):
 if pt not in cache:
  x,y=pt;v=xy(x*step,y*step)
  cache[pt]=(26<=x<=466 and 10<=y<=310 and reference_safe(v) and not any(q.Collide(v,clear) for q,x0,y0,x1,y1 in boxes if x0<=v.x<=x1 and y0<=v.y<=y1))
 return cache[pt]
q=[(0,0,start)];cost={start:0};prev={};found=False
while q:
 _,g,a=heapq.heappop(q)
 if g!=cost.get(a):continue
 if a==goal:found=True;break
 for dx,dy in dirs:
  c=(a[0]+dx,a[1]+dy)
  if not free(c) or (dx and dy and(not free((a[0]+dx,a[1]))or not free((a[0],a[1]+dy)))):continue
  ng=g+math.hypot(dx,dy)
  if ng<cost.get(c,1e99):cost[c]=ng;prev[c]=a;heapq.heappush(q,(ng+math.hypot(c[0]-goal[0],c[1]-goal[1]),ng,c))
if not found:
 for xx,yy in [(2,4.5),(2,4.8),(1.9,4.7),(2.1,4.5)]:
  vv=xy(xx,yy);print('BLOCK',xx,yy,[(i,q.BBox().GetLeft()/1e6,q.BBox().GetTop()/1e6,q.BBox().GetRight()/1e6,q.BBox().GetBottom()/1e6)for i,q in enumerate(obs)if q.Collide(vv,clear)])
 svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 8" width="1200" height="800">']
 for xx in range(26,466,4):
  for yy in range(10,310,4):
   color='green' if (xx,yy)in cost else ('white'if free((xx,yy))else'red')
   svg.append(f'<rect x="{xx*step}" y="{yy*step}" width=".09" height=".09" fill="{color}"/>')
 svg.append('</svg>');(D/'search_grid.svg').write_text(''.join(svg))
 p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'blocked_placement.kicad_pcb'),b)
 (D/'search_failure.json').write_text(json.dumps(dict(states=len(cost),goal_free=free(goal),start_free=free(start),closest=min(cost,key=lambda a:math.dist(a,goal)),reachable_bounds=[min(a[i]for a in cost)*step for i in [0,1]]+[max(a[i]for a in cost)*step for i in [0,1]]),indent=2))
 raise RuntimeError('No F.Cu route, states '+str(len(cost)))
path=[goal]
while path[-1]!=start:path.append(prev[path[-1]])
path.reverse();simpl=[path[0]]
for i in range(1,len(path)-1):
 if (path[i][0]-path[i-1][0],path[i][1]-path[i-1][1])!=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1]):simpl.append(path[i])
simpl.append(path[-1]);pts=[(x*step,y*step)for x,y in simpl]
# Remove quantization stair-steps using exact finite-copper line collision checks.
sm=[pts[0]];ii=0
while ii<len(pts)-1:
 jj=len(pts)-1
 while jj>ii+1:
  seg=p.SEG(xy(*pts[ii]),xy(*pts[jj]))
  if not any(sh.Collide(seg,clear) for sh in obs) and all(reference_safe(xy(pts[ii][0]+(pts[jj][0]-pts[ii][0])*kk/500,pts[ii][1]+(pts[jj][1]-pts[ii][1])*kk/500))for kk in range(501)):break
  jj-=1
 sm.append(pts[jj]);ii=jj
pts=sm
for a,c in zip(pts,pts[1:]):track(a,c,'RF_SIP')
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'mainboard_revD.kicad_pcb'),b)
(D/'route_proposal.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),points_mm=pts,rf_sip_route_mm=sum(math.dist(a,c)for a,c in zip(pts,pts[1:])),width_mm=.1814,terminal_unreferenced_mm=1.9,status='CONDITIONAL_NOFAB'),indent=2))
print('route',pts)
