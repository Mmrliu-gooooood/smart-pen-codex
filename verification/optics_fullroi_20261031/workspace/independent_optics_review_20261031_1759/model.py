"""Synthetic ideal pinhole plane model, not a lens or decoder qualification."""
import math

def project(x,y,distance_mm,focal_px,tilt_deg):
 if not all(math.isfinite(v) for v in (x,y,distance_mm,focal_px,tilt_deg)):raise ValueError("nonfinite input")
 t=math.radians(tilt_deg);z=distance_mm+y*math.sin(t)
 if not 1e-6<=distance_mm<=1e6 or not 1e-6<=focal_px<=1e6 or max(abs(x),abs(y))>1e6 or z<1e-9:raise ValueError("outside numeric domain or nonpositive depth")
 return focal_px*x/z,focal_px*y*math.cos(t)/z

def jacobian(x,y,distance_mm,focal_px,tilt_deg):
 project(x,y,distance_mm,focal_px,tilt_deg)
 t=math.radians(tilt_deg);z=distance_mm+y*math.sin(t)
 return focal_px/z,-focal_px*x*math.sin(t)/z**2,0.,focal_px*math.cos(t)*distance_mm/z**2

def screen(pitch_mm,dot_ratio,offset_ratio,distance_mm,focal_px,tilt_deg,roi_px=256,speed_mm_s=100,exposure_us=100,blur_limit_px=1.):
 if not all(math.isfinite(v) for v in (pitch_mm,dot_ratio,offset_ratio,distance_mm,focal_px,tilt_deg,roi_px,speed_mm_s,exposure_us,blur_limit_px)) or not 0<=speed_mm_s<=1e6 or not 0<=exposure_us<=1e6 or blur_limit_px<=0:raise ValueError("invalid finite/motion parameter")
 if pitch_mm<=0 or dot_ratio<=0 or offset_ratio<0 or not 0<=tilt_deg<90 or roi_px<=0:raise ValueError('invalid model parameter')
 p=pitch_mm;h=p*(2.5+offset_ratio+dot_ratio/2)
 corners=[project(x,y,distance_mm,focal_px,tilt_deg) for x in [-h,h] for y in [-h,h]]
 js=[jacobian(x,y,distance_mm,focal_px,tilt_deg) for x in [-h,0,h] for y in [-h,0,h]]
 sx=[abs(a)*p for a,b,c,d in js];sy=[math.hypot(b,d)*p for a,b,c,d in js]
 # Exact singular values of the triangular 2x2 local map.
 sig=[];sig_min=[];orth=[]
 for a,b,c,d in js:
  tr=a*a+b*b+d*d;det=(a*d)**2
  sig.append(math.sqrt((tr+math.sqrt(max(0,tr*tr-4*det)))/2))
  sig_min.append(abs(a*d)/sig[-1])
  orth.append(abs(b)/math.hypot(b,d))
 width=max(x for x,y in corners)-min(x for x,y in corners)
 height=max(y for x,y in corners)-min(y for x,y in corners)
 center=jacobian(0,0,distance_mm,focal_px,tilt_deg);ratio=center[3]/center[0]
 hard=[]
 if p*(1-2*offset_ratio-dot_ratio)<=0:hard.append('worst_case_ink_overlap')
 if not .10<=offset_ratio<=.30:hard.append('displacement_contract')
 if max(abs(a) for xy in corners for a in xy)>roi_px/2:hard.append('roi_window_envelope')
 if not 8<=p*center[0]<=32:hard.append('cold_pitch_x')
 if not .6<=ratio<=1.4:hard.append('cold_axis_ratio')
 proxy=[]
 if min(sx+sy)<8 or max(sx+sy)>32:proxy.append('local_spacing_outside_8_32_proxy')
 if max(orth)>.05:proxy.append('nonorthogonal_gt_005_proxy')
 spread=max(sx)/min(sx)
 if spread>1.10:proxy.append('pitch_spread_gt_10pct_proxy')
 blur=max(sig)*speed_mm_s*exposure_us*1e-6
 if blur>blur_limit_px:proxy.append('blur_gt_assumed_limit')
 if min(sig_min)*p*dot_ratio<2:proxy.append('dot_minor_under_2px_proxy')
 return dict(pitch_mm=p,dot_ratio=dot_ratio,offset_ratio=offset_ratio,distance_mm=distance_mm,focal_px=focal_px,tilt_deg=tilt_deg,spacing_x_min_px=min(sx),spacing_x_max_px=max(sx),spacing_y_min_px=min(sy),window_width_px=width,window_height_px=height,center_axis_ratio=ratio,worst_gap_mm=p*(1-2*offset_ratio-dot_ratio),max_nonorthogonality=max(orth),pitch_spread=spread,blur_bound_px=blur,max_exposure_us_for_assumed_1px=1e6/(max(sig)*speed_mm_s) if speed_mm_s else None,screen_reasons=hard,engineering_proxy_rejects=proxy,status='SCREEN_REJECT' if hard else ('MODEL_RISK' if proxy else 'MODEL_RETAIN_NOT_QUALIFIED'))
