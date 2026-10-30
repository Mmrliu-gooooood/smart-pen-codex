import geometry as g,json
p=g.p;F=p.F_Cu;B=p.B_Cu;I=p.In4_Cu;A='3V3_AON';G='GND';N='NIB_CONTACT_N';C='CONTACT'
def tr(n,l,ps,w=.15):return [g.track(n,l,a,b,w)for a,b in zip(ps,ps[1:])]
def via(n,pt,small=False):
 v=g.via(n,pt)
 if small:v.SetWidth(F,450000);v.SetDrill(200000)
 return v
parts={
 'mcu':tr(N,F,[(2.575,9.8),(1.95,9.8)])+[via(N,(1.95,9.8),True)]+tr(N,B,[(1.95,9.8),(3.475,9.8),(3.475,9.75),(3.325,11.5)]),
 'aon':tr(A,B,[(1.675,11.5),(1.3,12.1)],.25)+[via(A,(1.3,12.1))],
 'capgnd':tr(G,B,[(5.025,9.75),(5.025,10.4),(4.25,10.75)],.25),
 'contact':tr(C,B,[(3,52),(3.825,53),(3.825,54.25)],.25),
 'j103gnd':tr(G,B,[(5.4,52),(6.6,52)],.25)+[via(G,(6.6,52))],
 'long':tr(N,B,[(2.175,54.25),(1.4,54.25)],.15)+[via(N,(1.4,54.25),True)]+tr(N,I,[(1.95,9.8),(1.95,53.7),(1.4,54.25)],.15)
}
for name,items in parts.items():print(name,json.dumps(g.errors(items)))
print('total',json.dumps(g.errors(sum(parts.values(),[]))))
