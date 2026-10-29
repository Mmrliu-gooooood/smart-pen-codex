"""Read-only first-pass architecture screen; no component or charging release.
Uses Vishay material-9 curve polynomial and tabulated tolerance, NOT a beta-only extrapolation.
"""
import itertools,json,math
from pathlib import Path
Y={-40:2.79,-35:2.52,-30:2.26,-25:2.02,-20:1.78,-15:1.55,-10:1.33,-5:1.12,0:.92,5:.72,10:.53,15:.35,20:.17,25:0,30:.17,35:.32,40:.48,45:.63,50:.77,55:.91,60:1.05,65:1.18,70:1.31,75:1.44,80:1.56,85:1.68,90:1.79,95:1.90,100:2.01,105:2.12,110:2.22,115:2.32,120:2.42,125:2.51}
def resistance(t,rs,bs):
 k=t+273.15;lo=max(-40,min(120,math.floor(t/5)*5));dev=Y[lo]+(Y[lo+5]-Y[lo])*(t-lo)/5
 return 10000*math.exp(-14.6337+4791.842/k-115334/k**2-3.730535e6/k**3)*(1+rs*.02)*(1+bs*dev/100)
def solve(r,rs,bs):
 lo,hi=-40.,125.
 if not resistance(lo,rs,bs)>r>resistance(hi,rs,bs):raise ValueError('root outside domain')
 for _ in range(60):
  m=(lo+hi)/2
  if resistance(m,rs,bs)>r:lo=m
  else:hi=m
 return (lo+hi)/2
parts={'BQ24074':{'bias':[72e-6,78e-6],'cold':[2,2.2],'hot':[.270,.330]},'BQ25170':{'bias':[36.5e-6,39.5e-6],'cold':[.99,1.09],'hot':[.176,.200]},'BQ25185':{'bias':[36.5e-6,39.5e-6],'cold':[.9575,1.0575],'hot':[.105,.125]}}
out={'status':'NOFAB; static mathematical comparison only, not physical sensor qualification','NTC':'NTCLE100E3103GB0, R25 +/-2%; material9 curve and B tolerance table','parts':{}}
for name,p in parts.items():
 d={}
 for kind in ('cold','hot'):
  vals=[solve(v/i,rs,bs) for v,i,rs,bs in itertools.product(p[kind],p['bias'],[-1,1],[-1,1])]
  d[kind+'_trip_C']=[min(vals),max(vals)]
 d['cold_inhibit_at_0C_margin_V']=min(i*resistance(0,rs,bs)-p['cold'][1] for i,rs,bs in itertools.product(p['bias'],[-1,1],[-1,1]))
 d['cold_inhibit_at_10C_margin_V']=min(i*resistance(10,rs,bs)-p['cold'][1] for i,rs,bs in itertools.product(p['bias'],[-1,1],[-1,1]))
 d['hot_inhibit_at_45C_margin_V']=min(p['hot'][0]-i*resistance(45,rs,bs) for i,rs,bs in itertools.product(p['bias'],[-1,1],[-1,1]))
 d['static_0_45_endpoint_pass']=d['cold_inhibit_at_0C_margin_V']>0 and d['hot_inhibit_at_45C_margin_V']>0
 out['parts'][name]=d
if any(d['static_0_45_endpoint_pass'] for d in out['parts'].values()):raise RuntimeError('Unexpected outcome; inspect inputs')
print(json.dumps(out,indent=2))
