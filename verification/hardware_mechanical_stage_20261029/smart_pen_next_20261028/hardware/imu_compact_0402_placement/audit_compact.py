#!/usr/bin/env python3
import os,sys,json,math,hashlib,pathlib,xml.etree.ElementTree as ET
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=pathlib.Path(__file__).resolve().parent
path=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else D/'mainboard_revD.kicad_pcb'

# KiCad may repair track net assignments on load; validate explicit serialized identities first.
import re
def raw_track_nets(file):
 text=file.read_text();names={int(n):v for n,v in re.findall(r'\(net (\d+) "([^"\n]+)"\)',text)};out={}
 for block in re.findall(r'\n\t\((?:segment|via)\n.*?\n\t\)',text,re.S):
  uid=re.search(r'\(uuid "([^"\n]+)"\)',block);net=re.search(r'\(net (\d+)\)',block)
  if uid and net:out[uid[1]]=names[int(net[1])]
 return out
raw_expected=raw_track_nets(D.parent/'mainboard_input_imu_power_routing/mainboard_revD.kicad_pcb');raw_actual=raw_track_nets(path)
for uid in raw_actual.keys()&raw_expected.keys():
 if raw_actual[uid]!=raw_expected[uid]:raise RuntimeError('Explicit serialized copper net changed '+uid)

b=p.LoadBoard(str(path));old=p.LoadBoard(str(D.parent/'mainboard_input_imu_power_routing/mainboard_revD.kicad_pcb'))
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

na,nb=build(old),build(b);ca={n:components(v) for n,v in na.items() if sum(x[1] for x in v)>1};cb={n:components(v) for n,v in nb.items() if sum(x[1] for x in v)>1}
for net,comps in ca.items():
 for c in comps:require(any(set(c)<=set(z) for z in cb[net]),'Old pad component split '+net+str(c))
required={'3V3_AON':['J106.2','U501.2','U501.3','U501.9','U501.10','C501.1','C502.1','C503.1','R501.1','R502.1','C104.1'],'GND':['J106.3','U501.5','U501.6','U501.7','U501.8','C501.2','C502.2','C503.2','C104.2']}
for net,need in required.items():require(any(set(need)<=set(c) for c in cb[net]),'Power block disconnected '+net)
fps={f.GetReference():f for f in b.GetFootprints()};afps={f.GetReference():f for f in old.GetFootprints()}
x=ET.parse(D/'fresh.xml');cs={c.get('ref'):c for c in x.findall('./components/comp')};ns={(n.get('ref'),n.get('pin')):net.get('name') for net in x.findall('./nets/net') for n in net}
require(len(cs)==102 and len(ns)==356 and len(fps)==102,'Source count')
for r,f in fps.items():
 c=cs[r];require(f.GetValue()==c.findtext('value'),'Value mismatch '+r);require(f.GetFPIDAsString()==c.findtext('footprint'),'Footprint mismatch '+r)
 require(f.GetPath().AsString()=='/cebe562b-54ce-58d7-a4f0-094e70dd7d0a'+c.find('sheetpath').get('tstamps')+c.findtext('tstamps'),'Source path '+r)
 for pad in f.Pads():require(pad.GetNetname()==ns.get((r,pad.GetNumber()),''),'Actual pad-net '+r)
def fg(f):return(f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer(),f.GetAttributes(),f.GetValue(),f.GetFPIDAsString(),[(q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetSize().x,q.GetSize().y,q.GetOrientationDegrees(),list(q.GetLayerSet().Seq())) for q in f.Pads()])
require(sorted(r for r in fps if fg(fps[r])!=fg(afps[r]))==['C501','C502','C503','R501'],'Unexpected footprint delta')
def tg(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayer(),t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetDrillValue() if isinstance(t,p.PCB_VIA) else None)
a={t.m_Uuid.AsString():tg(t) for t in old.GetTracks()};c={t.m_Uuid.AsString():tg(t) for t in b.GetTracks()}
require(set(a)-set(c)==set(json.loads((D/'placement_delta.json').read_text())['removed_previous_imu_copper']),'Deleted copper')
require(all(a[k]==c[k] for k in a.keys()&c.keys()),'Old copper changed')
rows=json.loads((D/'new_local_routes.json').read_text());ids={r['uuid']for r in rows};require(set(c)-set(a)==ids,'New copper set')
byid={t.m_Uuid.AsString():t for t in b.GetTracks()}
for r in rows:
 t=byid[r['uuid']];require(t.GetNetname()==r['net'],'New copper net')
 if r['type']=='track':require(t.GetLayer()==p.F_Cu and t.GetWidth()==p.FromMM(r['width']) and [p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)]==r['a'] and [p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]==r['z'],'New copper geometry')
 else:require(t.GetDrillValue()==round(r['drill']*1e6)and t.GetWidth(p.F_Cu)==round(r['diameter']*1e6),'Via dimensions')
keep=p.SHAPE_POLY_SET();keep.NewOutline()
for xx,yy in [(3,81),(5,81),(5,83),(3,83)]:keep.Append(p.FromMM(xx),p.FromMM(yy))
rules=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()=='LIS2DW12_BODY_ALL6_NO_PLANES_OR_VIAS'];require(len(rules)==1 and set(rules[0].GetLayerSet().Seq())==set(L) and rules[0].GetDoNotAllowCopperPour() and rules[0].GetDoNotAllowVias(),'MEMS rule area')
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for l in L:
  if not z.IsOnLayer(l):continue
  q=p.SHAPE_POLY_SET();q.BooleanIntersection(z.GetFilledPolysList(l),keep);require(q.Area()<=1,'Actual plane intrusion MEMS')
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):continue
 for l in L:
  q=p.SHAPE_POLY_SET();q.BooleanIntersection(shape(t,l),keep);require(q.Area()<=1,'Via intrusion MEMS')
j=fps['JP301'];require('OPEN' in j.GetValue().upper() or 'OPEN' in j.GetFPIDAsString().upper(),'JP301 not declared OPEN')
jp=list(j.Pads());require(len(jp)==2 and jp[0].GetNetname()!=jp[1].GetNetname(),'JP301 pad identities')
q=p.SHAPE_POLY_SET();q.BooleanIntersection(shape(jp[0],p.F_Cu),shape(jp[1],p.F_Cu));require(q.Area()<=1,'JP301 pad bridge')
core=next(c for c in cb['3V3_AON'] if 'C104.1' in c);gate=[n for n in core if n.startswith('U301.') or n.startswith('C301.')];require(not gate,'Unexpected gate supply merge')
print(json.dumps({'status':'BOUNDED_GEOMETRY_CONNECTIVITY_ACCEPTED_NOFAB','pcb':hashlib.sha256(path.read_bytes()).hexdigest(),'counts':{'entities':len(cs),'endpoints':len(ns),'nets':len(x.findall('./nets/net'))},'added':len(ids),'removed':sorted(set(a)-set(c)),'MEMS_exact_polygon_plane_and_via_intrusion':False,'gate_not_in_core_AON':True,'pad_components':cb},indent=2))
