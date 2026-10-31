from pathlib import Path
import json,hashlib,os
O=Path(__file__).resolve().parent;W=O.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
j=json.load(open(O/'results.json'));k=json.load(open(O/'keepout_results.json'))
need(sha(O/'proposed_full104.json')==sha(W/'reconstruction_vsync_refined_mechanics_20261031_0358/proposed_full104.json'),'exact screened pose masks')
need((j['new_tracks'],j['new_outer_tracks'],j['new_vias'],j['removed_count'])==(259,81,6,77),'exact counts');need(not j['unqualified_body_Fab_hits']and not k['forbidden_intersections'],'bad projection')
expected={
 ('CAM_XCLK','U101','43'):([8.6,6.575],[8.6,6.11]),
 ('CAM_SCL','U101','44'):([8.2,6.575],[8.2,6.0]),
 ('CAM_SDA','U101','45'):([7.8,6.575],[7.925,5.45]),
 ('CAM_XCLK','U203','4'):([6.325,53.1375],[6.325,51.95]),
 ('CAM_XCLK','R221','1'):([2.175,56],[1.4,56])}

seen=set()
for r in j['rows']:
 for h in r['body_hits']+r['Fab_bbox_hits']:
  need(r['type']=='track'and len(h['actual_pad_ended'])==1,'actual terminal only');key=(r['net'],h['ref'],h['actual_pad_ended'][0]);need(key in expected,'unexpected terminal');a,b=expected[key];need(r['a']==a and r['b']==b,'exact monotonic terminal escape');seen.add(key)
need(seen==set(expected),'all exact terminal exits checked')
# Independent body-overlap negative via at actual proposed occupied centers.
os.makedirs('/tmp/recv0302',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/recv0302';import pcbnew as p
b=p.LoadBoard(str(O/'selected_native.kicad_pcb'));env=json.load(open(O/'proposed_full104.json'))['all_static_rectangles'];neg=[]
for ref in ['U101','U203','R221']:
 e=next(e for e in env if e['ref']==ref);x1,y1,x2,y2=e['xy_bounds'];q=p.SHAPE_POLY_SET();q.NewOutline()
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:q.Append(round(x*1e6),round(y*1e6))
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(round((x1+x2)*5e5),round((y1+y2)*5e5)));v.SetWidth(p.F_Cu,450000);v.SetWidth(p.B_Cu,450000);v.SetDrill(200000);s=p.SHAPE_POLY_SET();v.TransformShapeToPolygon(s,p.F_Cu,0,50,p.ERROR_OUTSIDE);c=p.SHAPE_POLY_SET();c.BooleanIntersection(s,q);a=c.Area()/1e12;need(a>.15,'negative missed');neg.append({'ref':ref,'area_mm2':a})
# Restrict every removed object to declared three control nets, never PDN/USB.
from collections import Counter
delta=json.load(open(O/'native_derived_delta.json'));base=p.LoadBoard(str(W/'reconstruction_vsync_refined_mechanics_20261031_0358/selected_native.kicad_pcb'));removed=Counter(t.GetNetname()for t in base.GetTracks()if t.m_Uuid.AsString()in delta['removed']);need(dict(removed)=={'CAM_SDA':41,'CAM_IO_EN':28,'CAM_SCL':8},'declared removal nets/counts')
(O/'checks_results.json').write_text(json.dumps({'native_sha256':sha(O/'selected_native.kicad_pcb'),'exact_terminal_scopes':[list(k)for k in sorted(seen)],'full_body_negative_discs':neg,'six_operation_gates_still_open':True,'removed_control_nets':dict(removed),'unchanged_pose_source_mechanical_manifest_sha256':sha(W/'reconstruction_vsync_refined_mechanics_20261031_0358/manifest.json')},indent=2)+'\n')
