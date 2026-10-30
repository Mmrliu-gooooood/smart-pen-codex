from pathlib import Path
import json,hashlib,collections,sys,re
import pcbnew as p
from finite_shapes import shape,build,L
D=Path(__file__).resolve().parent;B=D.parent/'j107_mode_port_closure';path=Path(sys.argv[1]) if len(sys.argv)>1 else D/'native/mainboard_revD.kicad_pcb'
def need(x,m):
 if not x:raise RuntimeError(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
need(sha(B/'native/mainboard_revD.kicad_pcb')=='8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5','baseline changed')
a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(path))
def track(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,list(t.GetLayerSet().Seq()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
need({t.m_Uuid.AsString():track(t)for t in a.GetTracks()}=={t.m_Uuid.AsString():track(t)for t in b.GetTracks()},'track/via delta not authorized')
# Native footprint blocks lock every pad/net/body/position, not merely counts.
def blocks(f,kind):return re.findall(r'\n\t\('+kind+r'\n.*?\n\t\)',f.read_text(),re.S)
need(blocks(B/'native/mainboard_revD.kicad_pcb','footprint')==blocks(path,'footprint'),'footprint delta')
for f in (B/'native').rglob('*.kicad_sch'):need(f.read_bytes()==(D/'native'/f.relative_to(B/'native')).read_bytes(),'source changed')
for ext in ['kicad_pro','kicad_dru']:need((B/'native'/('mainboard_revD.'+ext)).read_bytes()==(D/'native'/('mainboard_revD.'+ext)).read_bytes(),'project/rules changed')
rules={z.GetZoneName():z for z in b.Zones()if z.GetIsRuleArea()}
need('LIS2DW12_BODY_ALL6_NO_PLANES_OR_VIAS' not in rules,'obsolete all-layer rule retained')
f=rules.get('LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA');c=rules.get('LIS2DW12_F_CENTRAL_NO_TRACK_PROJECT_SCREEN')
need(f is not None and c is not None,'layered rules missing')
need(list(f.GetLayerSet().Seq())==[p.F_Cu] and f.GetDoNotAllowVias() and f.GetDoNotAllowCopperPour() and not f.GetDoNotAllowTracks(),'F body flags/layer')
need(list(c.GetLayerSet().Seq())==[p.F_Cu] and c.GetDoNotAllowTracks() and c.GetDoNotAllowVias() and c.GetDoNotAllowCopperPour() and not c.GetDoNotAllowPads(),'central flags/layer')
for z in a.Zones():
 if not z.GetIsRuleArea() or 'LIS2DW12' in z.GetZoneName():continue
 k=rules.get(z.GetZoneName());need(k is not None and k.Outline().Format()==z.Outline().Format() and list(k.GetLayerSet().Seq())==list(z.GetLayerSet().Seq()) and [k.GetDoNotAllowTracks(),k.GetDoNotAllowVias(),k.GetDoNotAllowCopperPour()]==[z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowCopperPour()],'non-MEMS rule changed')
need(len(rules)==len([z for z in b.Zones()if z.GetIsRuleArea()]),'duplicate rule names')
expected_names={z.GetZoneName()for z in a.Zones()if z.GetIsRuleArea()}-{'LIS2DW12_BODY_ALL6_NO_PLANES_OR_VIAS'}|{'LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA','LIS2DW12_F_CENTRAL_NO_TRACK_PROJECT_SCREEN'}
need(set(rules)==expected_names,'unexpected rule set')
def points(z):
 q=z.Outline().Outline(0);return[(q.CPoint(i).x,q.CPoint(i).y)for i in range(q.PointCount())]
need(points(f)==[(3000000,81000000),(5000000,81000000),(5000000,83000000),(3000000,83000000)],'F body outline')
need(points(c)==[(3425000,81412500),(4575000,81412500),(4575000,82587500),(3425000,82587500)],'central outline')
body=f.Outline();central=c.Outline()
for z in b.Zones():
 if z.GetIsRuleArea() or not z.IsOnLayer(p.F_Cu):continue
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(z.GetFilledPolysList(p.F_Cu),body);need(q.Area()<=1,'F body plane intrusion')
for t in b.GetTracks():
 if not t.IsOnLayer(p.F_Cu):continue
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(shape(t,p.F_Cu),body if isinstance(t,p.PCB_VIA)else central);need(q.Area()<=1,'via or central F track intrusion')
def graph(nodes):
 par=list(range(len(nodes)))
 def rt(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 for i,(_,_,x)in enumerate(nodes):
  for j,(_,_,y)in enumerate(nodes[:i]):
   for l in x.keys()&y.keys():
    if not x[l].BBox().Intersects(y[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(x[l],y[l])
    if q.Area()>1:par[rt(i)]=rt(j);break
 groups={}
 for i,(name,pad,_)in enumerate(nodes):groups.setdefault(rt(i),[]).append((name,pad))
 return list(groups.values())
na,nb=build(a),build(b);ca={n:graph(v)for n,v in na.items()};cb={n:graph(v)for n,v in nb.items()}
def pc(cs):return sorted(sorted(n for n,pad in g if pad)for g in cs if any(pad for _,pad in g))
need({n:pc(v)for n,v in ca.items()}=={n:pc(v)for n,v in cb.items()},'actual pad connectivity changed')
islands={}
for net,core in [('GND','C104.2'),('3V3_AON','C104.1')]:
 g=next(g for g in cb[net] if any(n==core for n,_ in g));in_core={n for n,_ in g};all_islands=[n for n,pad,_ in nb[net] if '/' in n and not pad];need(set(all_islands)<=in_core,'floating reference/power island '+net);islands[net]=all_islands
areas=[]
for z in b.Zones():
 if z.GetIsRuleArea():continue
 old=next(x for x in a.Zones()if x.m_Uuid==z.m_Uuid)
 for l in L:
  if z.IsOnLayer(l):
   removed=p.SHAPE_POLY_SET(old.GetFilledPolysList(l));removed.BooleanSubtract(z.GetFilledPolysList(l));need(removed.Area()<=1,'unexpected plane removal')
   added=p.SHAPE_POLY_SET(z.GetFilledPolysList(l));added.BooleanSubtract(old.GetFilledPolysList(l));added.BooleanSubtract(body);need(added.Area()<=1,'plane change outside declared body')
   areas.append({'zone':z.m_Uuid.AsString(),'net':z.GetNetname(),'layer':b.GetLayerName(l),'before_mm2':old.GetFilledPolysList(l).Area()/1e12,'after_mm2':z.GetFilledPolysList(l).Area()/1e12,'before_islands':old.GetFilledPolysList(l).OutlineCount(),'after_islands':z.GetFilledPolysList(l).OutlineCount()})
print(json.dumps({'status':'BOUNDED_RULE_AND_FINITE_COPPER_CHECK_ONLY_NOFAB','pcb_sha256':sha(path),'unchanged_tracks_vias':len(list(b.GetTracks())),'unchanged_footprints':len(list(b.GetFootprints())),'pad_net_components_identical':True,'all_plane_islands_reach_core':islands,'plane_areas':areas,'peripheral_F_pad_ground_links':'manual review remains open, not certified by central rule','manufacturer_layer_scope':'B allowed explicitly; inner reference geometry is project inference; no same-side central routing/via'},indent=2))
