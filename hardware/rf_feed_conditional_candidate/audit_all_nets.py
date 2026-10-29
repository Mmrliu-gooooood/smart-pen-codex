#!/usr/bin/env python3
import os,sys,pathlib,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-rf-check/config'
import pcbnew as p
D=pathlib.Path(__file__).resolve().parent;S=D;sys.path.insert(0,str(D/'tools'));from physical_graph import graph
old=p.LoadBoard(str(S/'source_before.kicad_pcb'));b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));aa=graph(old);bb=graph(b)
def parts(g):return{r['net']:sorted(sorted(c)for c in r['components'])for r in g}
a,c=parts(aa),parts(bb)
changes=[net for net in a if a[net]!=c.get(net)]
if sorted(changes)!=['RF_ANT','RF_SIP']:raise RuntimeError('Unexpected actual pad partition change '+str(changes))
for net in ['RF_ANT','RF_SIP','GND','3V3_AON','SENS_VIO_1V8','STRAP_GPIO45','STRAP_GPIO46','CAM_SDA']:
 if len(c[net])!=1:raise RuntimeError('Disconnected '+net)
def geom(t):return[t.GetClass(),t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth()]
a={t.m_Uuid.AsString():geom(t)for t in old.GetTracks()};c={t.m_Uuid.AsString():geom(t)for t in b.GetTracks()}
def padgeom(f):return[f.GetLayer(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetFPIDAsString(),sorted((x.GetNumber(),x.GetNetname(),x.GetPosition().x,x.GetPosition().y,x.GetSize().x,x.GetSize().y)for x in f.Pads())]
fps={f.GetReference():padgeom(f)for f in b.GetFootprints()};moved=[f.GetReference()for f in old.GetFootprints()if padgeom(f)!=fps.get(f.GetReference())]
if sorted(moved)!=['C106','C107','L101','R104']:raise RuntimeError('Unexpected changed footprints '+str(moved))
result=dict(status='ACTUAL_PAD_CONNECTIVITY_CLOSED_EXCEPT_INHERITED_EN1_NOFAB',source_sha256=hashlib.sha256((S/'source_before.kicad_pcb').read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),changed_partitions=changes,physical_graph=bb,moved_footprints=sorted(moved),removed=[dict(uuid=u,before=a[u])for u in sorted(a.keys()-c.keys())],modified=[dict(uuid=u,before=a[u],after=c[u])for u in sorted(a.keys()&c.keys())if a[u]!=c[u]],added=[dict(uuid=u,after=c[u])for u in sorted(c.keys()-a.keys())])
print(json.dumps(result,indent=2,sort_keys=True))
