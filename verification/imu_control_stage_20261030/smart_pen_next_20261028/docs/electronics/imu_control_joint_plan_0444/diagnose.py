import router_core as c,json
from scipy.ndimage import label
p=c.p;out={}
for net,pad in [('PICKUP_INT_N','U501.12'),('AON_I2C_SCL','U501.1'),('AON_I2C_SDA','U501.4')]:
 obs,vb=c.masks(net,.15);q=next(q for f in c.b.GetFootprints()for q in f.Pads()if f.GetReference()+'.'+q.GetNumber()==pad);x,y=c.xy(q.GetPosition());ix,iy=round(x/c.STEP),round(y/c.STEP);lab,_=label(~obs[0]);mask=lab==lab[ix,iy];points=c.np.argwhere(mask);free=points[~vb[mask]]
 out[net]={'Fcomponent_grid_count':len(points),'bbox_mm':[[float(points[:,j].min()*c.STEP),float(points[:,j].max()*c.STEP)]for j in[0,1]],'available_vias':len(free)}
 for yy in range(round(79.7/c.STEP),round(83.3/c.STEP)+1,4):
  print(net,round(yy*c.STEP,2),''.join('S'if(xi,yy)==(ix,iy)else('v'if mask[xi,yy]and not vb[xi,yy]else'.'if mask[xi,yy]else'#')for xi in range(60,221,2)))
print(json.dumps(out,indent=2));open(__file__.replace('diagnose.py','reachability.json'),'w').write(json.dumps(out,indent=2)+'\n')
