import reference_final as z,json
p=z.p;refs={p.F_Cu:[(p.In1_Cu,'GND')],p.B_Cu:[(p.In4_Cu,'GND')],p.In3_Cu:[(p.In4_Cu,'GND'),(p.In2_Cu,'3V3_AON')],p.In2_Cu:[(p.In1_Cu,'GND')]};unions={};members={}
for u,t in z.aa.items():
 if u not in z.bb or t.GetClass()=='PCB_VIA':continue
 for ref in refs.get(t.GetLayer(),[]):
  s=z.shape(t);old=p.SHAPE_POLY_SET();old.BooleanIntersection(s,z.pa[ref]);new=p.SHAPE_POLY_SET();new.BooleanIntersection(s,z.pb[ref]);old.BooleanSubtract(new)
  if old.Area()>0:
   k=(t.GetNetname(),t.GetLayer(),ref);unions.setdefault(k,p.SHAPE_POLY_SET()).BooleanAdd(old);members.setdefault(k,[]).append({'uuid':u,'individual_mm2':old.Area()/1e12})
rows=[{'net':n,'layer':z.b.GetLayerName(l),'reference_layer':z.b.GetLayerName(ref[0]),'reference_net':ref[1],'unique_lost_union_mm2':q.Area()/1e12,'members':members[(n,l,ref)]}for(n,l,ref),q in unions.items()];(z.D/'retained_reference_unions.json').write_text(json.dumps({'rows':rows,'scope':'Per-net/layer unique loss union; do not sum overlapping old track projections. This is static area characterization, not SI acceptance.'},indent=2));print(rows)
