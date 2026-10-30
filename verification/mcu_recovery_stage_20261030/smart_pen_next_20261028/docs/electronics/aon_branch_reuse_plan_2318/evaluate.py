from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/pen-aon-eval2318'
import pcbnew as p
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[2];B=R/'hardware/gnd_conservative_recovery_2305/native/mainboard_revD.kicad_pcb';O=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(B));a=p.LoadBoard(str(O));plan=json.loads((D/'plan.json').read_text());old={t.m_Uuid.AsString():t for t in a.GetTracks()};bn=build(b);an=build(a);on={x[0]:x for x in an['3V3_AON']};outline=p.SHAPE_POLY_SET()
if not b.GetBoardPolygonOutlines(outline):raise RuntimeError('board outline')
def reach(nodes,start,omit=set()):
 nodes=[n for n in nodes if n[0]not in omit];lookup={n[0]:n for n in nodes};seen={start};todo=[start]
 while todo:
  _,_,x=lookup[todo.pop()]
  for name,_,y in nodes:
   if name in seen:continue
   for l in x.keys()&y.keys():
    if not x[l].BBox().Intersects(y[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(x[l],y[l])
    if q.Area()>1:seen.add(name);todo.append(name);break
 return seen
rows=[];selected=[]
for g in plan['components']:
 if not g['accepted_preflight']:continue
 edge=[];rules=[];native=[]
 for u in g['objects']:
  t=old[u];layer=p.F_Cu if isinstance(t,p.PCB_VIA)else t.GetLayer();q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,layer,250000,100,p.ERROR_OUTSIDE);q.BooleanSubtract(outline)
  if q.Area()>1:edge.append(u)
  for z in b.Zones():
   if not z.GetIsRuleArea():continue
   if not(z.GetDoNotAllowVias()if isinstance(t,p.PCB_VIA)else z.GetDoNotAllowTracks()):continue
   for l in L:
    if z.IsOnLayer(l)and t.IsOnLayer(l):
     q=shape(t,l);q.BooleanIntersection(z.Outline())
     if q.Area()>1:rules.append(dict(object=u,rule_uuid=z.m_Uuid.AsString(),layer=b.GetLayerName(l)))
  native.append(dict(uuid=u,type='via'if isinstance(t,p.PCB_VIA)else'track',net=t.GetNetname(),actual_layers=[b.GetLayerName(l)for l in L if t.IsOnLayer(l)],start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width_mm=(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6,drill_mm=t.GetDrillValue()/1e6 if isinstance(t,p.PCB_VIA)else None))
 nodes=bn['3V3_AON']+[on[u]for u in g['objects']];r=reach(nodes,'J106.2');connected=set(g['objects'])|set(g['pads'])<=r
 row=dict(id=g['id'],pads=g['pads'],objects=g['objects'],geometry=native,whole_subgraph_reaches_current_AON_core_in_prefill_model=connected,edge_conflicts=edge,rule_conflicts=rules,proposed_for_bounded_native_trial=connected and not edge and not rules)
 rows.append(row)
 if row['proposed_for_bounded_native_trial']:selected.append(g)
ids=[u for g in selected for u in g['objects']];nodes=bn['3V3_AON']+[on[u]for u in ids];r=reach(nodes,'J106.2');corepads=sorted(n for n,pad,_ in nodes if pad and n in r);neg=[]
for g in selected:
 rr=reach(nodes,'J106.2',set(g['objects']));missing=sorted(set(g['pads'])-rr)
 if missing!=sorted(g['pads']):raise RuntimeError('group deletion not causal')
 neg.append(dict(group=g['id'],removed_objects=len(g['objects']),all_group_pads_disconnect=True))
# Conservative planar cutout estimate only; no ZONE_FILLER/new PCB is executed here.
cut=p.SHAPE_POLY_SET();ground=[];groundBefore={};groundAfter={}
for u in ids:
 t=old[u]
 if not isinstance(t,p.PCB_VIA):continue
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,p.In1_Cu,150000,100,p.ERROR_OUTSIDE);cut.BooleanAdd(q)
for z in b.Zones():
 if z.GetIsRuleArea()or z.GetNetname()!='GND':continue
 for l in L:
  if not z.IsOnLayer(l):continue
  q=native_fractured_once(z.GetFilledPolysList(l));after=p.SHAPE_POLY_SET(q);after.BooleanSubtract(cut);before_er=p.SHAPE_POLY_SET(q);before_er.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);after_er=p.SHAPE_POLY_SET(after);after_er.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
  ground.append(dict(zone_uuid=z.m_Uuid.AsString(),layer=b.GetLayerName(l),planned_antipad_removed_mm2=(q.Area()-after.Area())/1e12,before_eroded_025_pieces=before_er.OutlineCount(),after_cutout_eroded_025_pieces=after_er.OutlineCount()))
  groundBefore.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(q);groundAfter.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(after)
ref=[]
for t in b.GetTracks():
 if not t.GetNetname().startswith('SENS_')or isinstance(t,p.PCB_VIA):continue
 l=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;q=shape(t,t.GetLayer());oldq=p.SHAPE_POLY_SET();oldq.BooleanIntersection(q,groundBefore[l]);newq=p.SHAPE_POLY_SET();newq.BooleanIntersection(q,groundAfter[l]);lost=p.SHAPE_POLY_SET(oldq);lost.BooleanSubtract(newq)
 ref.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),reference_layer=b.GetLayerName(l),additional_uncovered_projection_mm2=lost.Area()/1e12))
# Hypothetical ground graph after planned via cutouts. Still not a fresh-fill/island-removal result.
gnodes=[n for n in bn['GND']if '/'not in n[0]]
for l,q in groundAfter.items():
 for i in range(q.OutlineCount()):gnodes.append(('planned_ground/'+str(l)+'/'+str(i),False,{l:q.UnitSet(i)}))
gbefore=reach(bn['GND'],'J106.3');gafter=reach(gnodes,'J106.3');gpadbefore=sorted(n for n,pad,_ in bn['GND']if pad and n in gbefore);gpadafter=sorted(n for n,pad,_ in gnodes if pad and n in gafter)
if gpadbefore!=gpadafter:raise RuntimeError('planned cutout disconnects present ground core pads')
via_ids=[u for u in ids if isinstance(old[u],p.PCB_VIA)];holes=[]
for i,u in enumerate(via_ids):
 for v in via_ids[:i]:
  x,y=old[u],old[v];gap=(math.hypot(x.GetPosition().x-y.GetPosition().x,x.GetPosition().y-y.GetPosition().y)-(x.GetDrillValue()+y.GetDrillValue())/2)/1e6
  if gap<.25-1e-6:raise RuntimeError('candidate pair drill clearance')
  holes.append(dict(a=u,b=v,gap_mm=gap))
print(json.dumps(dict(status='READ_ONLY_AON_WHOLE_SUBGRAPH_PROPOSAL_NOT_NATIVE',base_pcb_sha=hashlib.sha256(B.read_bytes()).hexdigest(),base_copper_objects=len(list(b.GetTracks())),candidate_via_count=len(via_ids),candidate_drill_pair_checks=holes,prefill_cutout_ground_core_pads_before=gpadbefore,prefill_cutout_ground_core_pads_after=gpadafter,geometrically_screened_groups=rows,proposed_group_count=len(selected),proposed_objects=len(ids),proposed_group_ids=[g['id']for g in selected],hypothetical_core_pad_count=len(corepads),hypothetical_core_pad_names=corepads,total_AON_physical_pads=39,whole_group_deletion_model_negatives=neg,ground_plane_antipad_estimate=ground,existing_SENS_reference_projection_estimate=ref,unchanged_SENS_VIO_domain=True,actual_source_file_unchanged=True,not_yet_run=['Native materialization, full DRC/parity and fresh refill','Ground core pad connectivity after actual new antipads/fill','Path-specific current/thermal and return qualification','Other AON branches; moved VCCA+decoupling joint reroute'],limits=['Hypothetical finite-copper connectivity uses current filled copper; not a native post-fill result.','Ground cutout subtraction is a planning bound, not a replacement for fresh fill or island removal.','No shorter/narrower source tracks, supply/return cuts or GPIO/domain changes made.']),indent=2))
