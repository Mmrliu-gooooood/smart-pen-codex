from pathlib import Path
import json,math
import numpy as np
P=Path(__file__).resolve().parent;C=P.parent/'smart_pen_tilt_v4_review_run_20261030';F=P.parent/'smart_pen_tilt_roi_v4_candidate_20261030'
dirs=np.load(P.parent/'smart_pen_viewport_audit_20261028/upstream_directions.npy')
def truth(s,xy):
 p=60/s['fov'];x=xy[...,0]-s['ox']-100/p;y=xy[...,1]-s['oy']-100/p
 z=1+s.get('perspective_x',0)*x+s.get('perspective_y',0)*y
 a=math.radians(s.get('angle',0));c=math.cos(a);t=math.sin(a)
 xx=x+s.get('shear',0)*y;yy=s.get('ratio',1)*y
 return np.stack([99.5+p*(c*xx-t*yy)/z,99.5+p*(t*xx+c*yy)/z],axis=-1)
def check(s,r):
 pts=np.array([(x,y) for y in range(r['y'],r['y']+6) for x in range(r['x'],r['x']+6)],float)
 a=np.array(r['H']).reshape(3,3)
 def mapped(q):
  h=np.c_[q,np.ones(len(q))]@a.T;return h[:,:2]/h[:,2,None]
 expect=truth(s,pts);pred=mapped(pts);err=np.linalg.norm(expect-pred,axis=1).max()
 symbols=dirs[r['y']:r['y']+6,r['x']:r['x']+6].reshape(-1)
 assert symbols.tolist()==r['directions'];assert err<=.1*(60/s['fov'])
 cos=[]
 for delta in ([.01,0],[0,.01]):
  x=mapped(pts+delta)-pred;y=truth(s,pts+delta)-expect
  cos.extend(np.sum(x*y,axis=1)/(np.linalg.norm(x,axis=1)*np.linalg.norm(y,axis=1)))
 assert min(cos)>math.cos(math.radians(5))
 t=np.linspace(0,2*np.pi,65536,endpoint=False);ring=np.c_[np.cos(t),np.sin(t)]/6;l,top,w,h=r['roi'];margin=math.inf
 for q,d in zip(pts,symbols):
  offset=np.array(((0,-1),(-1,0),(1,0),(0,1))[d])/6
  ink=truth(s,q+offset+ring)
  margin=min(margin,float((ink[:,0]-(l-.5)).min()),float((l+w-.5-ink[:,0]).min()),float((ink[:,1]-(top-.5)).min()),float((top+h-.5-ink[:,1]).min()))
 assert margin>0
 return dict(max_grid_error_px=float(err),min_basis_cosine=float(min(cos)),sampled_circle_margin_px=margin)
rows=[]
for s,r in zip(json.loads((C/'baseline_eight.json').read_text()),json.loads((C/'candidate_eight.json').read_text())):
 if r['status']==0:rows.append(dict(image=r['image'],**check(s,r)))
for r in json.loads((F/'regression_results.json').read_text())['cases']:
 if r['status']==0 and not r['square_support']:
  q=check(r['spec'],r);assert abs(q['sampled_circle_margin_px']-r['circle_margin_px'])<1e-6
  rows.append(dict(regression_index=r['fixture_index'],analytic_margin_px=r['circle_margin_px'],**q))
(P/'independent_geometry.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS independent scalar projection, exact 36 symbols, all-cell basis orientation <5deg, grid error <=0.1cell, dense 65536-angle/circle support: ',len(rows),'cases; dense sampled ring corroborates analytic bounds, not standalone continuum proof')
