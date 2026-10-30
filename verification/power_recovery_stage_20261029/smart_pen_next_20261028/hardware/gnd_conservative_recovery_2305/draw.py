from pathlib import Path
import os
os.environ['XDG_CONFIG_HOME']='/tmp/gnd2305draw';os.environ['MPLCONFIGDIR']='/tmp/gnd2305mpl'
import pcbnew as p, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle
D=Path(__file__).resolve().parent; S=D.parent/'gnd_fixed_branch_candidate_2159';B=D.parent/'aon_entry_bridge_candidate_2156'
fig,axs=plt.subplots(1,3,figsize=(12,7))
for ax,path,title in zip(axs,[B/'native/mainboard_revD.kicad_pcb',S/'native/mainboard_revD.kicad_pcb',D/'native/mainboard_revD.kicad_pcb'],['Base: AON bridge only (7 eroded pieces)','Rejected: 18 GND branches (8 pieces)','Conservative: 17 branches (7 pieces)']):
 b=p.LoadBoard(str(path));z=next(z for z in b.Zones()if z.GetNetname()=='3V3_AON');q=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In2_Cu));a=p.SHAPE_POLY_SET(q);a.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 for poly,color in [(q,'#ffdcad'),(a,'#70a8ca')]:
  for i in range(poly.OutlineCount()):
   for h in range(-1,poly.HoleCount(i)):
    c=poly.COutline(i)if h<0 else poly.CHole(i,h);ax.add_patch(Polygon([(c.CPoint(j).x/1e6,c.CPoint(j).y/1e6)for j in range(c.PointCount())],color=color if h<0 else 'white',lw=0))
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   c=t.GetPosition();ax.add_patch(Circle((c.x/1e6,c.y/1e6),t.GetWidth(p.F_Cu)/2e6,fill=False,color='black',lw=.5))
 ax.add_patch(Rectangle((.75,66.790688),.373265,.25,fill=False,edgecolor='red',lw=1.2));ax.set_xlim(.3,4.8);ax.set_ylim(70.2,65.6);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(title,fontsize=9);ax.set_xlabel('board x / mm');ax.set_ylabel('board y / mm')
fig.suptitle('NOFAB: whole group 37 withdrawn, not trimmed\nOrange = actual AON fill; blue = 0.25 mm geometric erosion, NOT ampacity qualification\nRemoved group: C207.2/U204.4, 14 objects; retained candidate 0 violations / 203 unconnected / 0 parity',fontsize=11);fig.tight_layout(rect=(0,0,1,.87));fig.savefig(D/'aon_neck_comparison.png',dpi=150)
