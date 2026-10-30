import geometry as g,json
p=g.p;F=p.F_Cu
for xy in [(10.325,70.5),(10.325,70),(10.325,69.5),(9.75,70.5),(10,71),(10,70.75)]:
 ts=[g.track('3V3_AON',F,(10.325,72),xy,.3),g.via('3V3_AON',xy)]
 print(xy,g.errors(ts))
