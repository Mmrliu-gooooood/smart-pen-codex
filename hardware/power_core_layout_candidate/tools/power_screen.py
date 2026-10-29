#!/usr/bin/python3
"""Conditional engineering screen, not measured system load, ampacity or thermal acceptance."""
from pathlib import Path
import pcbnew as p,numpy as np,json,math,heapq
from PIL import Image,ImageDraw
from scipy import ndimage
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'power_core_NOFAB.kicad_pcb'));scale=40;planes=[]
for z in b.Zones():
 if z.GetLayer()==p.B_Cu:continue
 poly=z.GetFilledPolysList(z.GetLayer());im=Image.new('1',(481,1401));draw=ImageDraw.Draw(im)
 for i in range(poly.OutlineCount()):
  c=poly.COutline(i);draw.polygon([(round(p.ToMM(c.CPoint(j).x)*scale),round(p.ToMM(c.CPoint(j).y)*scale)) for j in range(c.PointCount())],fill=1)
 mask=np.array(im,dtype=bool);labels,k=ndimage.label(mask);dist=ndimage.distance_transform_edt(mask)/scale;neck=[]
 for e in [.1,.15,.2,.25]:
  lab,n=ndimage.label(dist>=e);a=np.bincount(lab.ravel())[1:]/scale**2;neck.append({'erosion_mm':e,'regions_over_0p05mm2':int(sum(a>.05))})
 rec={'net':z.GetNetname(),'layer':b.GetLayerName(z.GetLayer()),'actual_filled_outlines':poly.OutlineCount(),'raster_connected_components':int(k),'raster_pitch_mm':1/scale,'erosion_screen':neck}
 if z.GetNetname().lstrip('/')=='SYS_RAW':
  start=(round(9.05*scale),round(9.2*scale));target=(round(3*scale),round(24*scale));best=np.zeros_like(dist);best[start[1],start[0]]=dist[start[1],start[0]];heap=[(-best[start[1],start[0]],start)]
  while heap:
   neg,(x,y)=heapq.heappop(heap);cap=-neg
   if cap<best[y,x]-1e-12:continue
   if (x,y)==target:break
   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if not (0<=xx<481 and 0<=yy<1401) or not mask[yy,xx]:continue
    c=min(cap,dist[yy,xx])
    if c>best[yy,xx]+1e-12:best[yy,xx]=c;heapq.heappush(heap,(-c,(xx,yy)))
  rec['widest_raster_path_min_width_mm']=float(best[target[1],target[0]]*2);rec['path_endpoints_mm']=[[9.05,9.2],[3,24]];assert rec['widest_raster_path_min_width_mm']>0
 planes.append(rec);im.save(D/'preview'/('plane_'+b.GetLayerName(z.GetLayer()).replace('.','_')+'.png'))
rho85=1.724e-8*(1+.00393*(85-20));models=[]
for thickness in [31.5,18]:
 for width in [.3,.5,.6]:
  r=rho85*.01/(width*.001*thickness*1e-6)
  models.append({'temperature_C':85,'assumed_copper_um':thickness,'width_mm':width,'length_mm':10,'R_mohm':r*1000,'at_1A_drop_mV':r*1000,'at_1A_loss_mW':r*1000})
load=.75;vin=2.8;vout=3.3;eta=.8;avg=vout*load/(vin*eta);d=1-vin/vout;cases=[]
for fMHz in [.5,1,1.4,2.1]:
 peak=avg+vin*d/(2*fMHz*1e6*.47e-6*.8);cases.append({'assumed_f_MHz':fMHz,'L_low_uH':.376,'Ipeak_A':peak,'recommended_20pct_margin_A':peak*1.2})
# Approximate loop boundary using straight internal device closure, not measured field/current distribution.
poly=[(5.5,22.25),(5.5,21.7),(4.815,21.015),(4.815,19.2),(7.185,19.2),(7.185,21.015),(6.5,21.7),(6.5,22.25)]
area=abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
result={'status':'CONDITIONAL SCREEN, no measured load or current/temperature certification','actual_planes':planes,'copper_resistance_models':models,'actual_power_trace_neck_mm':.3,'exceptions':'SYS_RAW 0.15mm track is EN-only high-Z branch; VBUS0.2mm branch only feeds CE pull-up. Official DLA pad itself is0.25mm wide. Do not confuse control widths with power trunk.', 'assumed_3V3_load_A':load,'assumed_vin_V':vin,'assumed_efficiency':eta,'input_average_A':avg,'peak_sweep':cases,'frequency_warning':'TPS63802 fSW table is typical/operating-condition dependent, not a guaranteed min; sweep is not a worst-case proof. Mode is PFM.','inductor_limits':'XFL4015-471MEC Isat25C3.5A@10%drop,5.4A@20%,6.6A@30%; TPS63802 boost current-limit max5.75A can exceed20%drop threshold. Not all-temperature fault qualification.','loop_boundary_mm2':area,'loop_polygon_mm':poly,'loop_warning':'Boundary approximation closes inside package/inductor with straight lines; not true magnetic loop/EMI certification.','capacitor_gate':'6 MLCC MPNs not selected. VIN effective>=4uF and VOUT effective>=7uF at3.3V must include DC-bias/temp/tolerance. Nominal values are not a proof.','thermal_gate':'No pen enclosure thermal model or test. BQ dissipation, via fill/stencil, cell/NTC placement and skin temperature unqualified.'}
(D/'power_screen.json').write_text(json.dumps(result,indent=2));print('PASS actual filled-plane screen; conditional resistive/load model, SW boundary',round(area,3),'mm2')
