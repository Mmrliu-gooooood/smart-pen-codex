from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-native1950-config';os.environ['MPLCONFIGDIR']='/tmp/pen-native1950-mpl'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));ts=list(b.GetTracks());nets=sorted(set(t.GetNetname()for t in ts));colors={n:plt.get_cmap('tab20')(i)for i,n in enumerate(nets)}
fig,axs=plt.subplots(1,3,figsize=(13,15))
for ax,name in zip(axs,['F.Cu','In3.Cu','B.Cu']):
 lid=b.GetLayerID(name)
 for f in b.GetFootprints():
  for q in f.Pads():
   if q.IsOnLayer(lid):
    box=q.GetBoundingBox();ax.add_patch(Rectangle((box.GetX()/1e6,box.GetY()/1e6),box.GetWidth()/1e6,box.GetHeight()/1e6,color='#bbbbbb',alpha=.6))
  if f.IsOnLayer(lid)and f.GetReference()in['U201','U202','U203','J103','J105','J106','J107','J202']:
   v=f.GetPosition();ax.text(v.x/1e6,v.y/1e6,f.GetReference(),fontsize=6)
 for t in ts:
  if isinstance(t,p.PCB_VIA):
   v=t.GetPosition();ax.add_patch(Circle((v.x/1e6,v.y/1e6),t.GetWidth(p.F_Cu)/2e6,fill=False,color=colors[t.GetNetname()],lw=.7))
  elif t.IsOnLayer(lid):ax.plot([t.GetStart().x/1e6,t.GetEnd().x/1e6],[t.GetStart().y/1e6,t.GetEnd().y/1e6],color=colors[t.GetNetname()],lw=1)
 for x in b.GetDrawings():
  if x.GetLayer()==p.Edge_Cuts:ax.plot([x.GetStart().x/1e6,x.GetEnd().x/1e6],[x.GetStart().y/1e6,x.GetEnd().y/1e6],color='black',lw=.8)
 ax.set_title(name);ax.set_xlim(-.5,14.5);ax.set_ylim(103,-1);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('X / mm')
axs[0].set_ylabel('Y / mm');fig.suptitle('NOFAB — actual saved native PCB, two-ref mechanical-clearance successor\n12 translator-to-head chains ONLY; 60 tracks + 16 vias; full DRC 0 / 262 unconnected / 0 parity\nAll former routing and plane fill absent: power, MCU, bias stubs and return paths NOT connected')
fig.tight_layout(rect=(0,0,1,.94));fig.savefig(D/'native_layers.png',dpi=150)
