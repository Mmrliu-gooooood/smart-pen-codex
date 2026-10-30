from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));new=set(json.loads((D/'geometry_delta.json').read_text())['added']);colors={'SENS_VIO_1V8':'#b32e35','SENS_SCL':'#1962a8','SENS_SDA':'#b37900','SENS_XSHUTDN_N':'#7a31a2','SENS_TRIG_IN':'#168364'}
fig,axs=plt.subplots(1,2,figsize=(12,12),gridspec_kw={'width_ratios':[1,1.6]})
for ax,extent in zip(axs,[(0,14,52,94),(.0,14,87.5,93)]):
 for t in b.GetTracks():
  uid=t.m_Uuid.AsString();isnew=uid in new;n=t.GetNetname();color=colors.get(n,'#aaa')if isnew else '#ccc';alpha=1 if isnew else .35
  if isinstance(t,p.PCB_VIA):
   x,y=t.GetPosition().x/1e6,t.GetPosition().y/1e6;ax.add_patch(Circle((x,y),t.GetWidth(p.F_Cu)/2e6,facecolor=color,edgecolor='none',alpha=alpha));ax.add_patch(Circle((x,y),t.GetDrillValue()/2e6,facecolor='white',edgecolor='none',alpha=alpha))
  else:
   x,z=t.GetStart(),t.GetEnd();ax.plot([x.x/1e6,z.x/1e6],[x.y/1e6,z.y/1e6],color=color,alpha=alpha,linewidth=1.3 if isnew else .3,linestyle='--'if isnew and t.GetLayer()==p.In3_Cu else '-')
 for f in b.GetFootprints():
  if f.GetReference()!='J202':continue
  for q in f.Pads():
   x,y=q.GetPosition().x/1e6,q.GetPosition().y/1e6;w,h=q.GetSize().x/1e6,q.GetSize().y/1e6;ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#167440'if q.GetNetname()=='GND'else'#d39b37',alpha=.75));ax.text(x,y+.65,q.GetNumber(),ha='center',va='center',fontsize=7,rotation=90)
 ax.add_patch(Rectangle((.05,90),13.9,4,facecolor='none',edgecolor='#777',linestyle='--'));ax.set_xlim(extent[:2]);ax.set_ylim(extent[2:]);ax.invert_yaxis();ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_xlabel('PCB X (mm)');ax.set_ylabel('PCB Y (mm)')
axs[0].set_title('Five new networks; old copper grey');axs[1].set_title('J202 breakout, all layers projected\nDashed tracks: In3; not an assembly view')
for n,c in colors.items():axs[0].plot([],[],color=c,label=n)
axs[0].legend(loc='upper center',bbox_to_anchor=(.5,-.08),fontsize=8)
fig.suptitle('NOFAB - static routing study, 17 violations / 21 unconnected remain');fig.tight_layout();fig.savefig(D/'routing_overview.png',dpi=180)
