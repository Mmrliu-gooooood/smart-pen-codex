from pathlib import Path
import os,json,hashlib,csv
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config';os.environ['XDG_CACHE_HOME']='/tmp/pen-layout-cache';os.environ['MPLCONFIGDIR']='/tmp/pen-mpl'
import pcbnew as p,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';B=R/'hardware/dvp_rotated_group_placement_1835/native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(A));b=p.LoadBoard(str(B));xy=lambda q:[q.GetPosition().x/1e6,q.GetPosition().y/1e6]
names=[f'SENS_D{i}'for i in range(8)]+['SENS_PCLK','SENS_VSYNC','SENS_HREF','SENS_EXTCLK'];rows=[]
for i,n in enumerate(names):
 ref='U201'if i<8 else 'U202'if i<11 else 'U203'
 def pad(board,ref):return next(q for f in board.GetFootprints()if f.GetReference()==ref for q in f.Pads()if q.GetNetname()==n)
 pa,pb,pj=pad(a,ref),pad(b,ref),pad(a,'J202')
 layer='F.Cu'if i<4 else'In3.Cu'if i<8 else'B.Cu';lane=[13.5,13.2,12.9,12.6][i%4]if i<4 or i>=8 else[1.4,1.1,.8,.5][i-4]
 rows.append({'net':n,'direction':'MCU to camera'if i==11 else'camera to MCU','translator_pin':ref+'.'+pa.GetNumber(),'accepted_xy':xy(pa),'rotated_unselected_xy':xy(pb),'J202_pin':pj.GetNumber(),'J202_xy':xy(pj),'proposed_layer':layer,'proposed_lane_x':lane,'status':'planning only; left lane and both end fanouts NOT routed'})
# Exact native finite copper obstacles on the proposed left In3 trunks.
def shape(o,l):
 q=p.SHAPE_POLY_SET();o.TransformShapeToPolygon(q,l,0,50,p.ERROR_OUTSIDE);return q
def hits(x,y):
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(x,y);return q.Area()>1
left=[]
for x in [.5,.8,1.1,1.4]:
 t=p.PCB_TRACK(a);t.SetStart(p.VECTOR2I(round(x*1e6),38000000));t.SetEnd(p.VECTOR2I(round(x*1e6),89000000));t.SetWidth(449998);t.SetLayer(p.In3_Cu);s=shape(t,p.In3_Cu);h=[]
 for v in a.GetTracks():
  if v.IsOnLayer(p.In3_Cu)and hits(s,shape(v,p.In3_Cu)):h.append({'uuid':v.m_Uuid.AsString(),'net':v.GetNetname(),'type':'via'if isinstance(v,p.PCB_VIA)else'track'})
 left.append({'x':x,'layer':'In3.Cu','y':[38,89],'width':.15,'clearance':.15,'blocking_objects':h})
out={'accepted_pcb_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'unselected_placement_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'rows':rows,'left_corridor_readonly_native_scan':left,'no_native_modification':True}
(D/'topology.json').write_text(json.dumps(out,indent=2)+'\n')
with (D/'pin_order_and_lanes.csv').open('w')as f:
 w=csv.writer(f);w.writerow(['net','direction','translator_pin','accepted_x','accepted_y','rotated_x','rotated_y','J202_pin','head_x','head_y','proposed_layer','proposed_x','status'])
 for r in rows:w.writerow([r['net'],r['direction'],r['translator_pin'],*r['accepted_xy'],*r['rotated_unselected_xy'],r['J202_pin'],*r['J202_xy'],r['proposed_layer'],r['proposed_lane_x'],r['status']])
fig,axs=plt.subplots(1,2,figsize=(15,8))
colors={'F.Cu':'#b53435','In3.Cu':'#6b46a2','B.Cu':'#1978a5'}
ax=axs[0]
for i,r in enumerate(rows):
 y=11-i;col=colors[r['proposed_layer']];ax.text(0,y,r['net'].replace('SENS_',''),fontsize=9,va='center',color=col);ax.text(2,y,r['translator_pin'],fontsize=9,va='center');ax.text(4,y,str(tuple(r['rotated_unselected_xy'])),fontsize=8,va='center');ax.text(8,y,'J202.'+r['J202_pin']+' @ '+str(tuple(r['J202_xy'])),fontsize=8,va='center')
ax.set_xlim(0,13);ax.set_ylim(-1,13);ax.axis('off');ax.text(0,12.4,'Net*',weight='bold');ax.text(2,12.4,'Translator',weight='bold');ax.text(4,12.4,'Rotated endpoint (mm)',weight='bold');ax.text(8,12.4,'Head endpoint (mm)',weight='bold');ax.set_title('Exact native pin identity; rotated layout is UNSELECTED')
ax.text(0,-.8,'* 11 inputs camera→MCU; EXTCLK travels MCU→camera.\nCoordinates are physical; this table does not depict copper routes.',fontsize=9)
ax=axs[1]
for r in rows:
 x=r['proposed_lane_x'];l=r['proposed_layer'];col=colors[l];offset=-.035 if l=='F.Cu'else .035 if l=='B.Cu'else 0
 ax.plot([x+offset]*2,[38,89],color=col,lw=2,ls='--'if l=='B.Cu'else'-');ax.text(x+offset,27 if l=='B.Cu'else 36,r['net'].replace('SENS_','')+' '+l,rotation=90,ha='center',va='bottom',fontsize=8,color=col)
ax.add_patch(Rectangle((0,38),14,51,fill=False,edgecolor='#444'));ax.add_patch(Rectangle((.05,90),13.9,4,fill=False,edgecolor='#444',ls=':'));ax.text(7,92,'J202: all 12 endpoints are B.Cu\nLayer changes / row fanout still required',ha='center',va='center',fontsize=9)
ax.text(6.7,58,'PLAN ONLY\nLeft In3 has existing\ncopper / via blockers.\nNo route imported.\n\nRight F/B sharing X\ndoes NOT allow a via\nthrough both nets.',ha='center',fontsize=10)
ax.set_xlim(-.3,14.3);ax.set_ylim(96,17);ax.set_xlabel('PCB X (mm); tiny F/B visual offset only');ax.set_ylabel('PCB Y (mm)');ax.set_title('Split-left/right lane allocation for MANUAL review');ax.grid(alpha=.2)
fig.suptitle('NOFAB — topology handoff, not a routed PCB or SI approval');fig.tight_layout();fig.savefig(D/'pin_order_lane_plan.png',dpi=150)
print(json.dumps({'left_blockers':[(v['x'],len(v['blocking_objects']),sorted(set(t['net']for t in v['blocking_objects'])))for v in left]},indent=2))
