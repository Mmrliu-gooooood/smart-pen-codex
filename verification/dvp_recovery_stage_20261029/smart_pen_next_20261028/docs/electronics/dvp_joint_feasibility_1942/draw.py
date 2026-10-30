from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-analytic';os.environ['MPLCONFIGDIR']='/tmp/pen-analytic-mpl'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
D=Path(__file__).resolve().parent;R=D.parents[2];b=p.LoadBoard(str(R/'hardware/dvp_rotated_group_placement_1835/native/mainboard_revD.kicad_pcb'));r=json.loads((D/'result.json').read_text());fig,axs=plt.subplots(1,3,figsize=(12,16));changes=json.loads((D/'placement_delta.json').read_text())
for f in b.GetFootprints():
 if f.GetReference() in changes:
  q=changes[f.GetReference()]['after']
  if b.GetLayerName(f.GetLayer())!=q['layer']:f.Flip(f.GetPosition(),False)
  f.SetPosition(p.VECTOR2I(*(round(v*1e6) for v in q['xy'])));f.SetOrientationDegrees(q['angle'])
nets=[q['net'] for q in r['routes']];colors={n:plt.get_cmap('tab20')(i) for i,n in enumerate(nets)}
for ax,layer in zip(axs,['F.Cu','In3.Cu','B.Cu']):
 lid=b.GetLayerID(layer)
 for f in b.GetFootprints():
  for q in f.Pads():
   if q.IsOnLayer(lid):
    box=q.GetBoundingBox();ax.add_patch(plt.Rectangle((box.GetX()/1e6,box.GetY()/1e6),box.GetWidth()/1e6,box.GetHeight()/1e6,color='#bbbbbb',alpha=.55));
 for g in r['geometry']:
  if g['type']=='via':ax.add_patch(Circle(g['start'],.225,fill=False,color=colors[g['net']],lw=.8))
  elif g['layer']==layer:ax.plot([g['start'][0],g['end'][0]],[g['start'][1],g['end'][1]],color=colors[g['net']],lw=1)
 for c in r['pad_clearance_conflicts']:
  if c['layer']==layer:
   f=next(f for f in b.GetFootprints() if f.GetReference()==c['ref']);q=next(q for q in f.Pads() if q.GetNumber()==c['pad']);x,y=q.GetPosition().x/1e6,q.GetPosition().y/1e6;ax.scatter(x,y,marker='x',color='red',s=22)
 ax.set_title(layer+' — RED X = actual pad blockers');ax.set_xlim(0,14);ax.set_ylim(94,28);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('X mm')
axs[0].set_ylabel('Y mm');fig.suptitle('NOFAB / analytic 12-net topology only\n76 hypothetical objects: mutual copper-clearance 0; actual pad conflicts 0; SIX REFS RELOCATED\nOld copper removed in input placement; power/returns/remaining 274 connections NOT validated')
fig.tight_layout(rect=(0,0,1,.94));fig.savefig(D/'joint_feasibility.png',dpi=130)
