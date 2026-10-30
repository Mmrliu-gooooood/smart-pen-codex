from pathlib import Path
import os,json,collections
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcuprobe0109'
import pcbnew as p
from finite_copper import build
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));ns=build(b)['GND'];lookup={x[0]:x for x in ns};seen={'C504.2'};todo=['C504.2'];prev={}
while todo:
 name=todo.pop(0);_,_,x=lookup[name]
 if name=='J106.3':break
 for n,_,y in ns:
  if n in seen:continue
  for l in x.keys()&y.keys():
   if not x[l].BBox().Intersects(y[l].BBox()):continue
   z=p.SHAPE_POLY_SET();z.BooleanIntersection(x[l],y[l])
   if z.Area()>1:seen.add(n);todo.append(n);prev[n]={'from':name,'layer':b.GetLayerName(l),'area_mm2':z.Area()/1e12};break
path=[];n='J106.3'
while n in prev:path.append(dict(to=n,**prev[n]));n=prev[n]['from']
objects={t.m_Uuid.AsString():{'net':t.GetNetname(),'start':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'layer':b.GetLayerName(t.GetLayer())}for t in b.GetTracks()if t.m_Uuid.AsString()in set(q['to']for q in path)|set(q['from']for q in path)}
print(json.dumps({'connected':'J106.3'in seen,'path':path[::-1],'objects':objects},indent=2))
