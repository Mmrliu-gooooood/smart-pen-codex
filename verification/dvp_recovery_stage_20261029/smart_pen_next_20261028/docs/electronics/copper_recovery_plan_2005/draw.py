from pathlib import Path
import json,os
os.environ['MPLCONFIGDIR']='/tmp/pen-recovery2005-mpl';os.environ['XDG_CONFIG_HOME']='/tmp/pen-recovery2005-config'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];r=json.loads((D/'recovery_plan.json').read_text());b=p.LoadBoard(str(R/'hardware/dvp_mechanical_clearance_successor_1957/native/mainboard_revD.kicad_pcb'));fig,axs=plt.subplots(1,3,figsize=(12,15))
for ax,layer in zip(axs,['F.Cu','In2.Cu','B.Cu']):
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   q=t.GetPosition();ax.add_patch(Circle((q.x/1e6,q.y/1e6),.225,color='#709ccc',alpha=.35))
  elif b.GetLayerName(t.GetLayer())==layer:ax.plot([t.GetStart().x/1e6,t.GetEnd().x/1e6],[t.GetStart().y/1e6,t.GetEnd().y/1e6],color='#709ccc',lw=.8,alpha=.4)
 for o in r['objects']:
  if o['net']not in ['3V3_AON','GND','CAM_3V3_SW','CAM_3V3_PRELINK']:continue
  if o['layer']not in [layer,'through']:continue
  color='#198849'if o['geometry_candidate']else'#cf2323'
  if o['type']=='via':ax.add_patch(Circle(o['start_mm'],o['width_mm']/2,fill=False,color=color,lw=.7))
  else:ax.plot([o['start_mm'][0],o['end_mm'][0]],[o['start_mm'][1],o['end_mm'][1]],color=color,lw=max(.4,o['width_mm']*3))
 ax.set_xlim(-.5,14.5);ax.set_ylim(96,-1);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(layer);ax.set_xlabel('X mm')
axs[0].set_ylabel('Y mm');fig.suptitle('READ-ONLY POWER COPPER RECOVERY PLAN — NO COPPER RESTORED\nGreen: old power/GND objects clear of screened additions; red: new conflict / original hazard\nBlue: actual f92c 12 signal chains. Plane fills OMITTED; green is NOT whole-net connectivity.')
fig.tight_layout(rect=(0,0,1,.94));fig.savefig(D/'power_recovery_map.png',dpi=130)
