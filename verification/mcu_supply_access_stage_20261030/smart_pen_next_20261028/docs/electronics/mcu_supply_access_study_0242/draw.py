import os
os.environ["MPLCONFIGDIR"]="/tmp/mcu-access-mpl"
os.environ["XDG_CACHE_HOME"]="/tmp/mcu-access-cache"
import contextlib,io
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle
import geometry as q
with contextlib.redirect_stdout(io.StringIO()):import two_vias as z
p=q.p
fig,axs=plt.subplots(1,2,figsize=(12,8))
def poly(ax,s,c,alpha=.6):
 for k in range(s.OutlineCount()):
  t=s.COutline(k); pts=[(t.CPoint(i).x/1e6,t.CPoint(i).y/1e6)for i in range(t.PointCount())]
  if len(pts)>2:ax.add_patch(Polygon(pts,closed=True,facecolor=c,edgecolor='none',alpha=alpha))
for ax,l in zip(axs,[p.F_Cu,p.B_Cu]):
 for t in q.old:
  if t.IsOnLayer(l):poly(ax,q.shape(t,l),'#9fadb4',.8)
 for pad in q.pads:
  if pad.IsOnLayer(l):poly(ax,q.shape(pad,l),'#586873',.7)
 for t in z.n:
  if t.IsOnLayer(l):
   poly(ax,q.shape(t,l),'#c32121'if t.GetNetname()=='3V3_AON'else'#009a67',.85)
   if isinstance(t,p.PCB_VIA):ax.add_patch(Circle(q.xy(t),.15,color='white',zorder=6))
 for ref in ['C103','R503','U101']:
  f=z.fps[ref];f.BuildCourtyardCaches();side=p.F_CrtYd if l==p.F_Cu else p.B_CrtYd
  s=f.GetCourtyard(side)
  if s.OutlineCount():
   for k in range(s.OutlineCount()):
    t=s.COutline(k);pts=[(t.CPoint(i).x/1e6,t.CPoint(i).y/1e6)for i in range(t.PointCount())];ax.add_patch(Polygon(pts,closed=True,fill=False,edgecolor='#dd9800',linestyle='--'))
  if f.GetLayer()==l:ax.text(*q.xy(f),ref,fontsize=10,ha='center',va='center')
 ax.set_xlim(0,4.6);ax.set_ylim(14,4.5);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('PCB x / mm');ax.set_title(q.b.GetLayerName(l)+' | new red=AON, green=GND reinforcement')
axs[0].set_ylabel('PCB y / mm');fig.suptitle('Read-only C103/R503 access study: no native board, NOFAB\nOrange courtyard overlap remains a manufacturing review gate')
fig.tight_layout();fig.savefig(q.D/'access_model.png',dpi=150)
