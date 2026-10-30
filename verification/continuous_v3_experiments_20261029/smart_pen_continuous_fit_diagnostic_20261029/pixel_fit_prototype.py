"""Pixel-only bounded-neighbor vector proposals + orthogonal refit prototype.
Diagnostic Python, not production firmware. No rendering truth enters models().
"""
import math
import numpy as np

def phase(v):
 return math.atan2(np.sin(2*np.pi*v).sum(),np.cos(2*np.pi*v).sum())/(2*np.pi)

def normalize(points,pitch,angle,ratio):
 co,si=math.cos(math.radians(angle)),math.sin(math.radians(angle))
 u=(points[:,0]*co+points[:,1]*si)/pitch;v=(-points[:,0]*si+points[:,1]*co)/(pitch*ratio)
 ox,oy=phase(u),phase(v)
 for _ in range(3):
  dx=u-ox-np.rint(u-ox);dy=v-oy-np.rint(v-oy);horizontal=np.abs(dx)>np.abs(dy)
  if horizontal.any():oy+=float(dy[horizontal].mean())
  if (~horizontal).any():ox+=float(dx[~horizontal].mean())
 ix=np.rint(u-ox);iy=np.rint(v-oy);dx=u-ox-ix;dy=v-oy-iy
 horizontal=np.abs(dx)>np.abs(dy)
 return np.stack((ix+np.where(horizontal,np.sign(dx)/6,0),iy+np.where(horizontal,0,np.sign(dy)/6)),axis=1)

def refine(points,pitch,angle,ratio):
 # No dropping points, outlier repair, phase oracle, codec-guided optimization.
 for _ in range(5):
  q=normalize(points,pitch,angle,ratio);q-=q.mean(axis=0);p=points-points.mean(axis=0)
  xx,yy=(q*q).sum(axis=0)
  if min(xx,yy)<1:return None
  ax,ay=q[:,0]@p;bx,by=q[:,1]@p
  m00=ax*ax/xx+by*by/yy;m01=ax*ay/xx-by*bx/yy;m11=ay*ay/xx+bx*bx/yy
  rad=.5*math.atan2(2*m01,m00-m11);co,si=math.cos(rad),math.sin(rad)
  px=(ax*co+ay*si)/xx;py=(-bx*si+by*co)/yy
  if px<=0 or py<=0:return None
  angle=math.degrees(rad);pitch=px;ratio=py/px
  if not (8<=pitch<=32 and -60<=angle<=60 and .6<=ratio<=1.4):return None
 return pitch,angle,ratio

def models(points):
 # At most 8 nearest neighbor vectors per point, each unordered pair once.
 n=len(points);vectors=[]
 for i,p in enumerate(points):
  delta=points-p;d2=(delta*delta).sum(axis=1);d2[i]=np.inf
  for j in np.argsort(d2,kind='stable')[:8]:
   if j<=i or not 16<=d2[j]<=1600:continue
   v=delta[j].copy()
   if v[0]<0:v=-v
   vectors.append(v)
 if len(vectors)<8:return [],{'vectors':len(vectors),'peaks':0,'pairs':0}
 vectors=np.array(vectors)
 # 41*81 uint8 cells suffice in a C implementation (saturate -> reject).
 bins=np.floor(vectors+.5).astype(int);bins[:,1]+=40
 hist=np.zeros((41,81),np.int32)
 for x,y in bins:
  if 0<=x<=40 and 0<=y<=80:hist[x,y]+=1
 # Smooth a fixed3x3 neighborhood and suppress a3px vector region per peak.
 padded=np.pad(hist,1);smooth=sum(padded[i:i+41,j:j+81] for i in range(3) for j in range(3))
 peaks=[]
 for _ in range(8):
  ix,iy=np.unravel_index(np.argmax(smooth),smooth.shape)
  if smooth[ix,iy]<4:break
  center=np.array([ix,iy-40.]);near=np.linalg.norm(vectors-center,axis=1)<=1.5
  if near.sum()>=4:peaks.append(np.mean(vectors[near],axis=0))
  xx,yy=np.indices(smooth.shape);smooth[(xx-ix)**2+(yy-iy)**2<=9]=0
 proposals=[];pairs=0
 for i,x in enumerate(peaks):
  pitch=np.linalg.norm(x);angle=math.degrees(math.atan2(x[1],x[0]))
  if not(8<=pitch<=32 and -60<=angle<=60):continue
  for j,y in enumerate(peaks):
   if i==j:continue
   cross=x[0]*y[1]-x[1]*y[0]
   if cross<0:y=-y
   length=np.linalg.norm(y);ratio=length/pitch
   if not(.6<=ratio<=1.4) or abs(x@y)/(pitch*length)>.20:continue
   pairs+=1
   found=refine(points,pitch,angle,ratio)
   if found is not None and not any(abs(found[0]-old[0])<1e-5 and abs(found[1]-old[1])<1e-5 and abs(found[2]-old[2])<1e-5 for old in proposals):proposals.append(found)
 return proposals,{'vectors':len(vectors),'peaks':len(peaks),'pairs':pairs}
