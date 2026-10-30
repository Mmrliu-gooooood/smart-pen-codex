from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Polygon
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));j=next(f for f in b.GetFootprints()if f.GetReference()=='J202');links=json.loads((D/'ground_links.json').read_text());fig,ax=plt.subplots(figsize=(14,7));ax.add_patch(Rectangle((.05,90),13.9,4,facecolor='#edf5f9',edgecolor='#6c8796',alpha=.7));
for pad in j.Pads():
 x,y=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6;w,h=pad.GetSize().x/1e6,pad.GetSize().y/1e6
 if round(pad.GetOrientationDegrees())%180==90:w,h=h,w
 ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#228b22'if pad.GetNetname()=='GND'else'#777777',edgecolor='black',linewidth=.5));ax.text(x,y-.45,pad.GetNumber(),ha='center',fontsize=8)
for q in links:
 for a,z in zip(q['path'],q['path'][1:]):
  dx,dy=z[0]-a[0],z[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*.125,dx/length*.125;ax.add_patch(Polygon([(a[0]+nx,a[1]+ny),(z[0]+nx,z[1]+ny),(z[0]-nx,z[1]-ny),(a[0]-nx,a[1]-ny)],facecolor='#008800'));ax.add_patch(Circle(a,.125,facecolor='#008800'));ax.add_patch(Circle(z,.125,facecolor='#008800'))
 if q['via_xy']:
  x,y=q['via_xy'];ax.add_patch(Circle((x,y),.3,facecolor='#77bb77',edgecolor='#006600'));ax.add_patch(Circle((x,y),.15,facecolor='white',edgecolor='#006600'));ax.text(x,y-.38,'G'+q['pin'],ha='center',fontsize=8)
for f in b.GetFootprints():
 if f.GetReference()!='J301':continue
 for pad in f.Pads():
  x,y=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6;w,h=pad.GetSize().x/1e6,pad.GetSize().y/1e6
  if round(pad.GetOrientationDegrees())%180==90:w,h=h,w
  ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,fill=False,edgecolor='#bb4444',linestyle='--'));ax.text(x,y,'J301.'+pad.GetNumber()+' F',ha='center',fontsize=8,color='#bb4444')
ax.text(7.5,91.6,'Pin13 -> Pin10: 2.90 mm branch; shared via lead 1.674 mm',ha='center',fontsize=10,color='#006600');ax.text(7,93.65,'Conservative native body outline: underside metal is not fully dimensioned',ha='center',fontsize=10,color='#345566');ax.set_xlim(-.1,14.1);ax.set_ylim(94.25,87.3);ax.set_aspect('equal');ax.set_xlabel('PCB x / mm');ax.set_ylabel('PCB y / mm');ax.grid(alpha=.2);ax.set_title('J202 ground return - PCB XY, not mirrored assembly view - NOFAB\n6 standard 0.60/0.30 vias explicitly tented both sides; other signal routing pending');fig.tight_layout();fig.savefig(D/'return_geometry.png',dpi=160)
