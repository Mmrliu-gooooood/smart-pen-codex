from pathlib import Path
import pcbnew as p,numpy as np,json
from PIL import Image,ImageDraw
from scipy import ndimage
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));S=40
im=Image.new('1',(481,3801));draw=ImageDraw.Draw(im)
for z in b.Zones():
 if z.GetLayer()!=p.In2_Cu or z.GetNetname()!='3V3_AON':continue
 pp=z.GetFilledPolysList(p.In2_Cu)
 for i in range(pp.OutlineCount()):
  c=pp.COutline(i);draw.polygon([(round(p.ToMM(c.CPoint(j).x)*S),round(p.ToMM(c.CPoint(j).y)*S)) for j in range(c.PointCount())],fill=1)
a=np.array(im,dtype=bool);dist=ndimage.distance_transform_edt(a)/S
# Crop endpoint neighborhoods only for erosion contact, not add copper.
ends={'input':[(6.1,82.4),(6.9,82.4)],'bridge_zone2':[(9.35,22.95)],'bridge_zone1':[(5.175,18.9)],'PICO_power':[ (7.4,5.8) ]}
def near(labels,xy,r=.45):
 hits=set()
 for x,y in xy:
  xx,yy=round(x*S),round(y*S);q=round(r*S)
  for dy in range(-q,q+1):
   for dx in range(-q,q+1):
    if dx*dx+dy*dy<=q*q and 0<=yy+dy<labels.shape[0] and 0<=xx+dx<labels.shape[1] and labels[yy+dy,xx+dx]:hits.add(int(labels[yy+dy,xx+dx]))
 return hits
rows=[]
for erosion in [0,.05,.075,.1,.125,.15,.2,.25,.3,.4]:
 lab,n=ndimage.label(a if erosion==0 else dist>erosion)
 rows.append({'erosion_radius_mm':erosion,'remaining_regions':int(n),'input_to_bridge_zone2':bool(near(lab,ends['input'])&near(lab,ends['bridge_zone2']))})
out={'method':'25um filled In2 raster, 4-connected region labels after isotropic erosion; endpoint contact within 0.45mm neighborhoods. Not exact polygon neck width, DC resistance, or full path PI proof. No copper added by analysis.','input_vias_mm':ends['input'],'bridge_zone2_via_mm':ends['bridge_zone2'],'minimum_axial_span_mm':82.4-22.95,'erosion_screen':rows,'important':'Input to bridge is about 59.45mm axial plane span, not merely the 7.039mm bridge. Width/current distribution/neck/via/wire resistance and transients remain unqualified.'}
(D/'plane_corridor_screen.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
Image.fromarray((a*255).astype('uint8')).save(D/'input_In2_filled.png')
from collections import deque
mask=dist>.1
starts=[];targets=set()
for key,dest in [('input',starts),('bridge_zone2',targets)]:
 for x,y in ends[key]:
  xx,yy=round(x*S),round(y*S)
  for dy in range(-18,19):
   for dx in range(-18,19):
    if dx*dx+dy*dy<=324 and mask[yy+dy,xx+dx]:
     v=(yy+dy)*481+xx+dx
     dest.append(v) if isinstance(dest,list) else dest.add(v)
prev=np.full(mask.size,-2,dtype=np.int32);q=deque(starts)
for v in starts:prev[v]=-1
finish=None
while q:
 v=q.popleft()
 if v in targets:finish=v;break
 y,x=divmod(v,481)
 for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
  if 0<=yy<3801 and 0<=xx<481:
   w=yy*481+xx
   if prev[w]==-2 and mask[yy,xx]:prev[w]=v;q.append(w)
if finish is None:raise RuntimeError('no AON path after .1mm raster erosion')
path=[];v=finish
while v>=0:
 y,x=divmod(v,481);path.append([x/S,y/S,float(dist[y,x])]);v=int(prev[v])
neck=[v for v in path if v[2]<=.125]
out['screened_path_length_orthogonal_mm']=(len(path)-1)/S
out['narrow_path_samples_clearance_le_125um']=neck
out['note_path']='Raster shortest path after 0.1mm erosion, not actual current streamline; clearance is distance to nearest void, not guaranteed conductor width.'
(D/'plane_corridor_screen.json').write_text(json.dumps(out,indent=2))
print('narrow samples',len(neck),'bounds', [min(v[i] for v in neck) for i in range(2)],[max(v[i] for v in neck) for i in range(2)])
