from pathlib import Path
import json,hashlib,os
O=Path(__file__).resolve().parent;W=O.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
 if not x:raise RuntimeError(m)
j=json.load(open(O/'results.json'));k=json.load(open(O/'keepout_results.json'))
need(sha(O/'proposed_full104.json')==sha(W/'reconstruction_data8_fullscreen_20261031_0135/proposed_full104.json'),'all full masks exact')
need((j['new_tracks'],j['new_outer_tracks'],j['new_vias'],j['removed_count'])==(148,97,5,0),'exact delta count')
need(not j['unqualified_body_Fab_hits'] and not k['forbidden_intersections'],'geometry hits')
need(k['new_objects_checked']==153 and len(k['board_and_footprint_rule_areas'])==8,'keepout scope')
expected={'CAM_SCL':([8.2,6.575],[8.2,6.15],'44'),'CAM_SDA':([7.8,6.575],[7.8,6.0],'45')};ends=[]
for r in j['rows']:
 if not(r['body_hits']or r['Fab_bbox_hits']):continue
 a,b,pad=expected[r['net']];need(r['type']=='track'and r['layer']=='F.Cu'and r['width_mm']==.15 and r['a']==a and r['b']==b,'only monotonic north terminal escape')
 for h in r['body_hits']+r['Fab_bbox_hits']:need(h['ref']=='U101'and h['actual_pad_ended']==[pad],'only actual terminal target')
 ends.append(r['uuid'])
need(len(ends)==2,'exact two terminal escapes')
# Test negative finite discs at actual full envelope centers using native polygon operations.
os.makedirs('/tmp/sccb0207checks',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/sccb0207checks';import pcbnew as p
board=p.LoadBoard(str(O/'selected_native.kicad_pcb'));env=json.load(open(O/'proposed_full104.json'))['all_static_rectangles'];neg=[]
for ref in ['U101','R231','U301']:
 e=next(e for e in env if e['ref']==ref);x1,y1,x2,y2=e['xy_bounds'];z=p.SHAPE_POLY_SET();z.NewOutline()
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:z.Append(round(x*1e6),round(y*1e6))
 v=p.PCB_VIA(board);v.SetPosition(p.VECTOR2I(round((x1+x2)*5e5),round((y1+y2)*5e5)));v.SetWidth(p.F_Cu,450000);v.SetWidth(p.B_Cu,450000);v.SetDrill(200000);s=p.SHAPE_POLY_SET();v.TransformShapeToPolygon(s,p.F_Cu,0,50,p.ERROR_OUTSIDE);c=p.SHAPE_POLY_SET();c.BooleanIntersection(s,z);area=c.Area()/1e12;need(area>.15,'body negative missed');neg.append({'ref':ref,'area_mm2':area})
(O/'checks_results.json').write_text(json.dumps({'selected_sha256':sha(O/'selected_native.kicad_pcb'),'full104_exact_parent_masks':True,'north_terminal_escape_uuids':ends,'full_body_negative_discs':neg,'finite_edge_min_mm':min(r['outline_gap_mm']for r in j['rows']),'six_operation_gates_not_closed':['J104','J108','JP201','JP202','C106','C107']},indent=2)+'\n')
print('PASS exact delta, masks, two monotonic pad-ended escapes and three body negatives')
