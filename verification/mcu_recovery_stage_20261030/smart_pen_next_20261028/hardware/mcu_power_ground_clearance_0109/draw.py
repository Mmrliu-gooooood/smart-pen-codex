from pathlib import Path
import os
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcudraw0109';os.environ['MPLCONFIGDIR']='/tmp/pen-mcudraw0109mpl'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle
D=Path(__file__).resolve().parent;old=D.parent/'mcu_power_ground_candidate_0043/native/mainboard_revD.kicad_pcb';new=D/'native/mainboard_revD.kicad_pcb';fig,axes=plt.subplots(1,3,figsize=(14,6))
for ax,f,l,title in zip(axes,[old,new,new],[p.B_Cu,p.B_Cu,p.F_Cu],['Rejected: old EP via overlaps C504.2 (B.Cu)','Successor: via moved + F ground link (B.Cu)','Successor: actual F.Cu supply / EP copper']):
 b=p.LoadBoard(str(f))
 for fp in b.GetFootprints():
  for q in fp.Pads():
   if not q.IsOnLayer(l):continue
   c=q.GetPosition()
   if not(1<c.x/1e6<11 and 4<c.y/1e6<15):continue
   poly=p.SHAPE_POLY_SET();q.TransformShapeToPolygon(poly,l,0,100,p.ERROR_INSIDE)
   col='#40a779'if q.GetNetname()=='GND'else '#d98345'if q.GetNetname()=='3V3_AON'else'#b0b6bd'
   for i in range(poly.OutlineCount()):
    z=poly.COutline(i);ax.add_patch(Polygon([(z.CPoint(j).x/1e6,z.CPoint(j).y/1e6)for j in range(z.PointCount())],facecolor=col,edgecolor='black',lw=.25,alpha=.7))
   if fp.GetReference()=='C504':ax.text(c.x/1e6,c.y/1e6,q.GetNumber(),ha='center',va='center',fontsize=9)
 for t in b.GetTracks():
  c=t.GetStart();e=t.GetEnd()
  if not t.IsOnLayer(l)or not(1<c.x/1e6<11 and 4<c.y/1e6<15):continue
  col='#137d51'if t.GetNetname()=='GND'else'#d3482f'if t.GetNetname()=='3V3_AON'else'#949ca8'
  if isinstance(t,p.PCB_VIA):
   ax.add_patch(Circle((c.x/1e6,c.y/1e6),t.GetWidth(p.F_Cu)/2e6,facecolor=col,edgecolor='black',lw=.5));ax.add_patch(Circle((c.x/1e6,c.y/1e6),t.GetDrillValue()/2e6,facecolor='white',edgecolor='black',lw=.25))
  else:
   poly=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(poly,l,0,100,p.ERROR_INSIDE)
   for i in range(poly.OutlineCount()):
    z=poly.COutline(i);ax.add_patch(Polygon([(z.CPoint(j).x/1e6,z.CPoint(j).y/1e6)for j in range(z.PointCount())],facecolor=col,edgecolor='none'))
 if l==p.B_Cu:
  ax.add_patch(Rectangle((3.025,9.275),2.45,.95,fill=False,edgecolor='#d3272a',ls='--',lw=1));ax.set_xlim(2.7,6.8);ax.set_ylim(12,8);ax.text(3.1,8.65,'Dashed: full C504 pad-union XY budget',fontsize=8)
 else:ax.set_xlim(1.7,10.3);ax.set_ylim(14.6,5.5)
 ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_title(title,fontsize=9);ax.set_xlabel('board x / mm');ax.set_ylabel('board y / mm')
fig.suptitle('NOFAB — actual native copper, not fabrication approval\n0 violations / 181 unconnected / 0 parity; 0.254 mm local supply fanout, nine ground EP terminals connected\nEight vias still in EP solder lands; relocated drill has only 23.8 um nominal top-pad edge margin',fontsize=11);fig.tight_layout(rect=(0,0,1,.85));fig.savefig(D/'native_mcu_comparison.png',dpi=160)
