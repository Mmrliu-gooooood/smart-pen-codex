import geometry_native as g,json,math
p=g.p;rows=[]
for f in g.b.GetFootprints():f.BuildCourtyardCaches()
for xy in [(12.9,77.025),(12.9,76.7),(12.125,77.9),(11.35,77.025),(5.4,67.6),(5.4,68.3),(5.4,69),(7,66.2)]:
 t=g.via('GND',xy);err=g.errors([t])
 for f in g.b.GetFootprints():
  for l in [p.F_CrtYd,p.B_CrtYd]:
   q=g.shape(t,p.F_Cu);q.BooleanIntersection(f.GetCourtyard(l))
   if q.Area()>1:err.append(('courtyard',f.GetReference(),g.b.GetLayerName(l),q.Area()/1e12))
 rows.append({'xy':xy,'dia_drill_mm':[.6,.3],'errors':err,'distance_to_source_SDA_via_mm':math.dist(xy,(6.25,67.65)),'distance_to_sink_SDA_via_mm':math.dist(xy,(12.125,77.025))})
g.D.joinpath('stitch_screen.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
