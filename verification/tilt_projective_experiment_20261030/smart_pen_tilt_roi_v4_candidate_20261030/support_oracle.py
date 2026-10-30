"""Analytic projected-circle support, independent of C decoder.
A homography maps each source circle parameter to (A+Bcos+Csin)/(D+Ecos+Fsin).
Where denominator stays positive, extrema satisfy Kcos+Lsin+M=0, solved directly.
Float boundary allowance 1e-8 px; no claims about a real printed dot/PSF.
"""
import math,numpy as np

def fixture_h(s):
 p=60/s['fov'];a=math.radians(s.get('angle',0));co,si=math.cos(a),math.sin(a);ratio=s.get('ratio',1);shear=s.get('shear',0)
 d=np.array([s.get('perspective_x',0),s.get('perspective_y',0)])
 h=np.eye(3);h[:2,:2]=p*np.array([[co,co*shear-si*ratio],[si,si*shear+co*ratio]])+99.5*d
 h[:2,2]=99.5;h[2,:2]=d;cx=s['ox']+100/p;cy=s['oy']+100/p
 return h@np.array([[1,0,-cx],[0,1,-cy],[0,0,1.]])

def circle_bounds(h,x,y,r=1/6):
 D=h[2,0]*x+h[2,1]*y+h[2,2];E=h[2,0]*r;F=h[2,1]*r
 if D-math.hypot(E,F)<=1e-12:return None
 out=[]
 for row in (0,1):
  A=h[row,0]*x+h[row,1]*y+h[row,2];B=h[row,0]*r;C=h[row,1]*r
  K=C*D-A*F;L=A*E-B*D;M=C*E-B*F;R=math.hypot(K,L)
  if R<1e-15:out.append((A/D,A/D));continue
  if abs(M)>R*(1+1e-12):return None
  phi=math.atan2(L,K);alpha=math.acos(max(-1.,min(1.,-M/R)))
  vals=[]
  for t in (phi-alpha,phi+alpha):
   co,si=math.cos(t),math.sin(t);vals.append((A+B*co+C*si)/(D+E*co+F*si))
  out.append((min(vals),max(vals)))
 return out

def circle_support(s,r,dirs):
 h=fixture_h(s);l,t,w,hh=r['roi'];margin=float('inf');omitted=set(map(tuple,s.get('omit',[])))
 for y in range(r['y'],r['y']+6):
  for x in range(r['x'],r['x']+6):
   if (x,y) in omitted:return dict(circle_support=False,circle_margin_px=None,reason='omitted cell')
   dx,dy=((0,-1),(-1,0),(1,0),(0,1))[dirs[y,x]];box=circle_bounds(h,x+dx/6,y+dy/6)
   if box is None:return dict(circle_support=False,circle_margin_px=None,reason='nonpositive denominator or degenerate conic')
   (xmin,xmax),(ymin,ymax)=box;margin=min(margin,xmin-(l-.5),l+w-.5-xmax,ymin-(t-.5),t+hh-.5-ymax)
 return dict(circle_support=bool(margin>=-1e-8),circle_margin_px=float(margin),method='analytic fractional-sinusoid extrema; floating tolerance1e-8px')
