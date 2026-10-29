from pathlib import Path
import os
D=Path(__file__).resolve().parent;R=D.parent
for k,s in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:os.environ[k]=str(D/'xdg'/s)
import pcbnew as p,numpy as np,json,math,hashlib,collections
from PIL import Image,ImageDraw
from scipy import ndimage
S=40;SHAPE=(3801,481)
def xy(v):return(p.ToMM(v.x),p.ToMM(v.y))
def mask(b,layer,net):
 im=Image.new('1',(SHAPE[1],SHAPE[0]));d=ImageDraw.Draw(im)
 for z in b.Zones():
  if z.GetLayer()!=layer or z.GetNetname()!=net:continue
  poly=z.GetFilledPolysList(layer)
  for i in range(poly.OutlineCount()):
   c=poly.COutline(i);d.polygon([(round(xy(c.CPoint(j))[0]*S),round(xy(c.CPoint(j))[1]*S)) for j in range(c.PointCount())],fill=1)
   for hi in range(poly.HoleCount(i)):
    c=poly.CHole(i,hi);d.polygon([(round(xy(c.CPoint(j))[0]*S),round(xy(c.CPoint(j))[1]*S)) for j in range(c.PointCount())],fill=0)
 return np.array(im,dtype=bool)
def near(labels,points,r=.45):
 hits=set()
 for x,y in points:
  cx,cy=round(x*S),round(y*S);q=round(r*S)
  for iy in range(cy-q,cy+q+1):
   for ix in range(cx-q,cx+q+1):
    if 0<=iy<SHAPE[0] and 0<=ix<SHAPE[1] and (iy-cy)**2+(ix-cx)**2<=q*q and labels[iy,ix]:hits.add(int(labels[iy,ix]))
 return hits
def erosion(a):
 dist=ndimage.distance_transform_edt(a)/S;rows=[]
 for radius in [0,.05,.075,.1,.125,.15,.2,.25]:
  lab,n=ndimage.label(a if radius==0 else dist>radius)
  rows.append({'radius_mm':radius,'regions':int(n),'input_to_upper_bridge':bool(near(lab,[(6.1,82.4),(6.9,82.4)])&near(lab,[(9.35,22.95)]))})
 return rows
boards={};masks={};out={}
for label,dir in [('HREF3','mainboard_href3_candidate'),('HREF2','mainboard_href2_candidate')]:
 f=R/dir/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));boards[label]=b;masks[label]={n:mask(b,l,n) for n,l in [('3V3_AON',p.In2_Cu),('GND',p.In1_Cu)]}
 c=next(f for f in b.GetFootprints() if f.GetReference()=='C201')
 out[label]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'C201':{'value':c.GetValue(),'footprint':str(c.GetFPID().GetLibNickname())+':'+str(c.GetFPID().GetLibItemName()),'pads':[{'number':a.GetNumber(),'net':a.GetNetname(),'xy_mm':xy(a.GetPosition()),'size_mm':xy(a.GetSize())} for a in c.Pads()]},'AON_erosion_screen':erosion(masks[label]['3V3_AON'])}
 Image.fromarray((masks[label]['3V3_AON']*255).astype('uint8')).save(D/(label+'_AON.png'))
regions={'existing_SCL_SDA_neck':(0,51.7,12,56.8),'new_inner_HREF_corridor':(0,37.8,12,43),'C201_region':(0,30.5,3.5,35.5)};diff={}
for net in ['3V3_AON','GND']:
 a=masks['HREF3'][net];b=masks['HREF2'][net];rows=[]
 for name,(x0,y0,x1,y1) in regions.items():
  old=a[round(y0*S):round(y1*S)+1,round(x0*S):round(x1*S)+1];new=b[round(y0*S):round(y1*S)+1,round(x0*S):round(x1*S)+1]
  rows.append({'region':name,'bbox_mm':[x0,y0,x1,y1],'lost_copper_pixels':int(np.sum(old&~new)),'gained_copper_pixels':int(np.sum(~old&new)),'pixel_area_mm2':1/S**2,'identical_at_25um':bool(np.array_equal(old,new))})
 diff[net]=rows
out['regional_plane_changes']=diff
# Native polygon Contains, independent of raster, tests centerline projection onto actual GND/In1.
a=boards['HREF3'];b=boards['HREF2'];old={t.m_Uuid.AsString():t for t in a.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()};added=[t for k,t in new.items() if k not in old]
def projection(board,tracks):
 zones=[z.GetFilledPolysList(p.In1_Cu) for z in board.Zones() if z.GetLayer()==p.In1_Cu and z.GetNetname()=='GND'];rows=[]
 for t in tracks:
  if isinstance(t,p.PCB_VIA) or t.GetNetname()=='GND':continue
  start,end=xy(t.GetStart()),xy(t.GetEnd());length=p.ToMM(t.GetLength());n=max(1,math.ceil(length/.025));miss=[]
  for f in np.linspace(0,1,n+1):
   x=start[0]+f*(end[0]-start[0]);y=start[1]+f*(end[1]-start[1]);point=p.VECTOR2I(p.FromMM(float(x)),p.FromMM(float(y)))
   if not any(poly.Contains(point,i) for poly in zones for i in range(poly.OutlineCount())):miss.append([round(x,6),round(y,6)])
  rows.append({'net':t.GetNetname(),'layer':board.GetLayerName(t.GetLayer()),'length_mm':length,'samples':n+1,'without_In1_GND':len(miss),'missing_xy_mm':miss})
 return rows
pr=projection(b,added);out['new_route_In1_projection']=pr
for label,board in boards.items():
 pins=[t for t in board.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='3V3_AON' and 30<xy(t.GetPosition())[1]<35 and xy(t.GetPosition())[0]<3]
 gnd=[xy(t.GetPosition()) for t in board.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND']
 out[label]['C201_AON_via_nearest_GND_via']=[{'AON_xy':xy(t.GetPosition()),'nearest_GND_xy':min(gnd,key=lambda q:math.dist(q,xy(t.GetPosition()))),'distance_mm':min(math.dist(q,xy(t.GetPosition())) for q in gnd)} for t in pins]
rho=1.724e-8*(1+.00393*(85-20));oldlen=.825;newlen=.625+math.sqrt(.6**2+.6**2)
def r(L,w):return rho*(L*1e-3)/(w*1e-3*17e-6)
out['conditional_resistance_screen']={'rho_85C_ohm_m':rho,'thickness_um':17,'current_assumption_A':.5,'C201_width_mm':.15,'old_length_mm':oldlen,'new_length_mm':newlen,'old_mOhm':r(oldlen,.15)*1e3,'new_mOhm':r(newlen,.15)*1e3,'delta_mOhm':(r(newlen,.15)-r(oldlen,.15))*1e3,'new_drop_mV_at_assumed_500mA':r(newlen,.15)*.5*1e3,'delta_drop_mV_at_assumed_500mA':(r(newlen,.15)-r(oldlen,.15))*.5*1e3,'legacy_neck_5p15mm_0p2mm_drop_mV_at_assumed_500mA':r(5.15,.2)*.5*1e3,'qualification':'Sensitivity screen only: excludes vias, spreading, AC inductance, effective capacitor ESR/ESL and actual load/current partition. Not a measured current or PI approval.'}
out['method_limits']='25um pixel-grid morphology and regional comparisons are screens, not exact physical neck width or conductive current distribution. In1 projection does not prove the actual adjacent reference plane for B.Cu (In2 AON), return-loop transfer impedance or EMI.'
(D/'power_return_analysis.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:out[k] for k in ['regional_plane_changes','conditional_resistance_screen']},indent=2))
print('new route In1 missing by net', {n:sum(x['without_In1_GND'] for x in pr if x['net']==n) for n in set(x['net'] for x in pr)})
print('AON erosion',[(l,out[l]['AON_erosion_screen']) for l in boards])
# Length-weighted midpoint sampling avoids overcounting many short route segments.
def weighted_projection(board,net):
 zones=[z.GetFilledPolysList(p.In1_Cu) for z in board.Zones() if z.GetLayer()==p.In1_Cu and z.GetNetname()=='GND'];total=missing=0.;bylayer={}
 for t in board.GetTracks():
  if isinstance(t,p.PCB_VIA) or t.GetNetname()!=net:continue
  length=p.ToMM(t.GetLength());n=max(1,math.ceil(length/.025));start,end=xy(t.GetStart()),xy(t.GetEnd());lost=0.
  for j in range(n):
   f=(j+.5)/n;point=p.VECTOR2I(p.FromMM(start[0]+f*(end[0]-start[0])),p.FromMM(start[1]+f*(end[1]-start[1])))
   if not any(poly.Contains(point,i) for poly in zones for i in range(poly.OutlineCount())):lost+=length/n
  total+=length;missing+=lost;k=board.GetLayerName(t.GetLayer());q=bylayer.setdefault(k,{'length_mm':0.,'without_In1_GND_mm_screen':0.});q['length_mm']+=length;q['without_In1_GND_mm_screen']+=lost
 return {'total_track_length_mm':total,'without_In1_GND_mm_screen':missing,'by_layer':bylayer}
out['full_net_ground_projection_screen']={label:{net:weighted_projection(b,net) for net in ['CAM_D7','CAM_VSYNC','CAM_HREF','CHIP_EN','3V3_AON']} for label,b in boards.items()}
out['source_unchanged_after_analysis']={label:hashlib.sha256((R/dir/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()==out[label]['sha256'] for label,dir in [('HREF3','mainboard_href3_candidate'),('HREF2','mainboard_href2_candidate')]}
(D/'power_return_analysis.json').write_text(json.dumps(out,indent=2))
