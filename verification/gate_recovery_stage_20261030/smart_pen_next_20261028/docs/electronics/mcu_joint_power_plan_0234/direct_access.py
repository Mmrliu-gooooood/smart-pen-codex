import geometry as q,json
out=[]
for at in [[1.2,7.8],[1.4,7.8],[1.6,7.8],[1.9,7.8],[1.2,7.0],[1.9,7.0]]:
 t=q.via('3V3_AON',at);out.append(dict(center=at,diameter=.6,drill=.3,errors=q.errors([t])))
print(json.dumps(dict(status='READ_ONLY_FIXED_LOCATION_OBSTACLE_PROBES_NOT_ROUTE_SEARCH',locations=out,physical_pad_bounds=[dict(pad=n,net=q.pm[n].GetNetname(),layer=q.b.GetLayerName(q.pm[n].GetLayer()),position=q.xy(q.pm[n]),bbox=[q.pm[n].GetBoundingBox().GetX()/1e6,q.pm[n].GetBoundingBox().GetY()/1e6,q.pm[n].GetBoundingBox().GetWidth()/1e6,q.pm[n].GetBoundingBox().GetHeight()/1e6])for n in ['C103.1','C103.2','R503.1']]),indent=2))
