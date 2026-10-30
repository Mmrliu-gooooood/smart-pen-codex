import geometry as g,json
p=g.p;F=p.F_Cu
remove=['13079769-348d-5142-9cb4-1d44ec56a7b8','fb1700a3-5c27-5c36-9d84-b9492b46b711'];g.old=[t for t in g.old if t.m_Uuid.AsString()not in remove]
ps=[(2.65,79.9),(2.65,79.1),(5.72,79.1),(5.72,80.7)]
aon=[g.track('3V3_AON',F,a,b,.25)for a,b in zip(ps,ps[1:])];print('replacement',g.errors(aon));g.objs.extend(aon)
# Escape pad endpoints above the removed top beam, then turn outside actual pad and MEMS areas.
routes={
'SCL':('AON_I2C_SCL',[(3.2375,81.25),(3.2,80.8),(3.2,79.7)]),
'IRQ':('PICKUP_INT_N',[(3.75,81.2375),(3.75,80.0),(3.8,79.7)])}
r={}
for tag,(net,points) in routes.items():
 ts=[g.track(net,F,a,b,.15)for a,b in zip(points,points[1:])];v=g.via(net,points[-1]);v.SetWidth(F,450000);v.SetDrill(200000);ts.append(v);r[tag]=g.errors(ts);print(tag,r[tag])
open(__file__.replace('.py','.json'),'w').write(json.dumps({'removed':remove,'replacement_errors':g.errors(aon),'escapes':r},indent=2)+'\n')
