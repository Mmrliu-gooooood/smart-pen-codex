from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));changed=json.loads((D/'placement_changes.json').read_text())['changed']
fig,axs=plt.subplots(1,2,figsize=(10,14))
for ax,l in zip(axs,[p.F_Cu,p.B_Cu]):
 for f in b.GetFootprints():
  if f.GetLayer()!=l or not 25<=f.GetPosition().y/1e6<=63:continue
  f.BuildCourtyardCaches();q=f.GetCourtyard(l)
  for i in range(q.OutlineCount()):
   c=q.COutline(i);ax.add_patch(Polygon([(c.CPoint(j).x/1e6,c.CPoint(j).y/1e6)for j in range(c.PointCount())],fill=False,edgecolor='#246aa7'if f.GetReference()in changed else '#aaa'))
  for a in f.Pads():
   if not a.IsOnLayer(l):continue
   bb=a.GetBoundingBox();ax.add_patch(Rectangle((bb.GetX()/1e6,bb.GetY()/1e6),bb.GetWidth()/1e6,bb.GetHeight()/1e6,color='#c99748',alpha=.7))
  v=f.GetPosition();ax.text(v.x/1e6,v.y/1e6,f.GetReference(),ha='center',va='center',fontsize=7)
 ax.set_xlim(0,14);ax.set_ylim(63,25);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(b.GetLayerName(l)+' / common top-view coordinates');ax.set_xlabel('PCB X mm');ax.set_ylabel('PCB Y mm')
fig.suptitle('NOFAB placement-only: 3 translators rotated; all routing removed\nBlue: changed courtyard; not electrical/mechanical qualification')
fig.tight_layout();fig.savefig(D/'placement_overview.png',dpi=140)
