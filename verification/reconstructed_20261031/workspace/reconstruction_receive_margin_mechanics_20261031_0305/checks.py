from pathlib import Path
import json,hashlib,os
O=Path(__file__).resolve().parent;W=O.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
j=json.load(open(O/'results.json'));k=json.load(open(O/'keepout_results.json'))
need(sha(O/'proposed_full104.json')==sha(W/'reconstruction_receive_pose_mechanics_20261031_0236/proposed_full104.json'),'exact screened pose masks')
need((j['new_tracks'],j['new_outer_tracks'],j['new_vias'],j['removed_count'])==(191,102,12,9),'exact counts');need(not j['unqualified_body_Fab_hits']and not k['forbidden_intersections'],'bad projection')
expected={
 ('GND','R230','2'):([11.1,33.425],[11.1,32.325]),
 ('CAM_PCLK','U202','4'):([6.325,43.1375],[6.325,42.1]),
 ('CAM_PCLK','U101','21'):([5.8,13.425],[5.9375,14.3]),
 ('GND','R229','2'):([5.325,40.9],[5.95,40.55]),
 ('GND','C104','2'):([6.775,15.8],[7.85,15.2]),
 ('CAM_HREF','U202','6'):([5.025,43.1375],[5.025,42.1]),
 ('CAM_HREF','R220','1'):([1.2,45],[1.2,44.15]),
 ('GND','R219','2'):([7.025,39.5],[6.8,40.725]),
 ('CAM_PCLK','R218','1'):([3.675,41.5],[3.1,41.5]),
 ('CAM_HREF','U101','23'):([6.6,13.425],[6.6,13.85])}
seen=set()
for r in j['rows']:
 for h in r['body_hits']+r['Fab_bbox_hits']:
  need(r['type']=='track'and len(h['actual_pad_ended'])==1,'actual terminal only');key=(r['net'],h['ref'],h['actual_pad_ended'][0]);need(key in expected,'unexpected terminal');a,b=expected[key];need(r['a']==a and r['b']==b,'exact monotonic terminal escape');seen.add(key)
need(seen==set(expected),'all exact terminal exits checked')
# Independent body-overlap negative via at actual proposed occupied centers.
os.makedirs('/tmp/recv0302',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/recv0302';import pcbnew as p
b=p.LoadBoard(str(O/'selected_native.kicad_pcb'));env=json.load(open(O/'proposed_full104.json'))['all_static_rectangles'];neg=[]
for ref in ['U101','R230','R219']:
 e=next(e for e in env if e['ref']==ref);x1,y1,x2,y2=e['xy_bounds'];q=p.SHAPE_POLY_SET();q.NewOutline()
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:q.Append(round(x*1e6),round(y*1e6))
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(round((x1+x2)*5e5),round((y1+y2)*5e5)));v.SetWidth(p.F_Cu,450000);v.SetWidth(p.B_Cu,450000);v.SetDrill(200000);s=p.SHAPE_POLY_SET();v.TransformShapeToPolygon(s,p.F_Cu,0,50,p.ERROR_OUTSIDE);c=p.SHAPE_POLY_SET();c.BooleanIntersection(s,q);a=c.Area()/1e12;need(a>.15,'negative missed');neg.append({'ref':ref,'area_mm2':a})
(O/'checks_results.json').write_text(json.dumps({'native_sha256':sha(O/'selected_native.kicad_pcb'),'exact_terminal_scopes':[list(k)for k in sorted(seen)],'full_body_negative_discs':neg,'six_operation_gates_still_open':True,'source_pose_package_manifest_sha256':sha(W/'reconstruction_receive_pose_mechanics_20261031_0236/manifest.json')},indent=2)+'\n')
