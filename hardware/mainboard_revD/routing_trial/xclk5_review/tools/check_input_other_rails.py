from pathlib import Path
import pcbnew as p,numpy as np,json,sys,math
from PIL import Image,ImageDraw
from scipy import ndimage
D=Path(__file__).resolve().parents[1];name=sys.argv[1];rail=sys.argv[2];rail_layer=p.In1_Cu if rail=='GND' else p.In2_Cu;anchor_ref='J106.3' if rail=='GND' else 'C202.1';b=p.LoadBoard(str(D/(name+'.kicad_pcb')));b.BuildConnectivity();con=b.GetConnectivity();scale=40
im=Image.new('1',(481,3801));draw=ImageDraw.Draw(im)
for z in b.Zones():
 if z.GetLayer()!=rail_layer or z.GetNetname()!=rail:continue
 pp=z.GetFilledPolysList(rail_layer)
 for i in range(pp.OutlineCount()):
  c=pp.COutline(i);draw.polygon([(round(p.ToMM(c.CPoint(j).x)*scale),round(p.ToMM(c.CPoint(j).y)*scale)) for j in range(c.PointCount())],fill=1)
labels,n=ndimage.label(np.array(im,dtype=bool));parent={}
def find(x):
 parent.setdefault(x,x)
 if parent[x]!=x:parent[x]=find(parent[x])
 return parent[x]
def union(a,z):parent[find(a)]=find(z)
rows=[]
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetNetname()!=rail:continue
  label=f.GetReference()+'.'+a.GetNumber()+'@'+a.m_Uuid.AsString();q=[a];seen=set();hits=set();via=[]
  while q:
   o=q.pop();key=o.m_Uuid.AsString()
   if key in seen:continue
   seen.add(key);union(label,key)
   if o.GetClass()=='PCB_VIA':
    x=p.ToMM(o.GetPosition().x);y=p.ToMM(o.GetPosition().y);via.append([x,y])
    for rad in [0,.2,.25]:
     for ang in range(0,360,45):
      xx=round((x+rad*math.cos(math.radians(ang)))*scale);yy=round((y+rad*math.sin(math.radians(ang)))*scale)
      if 0<=xx<481 and 0<=yy<3801 and labels[yy,xx]:hits.add(int(labels[yy,xx]))
   q.extend(con.GetConnectedTracks(o));q.extend(con.GetConnectedPads(o))
  for h in hits:union(label,'zone'+str(h))
  rows.append({'pad':label,'local_connected_copper_objects':len(seen),'reaches_plane_regions':sorted(hits),'reachable_vias_mm':via})
anchor=next(r['pad'] for r in rows if r['pad'].startswith(anchor_ref+'@'))
for r in rows:
 r['reaches_candidate_AON_anchor']=find(r['pad'])==find(anchor)
 r['electrical_component']=find(r['pad'])
bad=[r['pad'] for r in rows if not r['reaches_candidate_AON_anchor']]
result={'board':name,'anchor':anchor,'rail':rail,'note':'Each copper padshape identified by UUID, so duplicate EP pin57 pads cannot be falsely joined by equal pin number. Actual local copper graph + same-rail filled region contacts; no SI/current-capacity qualification.', 'filled_plane_raster_regions':int(n),'padshape_count':len(rows),'failed_pads':bad,'per_pad':rows}
(D/(name+'_'+rail+'_endpoints.json')).write_text(json.dumps(result,indent=2));print(rail+' endpoints',len(rows),'failed',bad,'regions',n);assert not bad
