from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
from copper_geometry import shape,L
D=Path(__file__).resolve().parent;a=p.LoadBoard(str(D.parent/'imu_irq_layered_candidate/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));xy=lambda v:[v.x/1e6,v.y/1e6]
def stats(b,n):
 ts=[t for t in b.GetTracks()if t.GetNetname()==n and not isinstance(t,p.PCB_VIA)];vs=[t for t in b.GetTracks()if t.GetNetname()==n and isinstance(t,p.PCB_VIA)];return{'tracks':len(ts),'vias':len(vs),'length_mm':sum(t.GetLength()/1e6 for t in ts),'short_tracks_below_0p1_mm':sum(t.GetLength()<100000 for t in ts),'minimum_track_mm':min((t.GetLength()/1e6 for t in ts),default=0)}
nets=['AON_I2C_SCL','AON_I2C_SDA','CAM_PWDN_UART_RX','CAM_D0','CAM_D1','CAM_D2','CAM_D3','CAM_D4','CAM_D5','CAM_D6','CAM_D7','CAM_PCLK','CAM_HREF','CAM_VSYNC','CAM_XCLK']
ns={n:{'before':stats(a,n),'after':stats(b,n)}for n in nets}
planes={}
for key,brd in [('before',a),('after',b)]:
 for l in [p.In1_Cu,p.In2_Cu,p.In4_Cu]:
  q=p.SHAPE_POLY_SET()
  for z in brd.Zones():
   if not z.GetIsRuleArea()and z.IsOnLayer(l):q.BooleanAdd(z.GetFilledPolysList(l))
  planes[key,l]=q
pd={}
for l in [p.In1_Cu,p.In2_Cu,p.In4_Cu]:
 x,z=planes['before',l],planes['after',l];lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(x,z);gained=p.SHAPE_POLY_SET();gained.BooleanSubtract(z,x);pd[b.GetLayerName(l)]={'before_mm2':x.Area()/1e12,'after_mm2':z.Area()/1e12,'lost_mm2':lost.Area()/1e12,'gained_mm2':gained.Area()/1e12}
rows=[]
for key,brd in [('before',a),('after',b)]:
 for t in brd.GetTracks():
  if isinstance(t,p.PCB_VIA)or t.GetNetname()not in ['AON_I2C_SCL','AON_I2C_SDA','CAM_D0','CAM_D7','CAM_PWDN_UART_RX']:continue
  l=t.GetLayer();ref=p.In1_Cu if l==p.F_Cu else p.In4_Cu;q=shape(t,l);ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(q,planes[key,ref]);aa,zz=xy(t.GetStart()),xy(t.GetEnd());length=t.GetLength()/1e6;steps=max(1,math.ceil(length/.005));runs=[];start=None
  for i in range(steps):
   u=(i+.5)/steps;v=p.VECTOR2I(round((aa[0]+u*(zz[0]-aa[0]))*1e6),round((aa[1]+u*(zz[1]-aa[1]))*1e6));inside=planes[key,ref].Contains(v)
   if not inside and start is None:start=i
   if inside and start is not None:runs.append((i-start)*length/steps);start=None
  if start is not None:runs.append((steps-start)*length/steps)
  rows.append({'version':key,'net':t.GetNetname(),'uuid':t.m_Uuid.AsString(),'layer':brd.GetLayerName(l),'a':aa,'z':zz,'ref':brd.GetLayerName(ref),'length_mm':length,'uncovered_area_mm2':(q.Area()-ix.Area())/1e12,'segment_gaps_mm':runs})
viarefs=[]
gv=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND']
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA)or t.GetNetname()not in ['AON_I2C_SCL','AON_I2C_SDA']:continue
 vv=sorted(gv,key=lambda v:math.dist(xy(v.GetPosition()),xy(t.GetPosition())))[:2];viarefs.append({'net':t.GetNetname(),'uuid':t.m_Uuid.AsString(),'xy':xy(t.GetPosition()),'nearest_GND':[{'xy':xy(v.GetPosition()),'distance':math.dist(xy(v.GetPosition()),xy(t.GetPosition()))}for v in vv]})
out={'status':'GEOMETRY_SCREEN_NOT_TIMING_PI_OR_EMI_QUALIFICATION','net_stats':ns,'plane_delta':pd,'new_signal_via_return':viarefs,'per_segment_projection':rows,'sampling_mm':.005,'sampling_gap_error_mm':.010};(D/'measurements.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='per_segment_projection'},indent=2))
