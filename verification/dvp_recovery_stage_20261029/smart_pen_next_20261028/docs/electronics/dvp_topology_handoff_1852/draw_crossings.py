from pathlib import Path
import os,json
os.environ['MPLCONFIGDIR']='/tmp/pen-mpl';os.environ['XDG_CACHE_HOME']='/tmp/pen-layout-cache'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parent;r=json.loads((D/'topology.json').read_text())['rows'];fig,axs=plt.subplots(1,3,figsize=(11,14));palette=plt.get_cmap('tab10')
for ax,layer in zip(axs,['F.Cu','In3.Cu','B.Cu']):
 group=[q for q in r if q['proposed_layer']==layer]
 for i,q in enumerate(group):
  sx,sy=q['rotated_unselected_xy'];x=q['proposed_lane_x'];hx,hy=q['J202_xy'];col=palette(i)
  ax.plot([sx,x,x,hx],[sy,64,86,hy],ls='--',color=col,lw=1.3,label=q['net'].replace('SENS_',''))
  ax.plot(sx,sy,'o',mfc='white',mec=col);ax.text(sx,sy-1.2,q['translator_pin'],fontsize=7,ha='center',va='bottom',rotation=90,color=col)
  ax.plot(hx,hy,'s',mfc='white',mec=col);ax.text(hx,hy+1.3,q['J202_pin'],fontsize=7,ha='center',color=col)
 ax.text(7,76,'DASHED EDGES ARE\nCONNECTIVITY ONLY\nNOT TRACKS',ha='center',fontsize=8,color='#555')
 ax.axhspan(86,94,alpha=.06,color='orange');ax.text(7,95,'J202: all B.Cu',ha='center',fontsize=9)
 ax.set_xlim(0,14);ax.set_ylim(98,29);ax.set_title(layer+' role',weight='bold');ax.set_xlabel('PCB X mm');ax.set_ylabel('PCB Y mm (rotated, UNSELECTED)');ax.grid(alpha=.2);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.04),ncol=2,fontsize=9)
 if layer=='F.Cu':msg='Source F → F corridor\nHead transition F → B REQUIRED'
 elif layer=='In3.Cu':msg='Source F → In3 REQUIRED\nHead transition In3 → B REQUIRED'
 else:msg='Source F → B REQUIRED\nHead is B; fanout still must be planned'
 ax.text(7,31,msg,ha='center',va='top',fontsize=9)
fig.suptitle('NOFAB — layer-separated endpoint / crossover planning\nIntersections shown are projected connectivity, not shorts or routed crossings.\nCorner locations (Y64/86) are illustrative, not selected copper or via coordinates.',fontsize=11);fig.tight_layout(rect=[0,.02,1,.94]);fig.savefig(D/'layer_endpoint_crossovers.png',dpi=140)
