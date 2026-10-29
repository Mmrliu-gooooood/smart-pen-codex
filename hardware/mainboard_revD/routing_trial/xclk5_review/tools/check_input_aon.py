from pathlib import Path
import pcbnew as p,numpy as np,json,sys,math
from PIL import Image,ImageDraw
from scipy import ndimage
D=Path(__file__).resolve().parents[1];name=sys.argv[1];b=p.LoadBoard(str(D/(name+'.kicad_pcb')));b.BuildConnectivity();con=b.GetConnectivity();scale=40
im=Image.new('1',(481,3801));draw=ImageDraw.Draw(im)
for z in b.Zones():
 if z.GetLayer()!=p.In2_Cu or z.GetNetname()!='3V3_AON':continue
 pp=z.GetFilledPolysList(p.In2_Cu)
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
  if a.GetNetname()!='3V3_AON':continue
  label=f.GetReference()+'.'+a.GetNumber();q=[a];seen=set();hits=set();via=[]
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
anchor='J106.2';assert anchor in [r['pad'] for r in rows]
for r in rows:
 r['reaches_candidate_AON_anchor']=find(r['pad'])==find(anchor)
 r['electrical_component']=find(r['pad'])
bad=[r['pad'] for r in rows if not r['reaches_candidate_AON_anchor']]
result={'board':name,'anchor':anchor,'note':'J106.2 is a physically placed PCB wire land; wire and assembly are not qualified. Native local track/pad graph plus actual filled In2 raster-region contacts; 25um geometric screening, not DC drop/current capacity or SI qualification. Each same-net via sampled within copper annulus.', 'filled_plane_raster_regions':int(n),'padshape_count':len(rows),'failed_pads':bad,'per_pad':rows}
(D/(name+'_aon_endpoints.json')).write_text(json.dumps(result,indent=2));print('AON endpoints',len(rows),'failed',bad,'regions',n);assert not bad
