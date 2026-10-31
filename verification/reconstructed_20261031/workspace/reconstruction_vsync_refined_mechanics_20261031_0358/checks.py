from pathlib import Path
import json,hashlib,os
O=Path(__file__).resolve().parent;W=O.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
j=json.load(open(O/'results.json'));k=json.load(open(O/'keepout_results.json'))
need(sha(O/'proposed_full104.json')==sha(W/'reconstruction_receive_margin_mechanics_20261031_0305/proposed_full104.json'),'exact screened pose masks')
need((j['new_tracks'],j['new_outer_tracks'],j['new_vias'],j['removed_count'])==(161,68,6,1),'exact counts');need(not j['unqualified_body_Fab_hits']and not k['forbidden_intersections'],'bad projection')
expected={
 ('CAM_VSYNC','U101','22'):([6.2,13.425],[6.2,13.85]),
 ('CAM_VSYNC','U202','5'):([5.675,43.1375],[5.675,41.65]),
 ('CAM_VSYNC','R219','1'):([5.375,39.5],[4.55,39.5]),
 ('SENS_D6','U201','15'):([3.725,36.8625],[3.725,37.8])}

seen=set()
for r in j['rows']:
 for h in r['body_hits']+r['Fab_bbox_hits']:
  need(r['type']=='track'and len(h['actual_pad_ended'])==1,'actual terminal only');key=(r['net'],h['ref'],h['actual_pad_ended'][0]);need(key in expected,'unexpected terminal');a,b=expected[key];need(r['a']==a and r['b']==b,'exact monotonic terminal escape');seen.add(key)
need(seen==set(expected),'all exact terminal exits checked')
# Independent body-overlap negative via at actual proposed occupied centers.
os.makedirs('/tmp/recv0302',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/recv0302';import pcbnew as p
b=p.LoadBoard(str(O/'selected_native.kicad_pcb'));env=json.load(open(O/'proposed_full104.json'))['all_static_rectangles'];neg=[]
for ref in ['U101','U201','R219']:
 e=next(e for e in env if e['ref']==ref);x1,y1,x2,y2=e['xy_bounds'];q=p.SHAPE_POLY_SET();q.NewOutline()
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:q.Append(round(x*1e6),round(y*1e6))
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(round((x1+x2)*5e5),round((y1+y2)*5e5)));v.SetWidth(p.F_Cu,450000);v.SetWidth(p.B_Cu,450000);v.SetDrill(200000);s=p.SHAPE_POLY_SET();v.TransformShapeToPolygon(s,p.F_Cu,0,50,p.ERROR_OUTSIDE);c=p.SHAPE_POLY_SET();c.BooleanIntersection(s,q);a=c.Area()/1e12;need(a>.15,'negative missed');neg.append({'ref':ref,'area_mm2':a})
# Sole replacement preserves actual U201.15 terminal finite segment as a subset.
delta=json.load(open(O/'native_derived_delta.json'));need(delta['removed']==['7536cae6-fbca-555e-a61d-9079d587d78c'],'single bounded removal')
base=p.LoadBoard(str(W/'reconstruction_receive_margin_mechanics_20261031_0305/selected_native.kicad_pcb'));old=next(t for t in base.GetTracks()if t.m_Uuid.AsString()==delta['removed'][0]);need(old.GetNetname()=='SENS_D6'and old.GetLayer()==p.F_Cu and old.GetWidth()==150000,'old leaf identity')
new=next(t for t in b.GetTracks()if t.GetNetname()=='SENS_D6'and t.m_Uuid.AsString()in delta['added']and t.GetStart()==p.VECTOR2I(3725000,36862500));s1=p.SHAPE_POLY_SET();s2=p.SHAPE_POLY_SET();new.TransformShapeToPolygon(s1,p.F_Cu,0,50,p.ERROR_OUTSIDE);old.TransformShapeToPolygon(s2,p.F_Cu,0,50,p.ERROR_OUTSIDE);extra=p.SHAPE_POLY_SET();extra.BooleanSubtract(s1,s2);need(extra.Area()/1e12<1e-8,'new U201 terminal not inherited subset')
need(sorted((tuple(r['a']),tuple(r['b']))for r in j['rows']if r['net']=='SENS_D6')==sorted([((3.725,36.8625),(3.725,37.8)),((3.725,37.8),(3.4,38.05)),((3.4,38.05),(3.4,38.9)),((3.4,38.9),(3.725,39.3))]),'exact four-segment reroute')
(O/'checks_results.json').write_text(json.dumps({'native_sha256':sha(O/'selected_native.kicad_pcb'),'exact_terminal_scopes':[list(k)for k in sorted(seen)],'full_body_negative_discs':neg,'six_operation_gates_still_open':True,'SENS_D6_terminal_added_projection_mm2':extra.Area()/1e12,'unchanged_pose_source_mechanical_manifest_sha256':sha(W/'reconstruction_receive_margin_mechanics_20261031_0305/manifest.json')},indent=2)+'\n')
