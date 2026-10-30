"""Numerical cross-check of analytic conic bounds (not hardware evidence)."""
from pathlib import Path
import json,numpy as np
from support_oracle import circle_bounds
rng=np.random.default_rng(7681);worst=0
for i in range(100):
 h=np.eye(3);h[:2,:]=rng.normal(size=(2,3));h[2,:2]=rng.uniform(-.1,.1,2);x,y=rng.uniform(-2,2,2);b=circle_bounds(h,x,y)
 if b is None:continue
 t=np.linspace(0,2*np.pi,20000,endpoint=False);p=np.array([x+np.cos(t)/6,y+np.sin(t)/6,np.ones(len(t))]);q=h@p;q=q[:2]/q[2]
 for axis in (0,1):
  assert b[axis][0]<=q[axis].min()+1e-10 and b[axis][1]>=q[axis].max()-1e-10
  worst=max(worst,abs(b[axis][0]-q[axis].min()),abs(b[axis][1]-q[axis].max()))
r=dict(passed=True,cases=100,seed=7681,perimeter_samples=20000,max_dense_sampling_gap=float(worst));print(r)
Path(__file__).with_name('support_oracle_selftest.json').write_text(json.dumps(r,indent=2)+'\n')
