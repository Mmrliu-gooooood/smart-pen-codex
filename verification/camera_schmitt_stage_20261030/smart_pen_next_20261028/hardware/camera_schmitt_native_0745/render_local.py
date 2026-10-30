from pathlib import Path
import os
os.environ['XDG_CONFIG_HOME']='/tmp/schmitt-render0745';os.environ['MPLCONFIGDIR']='/tmp/schmitt-mpl0745'
import pcbnew as p,matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));fig,axs=plt.subplots(1,3,figsize=(18,7));colors={'GND':'#228833','3V3_AON':'#dd3322','ISO_GATE':'#0088aa','CAM_ISO_OE_N':'#aa3377'}
for ax,layer in zip(axs,[p.F_Cu,p.In3_Cu,p.B_Cu]):
 for t in b.GetTracks():
  a,z=t.GetStart(),t.GetEnd()
  if min(a.y,z.y)/1e6>73 or max(a.y,z.y)/1e6<66:continue
  col=colors.get(t.GetNetname(),'#999999')
  if isinstance(t,p.PCB_VIA):ax.add_patch(Circle((a.x/1e6,a.y/1e6),t.GetWidth(p.F_Cu)/2e6,fill=False,color=col,linewidth=1));continue
  if t.GetLayer()!=layer:continue
  ax.plot([a.x/1e6,z.x/1e6],[a.y/1e6,z.y/1e6],color=col,linewidth=t.GetWidth()/1e6*8,solid_capstyle='round')
 for f in b.GetFootprints():
  f.BuildCourtyardCaches()
  if layer in[p.F_Cu,p.B_Cu]:
   cy=f.GetCourtyard(p.F_CrtYd if layer==p.F_Cu else p.B_CrtYd)
   for j in range(cy.OutlineCount()):
    c=cy.COutline(j);xy=[(c.CPoint(i).x/1e6,c.CPoint(i).y/1e6)for i in range(c.PointCount())]
    if xy:ax.add_patch(Polygon(xy,fill=False,edgecolor='#666666',linestyle=':',linewidth=.6))
  for pad in f.Pads():
   x,y=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6
   if not 66<y<73 or not pad.IsOnLayer(layer):continue
   sh=p.SHAPE_POLY_SET();pad.TransformShapeToPolygon(sh,layer,0,50,p.ERROR_OUTSIDE)
   for j in range(sh.OutlineCount()):
    c=sh.COutline(j);xy=[(c.CPoint(i).x/1e6,c.CPoint(i).y/1e6)for i in range(c.PointCount())];ax.add_patch(Polygon(xy,color=colors.get(pad.GetNetname(),'#999999'),alpha=.35))
   ax.text(x,y,f.GetReference()+'.'+pad.GetNumber(),fontsize=6,ha='center',va='center',clip_on=True)
 ax.set(xlim=(.2,7),ylim=(73,66),aspect='equal',title=b.GetLayerName(layer)+' (top-view coordinates)',xlabel='mm');ax.grid(alpha=.2)
fig.suptitle('Schmitt experimental local candidate — NOFAB / NOPOWER\nRed AON, green GND, cyan ISO_GATE, purple OE; grey unrelated retained copper; dotted courtyards\nAll 4 through vias shown on every layer; no assembled/measured claim')
fig.tight_layout();fig.savefig(D/'local_after.png',dpi=160);fig.savefig(D/'local_after.svg')
