import reference_final as z
import json
from fractions import Fraction
p=z.p
out={}
for name,b in [('baseline',z.a),('candidate',z.b)]:
 q=z.planes(b)[p.In2_Cu,'3V3_AON'];rows=[]
 for ymm in [49.8,50,50.5,51,51.05,51.1,51.2,51.275,51.35,51.45,51.5,51.55,52,52.2]:
  y=round(ymm*1e6);xs=[]
  for i in range(q.OutlineCount()):
   for c in [q.Outline(i)]+[q.Hole(i,j)for j in range(q.HoleCount(i))]:
    pts=[c.CPoint(k)for k in range(c.PointCount())]
    for a,d in zip(pts,pts[1:]+pts[:1]):
     if (a.y<=y<d.y)or(d.y<=y<a.y):xs.append(Fraction(a.x)+Fraction((y-a.y)*(d.x-a.x),d.y-a.y))
  xs.sort();assert len(xs)%2==0;ints=[[float(xs[k])/1e6,float(xs[k+1])/1e6]for k in range(0,len(xs),2)if xs[k+1]>xs[k]];rows.append({'y_mm':ymm,'filled_x_intervals_mm':ints,'total_width_mm':sum(v-u for u,v in ints)})
 out[name]={'area_mm2':q.Area()/1e12,'crosssections':rows}
(z.D/'plane_neck.json').write_text(json.dumps(out,indent=2))
