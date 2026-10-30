exec((__import__('pathlib').Path(__file__).parent/'plan.py').read_text().split('result=dict(')[0])
ns='SENS_VIO_1V8';sel={r['pad']:r['selected']for r in attempts};rows=[]
# One shared left trunk, with exact branch points independent of electrical power generation.
for layer in [p.B_Cu,p.In3_Cu]:
 for xx in [.65,1.0,1.3]:
  for yy in [89.3,89.5,89.7]:
   items=[track(ns,layer,(xx,sel['C202.1'][1]),(xx,yy)),via(ns,(xx,yy)),track(ns,p.B_Cu,(xx,yy),(1.75,90.5))]
   for name in ['C202.1','C204.1','C206.1','C208.1','U204.1']:
    a=sel[name];items.append(track(ns,layer,a,(xx,a[1])))
   er=errors(items);rows.append(dict(layer=b.GetLayerName(layer),x=xx,y=yy,conflicts=er))
   if not er:
    add(items,'sensor_external_reference_trunk');print('SUCCESS',b.GetLayerName(layer),xx,yy);break
  else:continue
  break
 else:continue
 break
(D/'sensor_compare.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([dict(layer=x['layer'],x=x['x'],y=x['y'],count=len(x['conflicts']),first=x['conflicts'][:5])for x in rows],indent=2))
if not er:(D/'with_sensor_plan.json').write_text(json.dumps(dict(base_sha=hashlib.sha256(S.read_bytes()).hexdigest(),objects=spec,local_via_attempts=attempts),indent=2)+'\n')
