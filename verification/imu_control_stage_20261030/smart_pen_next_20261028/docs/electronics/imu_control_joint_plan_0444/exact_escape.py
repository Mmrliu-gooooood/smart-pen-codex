import geometry as g,json
p=g.p;out={}
for n in['PICKUP_INT_N','AON_I2C_SCL']:
 points=[];bad={}
 for ix in range(120,209,2):
  for iy in range(3220,3237,2):
   a=(ix*.025,iy*.025);v=g.via(n,a);v.SetWidth(p.F_Cu,450000);v.SetDrill(200000);e=g.errors([v])
   if not e:points.append(a)
   else:
    for x in e:bad[str(x)]=bad.get(str(x),0)+1
 out[n]={'clear_via_centers':points,'rejects':bad}
 print(n,len(points),points[:20],flush=True)
open(__file__.replace('exact_escape.py','exact_escape.json'),'w').write(json.dumps(out,indent=2)+'\n')
