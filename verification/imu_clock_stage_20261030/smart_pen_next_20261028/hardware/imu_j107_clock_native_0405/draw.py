from pathlib import Path
import sys,types,os
D=Path(__file__).resolve().parent;R=D.parents[1]
os.environ['MPLCONFIGDIR']='/tmp/imu-native-mpl'
sys.path.insert(0,str(R/'hardware/imu_power_return_candidate_0333'));import geometry as q
q.b=q.p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));q.pads=[pad for f in q.b.GetFootprints()for pad in f.Pads()];q.old=[]
z=types.SimpleNamespace(q=q,new=list(q.b.GetTracks()),D=D)
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
q=z.q;p=q.p
fig,axes=plt.subplots(1,3,figsize=(12,9),sharex=True,sharey=True)
for ax,l,title in zip(axes,[p.F_Cu,p.B_Cu,p.In3_Cu],['Front: unchanged IMU/caps','Back: moved J107, clock endpoints','In3: restored clock corridor']):
 for pad in q.pads:
  if pad.IsOnLayer(l):
   a=pad.GetPosition();sz=pad.GetSize();ax.add_patch(Rectangle((a.x/1e6-sz.x/2e6,a.y/1e6-sz.y/2e6),sz.x/1e6,sz.y/1e6,color='gray',alpha=.35))
 for t in q.old+z.new:
  if not t.IsOnLayer(l):continue
  col={'3V3_AON':'#d64a35','GND':'#198d57','SENS_EXTCLK':'#7335d6'}.get(t.GetNetname(),'#9bb0bb');a=t.GetStart();b=t.GetEnd()
  if isinstance(t,p.PCB_VIA):ax.add_patch(Circle((a.x/1e6,a.y/1e6),t.GetWidth(l)/2e6,fill=False,color=col,lw=1))
  else:ax.plot([a.x/1e6,b.x/1e6],[a.y/1e6,b.y/1e6],color=col,lw=1.6 if t in z.new else .7)
 ax.set_title(title,fontsize=10);ax.set_xlim(.5,8);ax.set_ylim(91,77);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('PCB x / mm')
axes[0].set_ylabel('PCB y / mm');axes[0].add_patch(Rectangle((3,81),2,2,fill=False,ls='--',color='black'))
fig.suptitle('NATIVE CANDIDATE — NO FAB / NO POWER\nRed=AON · Green=GND · Purple=EXTCLK; trace widths illustrative, native checks in JSON',fontsize=11)
fig.tight_layout();fig.savefig(z.D/'native_view.png',dpi=150)
