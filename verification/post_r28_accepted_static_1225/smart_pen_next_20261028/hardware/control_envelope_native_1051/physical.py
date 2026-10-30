import geometry_native as g,json,math
p=g.p;m=json.loads((g.D/'materialization.json').read_text());ids=set(m['added']);new=[t for t in g.old if t.m_Uuid.AsString()in ids];g.old=[t for t in g.old if t.m_Uuid.AsString()not in ids];errors=g.errors(new)
if errors:raise RuntimeError(errors)
for f in g.b.GetFootprints():f.BuildCourtyardCaches()
rows=[];court=[]
for t in new:
 if not isinstance(t,p.PCB_VIA):continue
 rows.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'xy':g.xy(t),'diameter_mm':t.GetWidth(p.F_Cu)/1e6,'drill_mm':t.GetDrillValue()/1e6})
 for f in g.b.GetFootprints():
  for l in [p.F_CrtYd,p.B_CrtYd]:
   z=g.shape(t,p.F_Cu);z.BooleanIntersection(f.GetCourtyard(l))
   if z.Area()>1:court.append({'via':t.m_Uuid.AsString(),'ref':f.GetReference(),'layer':g.b.GetLayerName(l),'area_mm2':z.Area()/1e12})
if court:raise RuntimeError('changed vias must clear ALL native courtyards: '+str(court))
print(json.dumps({'finite_geometry_errors':errors,'changed_vias_all_layer_all_pad_checks':rows,'changed_via_courtyard_overlaps':court,'scope':'Nominal finite CAD; full J202 operating envelope and underbody/tenting/process must be reviewed separately. No pad overlap waivers.'},indent=2))
