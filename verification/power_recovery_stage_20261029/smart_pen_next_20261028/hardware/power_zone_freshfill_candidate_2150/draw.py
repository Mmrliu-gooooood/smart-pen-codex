from pathlib import Path
import os
os.environ['XDG_CONFIG_HOME']='/tmp/pen-draw2150';os.environ['MPLCONFIGDIR']='/tmp/pen-mpl2150'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));fig,axs=plt.subplots(1,3,figsize=(10,15))
for ax,l in zip(axs,[p.In1_Cu,p.In2_Cu,p.In4_Cu]):
 for z in b.Zones():
  if z.GetIsRuleArea()or not z.IsOnLayer(l):continue
  q=z.GetFilledPolysList(l)
  for i in range(q.OutlineCount()):
   for h in range(-1,q.HoleCount(i)):
    c=q.COutline(i)if h<0 else q.CHole(i,h);ax.add_patch(Polygon([(c.CPoint(j).x/1e6,c.CPoint(j).y/1e6)for j in range(c.PointCount())],color=('#9ccdbb'if z.GetNetname()=='GND'else '#e8b985')if h<0 else 'white',lw=0))
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   c=t.GetPosition();ax.add_patch(Circle((c.x/1e6,c.y/1e6),t.GetWidth(p.F_Cu)/2e6,fill=False,color='black',lw=.5))
  elif t.IsOnLayer(l):ax.plot([t.GetStart().x/1e6,t.GetEnd().x/1e6],[t.GetStart().y/1e6,t.GetEnd().y/1e6],color='#5555bb',lw=.6)
 ax.plot([11.9,11.9],[83.9,86.3],'rx');ax.set_title(b.GetLayerName(l));ax.set_xlim(-.5,14.5);ax.set_ylim(103,-1);ax.set_aspect('equal');ax.grid(alpha=.2)
fig.suptitle('NOFAB - fresh fill only d64594c0\n2 warnings / 232 unconnected / 0 parity; AON island not powered\nOnly 1/39 AON and 2/102 GND pads connected to J106 core. Do not power.');fig.tight_layout(rect=(0,0,1,.94));fig.savefig(D/'fresh_planes.png',dpi=140)
