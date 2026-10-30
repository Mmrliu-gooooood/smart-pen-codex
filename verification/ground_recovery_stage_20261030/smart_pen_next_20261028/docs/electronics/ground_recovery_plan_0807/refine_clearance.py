from pathlib import Path
import os,sys,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/groundrefine0819'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'hardware/camera_schmitt_native_0745'));import geometry_native as g
m=json.loads((D/'selected20.json').read_text());moves={(8.325,51.75):(8.325,51.9),(9.399,57.201):(9.35,57.25)};items=[]
for r in m['new']:
 for k in['a','b']:
  if tuple(r[k])in moves:r[k]=list(moves[tuple(r[k])])
 if r['type']=='via':
  t=g.via('GND',r['a']);t.SetWidth(p.F_Cu,450000);t.SetDrill(200000)
 else:t=g.track('GND',g.b.GetLayerID(r['layer']),r['a'],r['b'],.3)
 items.append(t)
errors=g.errors(items);print(json.dumps(errors,indent=2))
if errors:raise RuntimeError('refinement not clear')
for r in m['rows']:
 if r.get('path'):r['path']=[list(moves.get(tuple(x),tuple(x)))for x in r['path']]
m['local_clearance_refinement']=[{'target':'R234.2','before':[8.325,51.75],'after':[8.325,51.9],'intent':'clear own courtyard instead of accepting nominal margin'}, {'target':'J104.3/R223.2 shared via','before':[9.399,57.201],'after':[9.35,57.25],'intent':'increase actual circular probe-pad copper clearance from0.12494 to0.19424mm'}]
(D/'selected20_refined.json').write_text(json.dumps(m,indent=2)+'\n')
