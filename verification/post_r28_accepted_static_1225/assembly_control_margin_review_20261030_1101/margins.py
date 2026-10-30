import json,math
from pathlib import Path
O=Path(__file__).resolve().parent;j=json.load(open(O/'results.json'))['stages'][-1]
def ptseg(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];dd=dx*dx+dy*dy;t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/dd))if dd else 0;return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def ptr(p,r):return math.hypot(max(r[0]-p[0],0,p[0]-r[2]),max(r[1]-p[1],0,p[1]-r[3]))
def segrect(a,b,r):
 lo,hi=0.,1.
 for k in [0,1]:
  d=b[k]-a[k]
  if abs(d)<1e-15:
   if a[k]<r[k]or a[k]>r[k+2]:lo,hi=1.,0.;break
  else:
   x,y=sorted([(r[k]-a[k])/d,(r[k+2]-a[k])/d]);lo=max(lo,x);hi=min(hi,y)
 if lo<=hi:return 0.
 return min(ptr(a,r),ptr(b,r),*[ptseg(c,a,b)for c in [(r[0],r[1]),(r[0],r[3]),(r[2],r[1]),(r[2],r[3])]])
obstacles=[('C206_full','F.Cu',[9.125,58.3875,11.575,59.3375]),('J104_native_service','B.Cu',[8.955,51.755,11.045,57.845])];out=[]
for name,side,rect in obstacles:
 rows=[]
 for r in j['rows']:
  if r['type']!='via'and r['layer']!=side:continue
  gap=segrect(r['start'],r['end'],rect)-r['width']/2;rows.append({'type':r['type'],'net':r['net'],'start':r['start'],'end':r['end'],'width':r['width'],'gap_mm':gap})
 rows.sort(key=lambda x:x['gap_mm']);out.append({'obstacle':name,'side':side,'bounds':rect,'closest':rows[:5]})
(O/'margins.json').write_text(json.dumps({'sha256':j['sha256'],'method':'exact analytic round-cap segment/disc to specified rectangular budget; nominal only','obstacles':out},indent=2)+'\n');print(out)
