import reference_final as z,json
p=z.p;out=[]
for ref,a in z.pa.items():
 b=z.pb[ref];lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(a,b);gain=p.SHAPE_POLY_SET();gain.BooleanSubtract(b,a);out.append({'layer':z.b.GetLayerName(ref[0]),'net':ref[1],'lost_mm2':lost.Area()/1e12,'gained_mm2':gain.Area()/1e12})
(z.D/'plane_delta_final.json').write_text(json.dumps(out,indent=2));print(out)
