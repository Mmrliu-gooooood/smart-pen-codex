from pathlib import Path
import json
D=Path(__file__).resolve().parent
def flags(bounds,cells,lo,hi,step):
 return {'touches_artificial_y_min':bool(cells and bounds[1]<=int(lo/step)*step+1e-10),'touches_artificial_y_max':bool(cells and bounds[3]>=(int(hi/step)-1)*step-1e-10)}
r=json.loads((D/'ordinary_layer_component_evidence.json').read_text());checks={}
for name,c in r['components'].items():
 allflags=[]
 for row in c['reachable']:
  f=flags(row['bounds'],row['cells'],*r['window_y_mm'],r['grid_mm']);checks[name+'_'+row['layer']]=all(row[k]==v for k,v in f.items());allflags+=list(f.values())
 checks[name+'_incomplete_box_proof']=c['incomplete_box_proof']==any(allflags)
checks['synthetic_touch_detected']=flags([1,10,2,19.975],4,10,20,.025)=={'touches_artificial_y_min':True,'touches_artificial_y_max':True};checks['synthetic_interior_clear']=not any(flags([1,10.025,2,19.95],4,10,20,.025).values());checks['empty_component_not_a_touch']=not any(flags(None,0,10,20,.025).values())
if not all(checks.values()):raise RuntimeError(checks)
(D/('boundary_regression_optimized.json'if not __debug__ else'boundary_regression.json')).write_text(json.dumps({'checks':checks,'scope':'Automatic search-box warning classification; a touched artificial boundary requires bounded ordinary-layer expansion before layer/pose trade. No touch still does not prove continuous/global impossibility. No recomputation of historical trial geometry is implied.'},indent=2));print(len(checks),'boundary warning regressions pass')
