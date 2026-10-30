from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/groundrender0818';os.environ['MPLCONFIGDIR']='/tmp/groundrender0818-mpl'
import pcbnew as p,matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());ids=set(m['added']);targets={'R222.1','R223.1','U203.5','U203.6'}
fig,axs=plt.subplots(1,2,figsize=(12,7),squeeze=False)
for row,(lo,hi)in enumerate([(51,62)]):
 for col,l in enumerate([p.F_Cu,p.B_Cu]):
  ax=axs[row,col]
  for t in b.GetTracks():
   a,z=t.GetStart(),t.GetEnd()
   if min(a.y,z.y)/1e6>hi or max(a.y,z.y)/1e6<lo:continue
   new=t.m_Uuid.AsString()in ids;color='#007744'if new else'#bbbbbb'
   if isinstance(t,p.PCB_VIA):ax.add_patch(Circle((a.x/1e6,a.y/1e6),t.GetWidth(p.F_Cu)/2e6,fill=False,color=color,linewidth=1.3 if new else .5));continue
   if t.GetLayer()!=l:continue
   sh=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(sh,l,0,50,p.ERROR_OUTSIDE)
   for j in range(sh.OutlineCount()):
    ch=sh.COutline(j);xy=[(ch.CPoint(i).x/1e6,ch.CPoint(i).y/1e6)for i in range(ch.PointCount())];ax.add_patch(Polygon(xy,color=color))
  for f in b.GetFootprints():
   for d in f.Pads():
    x,y=d.GetPosition().x/1e6,d.GetPosition().y/1e6
    if not lo<y<hi or not d.IsOnLayer(l):continue
    sh=p.SHAPE_POLY_SET();d.TransformShapeToPolygon(sh,l,0,50,p.ERROR_OUTSIDE)
    for j in range(sh.OutlineCount()):
     ch=sh.COutline(j);xy=[(ch.CPoint(i).x/1e6,ch.CPoint(i).y/1e6)for i in range(ch.PointCount())];ax.add_patch(Polygon(xy,color='#77bb99'if d.GetNetname()=='GND'else'#999999',alpha=.35))
    name=f.GetReference()+'.'+d.GetNumber()
    if name in targets:ax.text(x,y,name,fontsize=6,ha='center',va='center',clip_on=True)
   if f.GetReference()in['U202','U203']:
    for it in f.GraphicalItems():
     if not isinstance(it,p.PCB_SHAPE)or it.GetLayer()!=(p.F_Fab if l==p.F_Cu else p.B_Fab):continue
     a,z=it.GetStart(),it.GetEnd();x,y,w,h=a.x/1e6,a.y/1e6,(z.x-a.x)/1e6,(z.y-a.y)/1e6
     if it.GetShape()==0:ax.plot([x,x+w],[y,y+h],color='#bb4477',linewidth=.7)
     elif it.GetShape()==1:ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='#bb4477',linestyle=':'))
  for budget in json.loads((D/'installation_obstacles.json').read_text()):
   if budget['ref']in ['C206','J104'] and budget['side']==b.GetLayerName(l):
    x0,y0,x1,y1=budget['xy_bounds'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,edgecolor='#d47700',linestyle='--',linewidth=1));ax.text(x0,y0,budget['ref']+' retained budget',fontsize=7,color='#b36600')
  ax.set(xlim=(2,12.5),ylim=(hi,lo),aspect='equal',title=b.GetLayerName(l)+' / y='+str(lo)+'..'+str(hi)+' mm');ax.grid(alpha=.15)
fig.suptitle('Known-control-input bias routing — NOFAB / NOPOWER\nGreen=new bias copper; grey=retained. Pink=U202/U203 Fab outlines.\nR104 RF strap and J202 six grounds deliberately remain unresolved.');fig.tight_layout(rect=(0,0,1,.94));fig.savefig(D/'group_views.png',dpi=170);fig.savefig(D/'group_views.svg')
