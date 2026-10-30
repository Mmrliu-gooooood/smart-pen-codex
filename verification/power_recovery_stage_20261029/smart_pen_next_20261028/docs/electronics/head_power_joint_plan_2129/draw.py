from pathlib import Path
import os,json
os.environ['MPLCONFIGDIR']='/tmp/pen-head-powerplot'
os.environ['XDG_CACHE_HOME']='/tmp/pen-head-powerfont'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
D=Path(__file__).resolve().parent;p=json.loads((D/'result.json').read_text());fig,axs=plt.subplots(1,4,figsize=(15,10),sharey=True)
colors={'3V3_AON':'#e88a00','GND':'#17834f','CAM_3V3_SW':'#be2b85'}
for ax,l in zip(axs,['F.Cu','In2.Cu','In3.Cu','B.Cu']):
 for pad in p['pad_display']:
  if l not in pad['copper_layers']:continue
  x,y,w,h=pad['bbox']
  if y<70 or y>94:continue
  ax.add_patch(Rectangle((x,y),w,h,facecolor='#dddddd',edgecolor='#777777',lw=.3))
  if pad['ref']in['J106','J301','J202']:ax.text(x+w/2,y+h/2,pad['ref']+'.'+pad['pin'],fontsize=4,ha='center',va='center')
 for o in p['objects']:
  if o['layer']not in[l,'through']:continue
  c=colors.get(o['net'],'#24588e');x,y=o['start'];xx,yy=o['end']
  if o['type']=='via':ax.add_patch(Circle((x,y),o['width']/2,fill=False,edgecolor=c,lw=.7));ax.add_patch(Circle((x,y),o['drill']/2,color='white',ec=c,lw=.3))
  else:ax.plot([x,xx],[y,yy],color=c,lw=o['width']*3,alpha=.9)
 ax.set_xlim(0,14);ax.set_ylim(94,70);ax.set_aspect('equal');ax.set_title(l);ax.grid(alpha=.15);ax.set_xlabel('mm')
axs[0].set_ylabel('Board y / mm');fig.suptitle('Single joint head / power topology: in-memory proposal only, NOFAB\nBlue DVP | orange AON | magenta camera SW | green GND; gray pads are display AABBs, not manufacturing outlines',fontsize=12)
fig.tight_layout(rect=[0,0,1,.95]);fig.savefig(D/'head_joint_plan.png',dpi=170)
