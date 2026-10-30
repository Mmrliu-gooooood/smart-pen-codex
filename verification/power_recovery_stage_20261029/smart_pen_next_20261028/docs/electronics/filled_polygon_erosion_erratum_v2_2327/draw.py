from pathlib import Path
import os
os.environ['XDG_CONFIG_HOME']='/tmp/gnd2305draw';os.environ['MPLCONFIGDIR']='/tmp/gnd2305mpl'
import pcbnew as p, matplotlib
from native_polygon import native_fractured_once
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle,PathPatch
from matplotlib.path import Path as MPath
D=Path(__file__).resolve().parent; R=D.parents[2]; S=R/'hardware/gnd_fixed_branch_candidate_2159';B=R/'hardware/aon_entry_bridge_candidate_2156'
fig,axs=plt.subplots(1,3,figsize=(12,7))
for ax,path,title in zip(axs,[B/'native/mainboard_revD.kicad_pcb',S/'native/mainboard_revD.kicad_pcb',R/'hardware/gnd_conservative_recovery_2305/native/mainboard_revD.kicad_pcb'],['Base: normalized (1 eroded piece)','18-branch comparison: normalized (1 piece)','17-branch candidate: normalized (1 piece)']):
 b=p.LoadBoard(str(path));z=next(z for z in b.Zones()if z.GetNetname()=='3V3_AON');q=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In2_Cu));q=native_fractured_once(q);a=p.SHAPE_POLY_SET(q);a.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 for poly,color in [(q,'#ffdcad'),(a,'#70a8ca')]:
  verts=[];codes=[]
  for i in range(poly.OutlineCount()):
   for h in range(-1,poly.HoleCount(i)):
    c=poly.COutline(i)if h<0 else poly.CHole(i,h);pts=[(c.CPoint(j).x/1e6,c.CPoint(j).y/1e6)for j in range(c.PointCount())]
    signed=sum(pts[j][0]*pts[(j+1)%len(pts)][1]-pts[(j+1)%len(pts)][0]*pts[j][1]for j in range(len(pts)))
    if (signed>0)!=(h<0):pts.reverse()
    verts+=pts+[pts[0]];codes+=[MPath.MOVETO]+[MPath.LINETO]*(len(pts)-1)+[MPath.CLOSEPOLY]
  ax.add_patch(PathPatch(MPath(verts,codes),facecolor=color,edgecolor='none'))
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   c=t.GetPosition();ax.add_patch(Circle((c.x/1e6,c.y/1e6),t.GetWidth(p.F_Cu)/2e6,fill=False,color='black',lw=.5))
 ax.add_patch(Rectangle((.75,66.790688),.373265,.25,fill=False,edgecolor='red',lw=1.2));ax.set_xlim(.3,4.8);ax.set_ylim(70.2,65.6);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(title,fontsize=9);ax.set_xlabel('board x / mm');ax.set_ylabel('board y / mm')
fig.suptitle('ERRATUM: raw fractured-polygon erosion was encoding-sensitive, not proof of an added neck\nOrange = normalized native copper; blue = normalized 0.25 mm erosion\nAll three AON shapes remain one eroded component. Still NOFAB; no ampacity claim or branch reinstatement.',fontsize=11);fig.tight_layout(rect=(0,0,1,.87));fig.savefig(D/'normalized_comparison.png',dpi=150)
