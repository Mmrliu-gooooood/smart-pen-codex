from geometry import *
from finite_copper import build,components,shape as finite
r=json.loads((D/'plan.json').read_text());N='SENS_VIO_1V8';ns=build(b)[N];rows=[]
for omit in [None,14,1]:
 nodes=list(ns)
 for i,s in enumerate(r['objects']):
  if i==omit:continue
  t=via(N,s['start'])if s['type']=='via'else track(N,b.GetLayerID(s['layer']),s['start'],s['end'],s['width']);alltemps.append(t);nodes.append((str(i),False,{l:finite(t,l)for l in L if t.IsOnLayer(l)}))
 c=components(nodes)
 if omit is None and not(len(c)==1 and len(c[0])==12):raise RuntimeError('positive')
 if omit is not None and len(c)==1:raise RuntimeError('negative failed')
 rows.append(dict(omitted=omit,object=None if omit is None else r['objects'][omit],components=c))
(D/'negative.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
