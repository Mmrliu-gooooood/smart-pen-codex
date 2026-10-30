from pathlib import Path
import os,sys,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/r2250821';import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'hardware/camera_schmitt_native_0745'));import geometry_native as g
m=json.loads((D/'selected20_refined.json').read_text());rows=[r for r in m['new']if r['target_pad']!='R225.2'];pts=[(5.325,43.3),(4.525,44.1),(2.84,44.1)]
for a,z in zip(pts,pts[1:]):rows.append({'target_pad':'R225.2','type':'track','net':'GND','layer':'B.Cu','a':list(a),'b':list(z),'width':.3,'drill':None})
items=[]
for r in rows:
 if r['type']=='via':t=g.via('GND',r['a']);t.SetWidth(p.F_Cu,450000);t.SetDrill(200000)
 else:t=g.track('GND',g.b.GetLayerID(r['layer']),r['a'],r['b'],.3)
 items.append(t)
e=g.errors(items);print(json.dumps(e,indent=2))
if not e:
 m['new']=rows
 for r in m['rows']:
  if r['pad']=='R225.2':r['path']=[list(x)for x in pts];r['anchor']='proposed_R220_ground_branch';r['new_via']=False
 m['local_clearance_refinement'].append({'target':'R225.2','intent':'avoid U202 body through via by B.Cu dogleg to proposed R220 core branch; no existing copper modified','path':pts})
 (D/'selected20_final.json').write_text(json.dumps(m,indent=2)+'\n')
