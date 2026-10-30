from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/"docs/electronics/remaining_power_return_plan_0208"))
import contextlib,io
with contextlib.redirect_stdout(io.StringIO()):import plan as q
import os
os.environ['MPLCONFIGDIR']='/tmp/power0208-mpl'
os.environ['XDG_CACHE_HOME']='/tmp/power0208-cache'
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle
p=q.p
b=p.LoadBoard(str(D/"native/mainboard_revD.kicad_pcb"));m=json.loads((D/"materialization.json").read_text());q.gate3=[t for t in b.GetTracks()if q.uid(t)in m["added"]]
fig,axes=plt.subplots(1,1,figsize=(8,9));axes=[axes]
def plot(ax,obj,layer,color,alpha=.65):
 poly=q.shape(obj,layer)
 for i in range(poly.OutlineCount()):
  ch=poly.COutline(i);coords=[(ch.CPoint(j).x/1e6,ch.CPoint(j).y/1e6)for j in range(ch.PointCount())]
  ax.add_patch(Polygon(coords,closed=True,facecolor=color,edgecolor='none',alpha=alpha))
 if isinstance(obj,p.PCB_VIA):
  x,y=q.xy(obj);ax.add_patch(Circle((x,y),obj.GetDrillValue()/2e6,color='white',zorder=10))
for ax,layer,extent,title,model in [(axes[0],p.B_Cu,(2,13,61.5,76),'Gate input / returns: native seven objects',q.gate3)]:
 for t in q.old:
  if t.IsOnLayer(layer):plot(ax,t,layer,'#999999')
 for pad in q.pads:
  if pad.IsOnLayer(layer):plot(ax,pad,layer,'#555555')
 for t in model:
  if t.IsOnLayer(layer):plot(ax,t,layer,'#d72e2e'if t.GetNetname()=='3V3_AON'else'#087f5b',.9)
 for name in (['U301.1','U301.2','C301.1','C302.2','C303.2','R301.2']if layer==p.B_Cu else['U101.2','U101.3','C103.1']):
  x,y=q.xy(q.pm[name]);ax.text(x+.08,y-.15,name,fontsize=8,color='black',bbox=dict(facecolor='white',alpha=.7,pad=.3,edgecolor='none'))
 ax.set_xlim(extent[0],extent[1]);ax.set_ylim(extent[3],extent[2]);ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_title(title);ax.set_xlabel('PCB X (mm)');ax.set_ylabel('PCB Y (mm)')
fig.suptitle('NATIVE CANDIDATE / NOFAB / NOPOWER - 0/137/0 DRC, not hardware qualification',fontsize=11)
fig.tight_layout();fig.savefig(D/'native_view.png',dpi=160)
