from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/transdraw0130';os.environ['MPLCONFIGDIR']='/tmp/transdraw0130mpl'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));fig,axs=plt.subplots(1,4,figsize=(17,5));colors={'GND':'#168255','3V3_AON':'#d35c2c','SENS_VIO_1V8':'#3268c9'}
for ax,(lo,hi,label)in zip(axs,[(29,39,'U201 / C201–202'),(41,51,'U202 / C203–204'),(51,61,'U203 / C205–206'),(62,68,'U204 / exchanged C207–208')]):
 for f in b.GetFootprints():
  for q in f.Pads():
   if not q.IsOnLayer(p.F_Cu)or not lo-.5<q.GetPosition().y/1e6<hi+.5:continue
   poly=p.SHAPE_POLY_SET();q.TransformShapeToPolygon(poly,p.F_Cu,0,100,p.ERROR_INSIDE)
   for i in range(poly.OutlineCount()):
    z=poly.COutline(i);ax.add_patch(Polygon([(z.CPoint(j).x/1e6,z.CPoint(j).y/1e6)for j in range(z.PointCount())],facecolor=colors.get(q.GetNetname(),'#b8bdc7'),edgecolor='#555',lw=.25,alpha=.8))
   if f.GetReference()in['C201','C202','C203','C204','C205','C206','C207','C208']:ax.text(q.GetPosition().x/1e6,q.GetPosition().y/1e6,f.GetReference()+'.'+q.GetNumber(),fontsize=5,ha='center',va='center')
 for t in b.GetTracks():
  if not t.IsOnLayer(p.F_Cu):continue
  if min(t.GetStart().y,t.GetEnd().y)/1e6>hi or max(t.GetStart().y,t.GetEnd().y)/1e6<lo:continue
  c=t.GetStart();col=colors.get(t.GetNetname(),'#aaa')
  if isinstance(t,p.PCB_VIA):
   ax.add_patch(Circle((c.x/1e6,c.y/1e6),t.GetWidth(p.F_Cu)/2e6,facecolor=col,ec='black',lw=.2));ax.add_patch(Circle((c.x/1e6,c.y/1e6),t.GetDrillValue()/2e6,facecolor='white',ec='black',lw=.2))
  else:
   poly=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(poly,p.F_Cu,0,100,p.ERROR_INSIDE)
   for i in range(poly.OutlineCount()):
    z=poly.COutline(i);ax.add_patch(Polygon([(z.CPoint(j).x/1e6,z.CPoint(j).y/1e6)for j in range(z.PointCount())],facecolor=col,ec='none'))
 ax.set_xlim(.5,13.8);ax.set_ylim(hi,lo);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(label,fontsize=9);ax.set_xlabel('x / mm');ax.set_ylabel('y / mm')
fig.suptitle('NOFAB: actual F.Cu local translator-domain candidate, 0 / 149 / 0\nOrange=AON; blue=SENS reference; green=ground. SENS J202.23 input still isolated.\nCaps C207/C208 exchanged with source net identities unchanged. No electrical/thermal manufacturing qualification.',fontsize=11);fig.tight_layout(rect=(0,0,1,.89));fig.savefig(D/'native_local_domains.png',dpi=160)
