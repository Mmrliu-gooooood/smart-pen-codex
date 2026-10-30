from pathlib import Path
import json, hashlib, copy, math, os
os.environ['XDG_CONFIG_HOME']='/tmp/pen-powerplan2124-verify'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2]
data=json.loads((D/'plan.json').read_text())
S=R/'hardware/complete_net_restore_candidate_2014/native/mainboard_revD.kicad_pcb'
b=p.LoadBoard(str(S));L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def req(a,m):
 if not a:raise ValueError(m)
def validate(d):
 req(d['status']=='READ_ONLY_NOFAB_NOT_ROUTED','qualification')
 req(d['current_drc_fact']==[0,233,0],'baseline')
 req(len(d['bounded_candidates'])==14,'bounded count')
 req(sum(c['finite_geometry_clear'] for c in d['bounded_candidates'])==6,'partial clear count')
 for c in d['bounded_candidates']:
  req(c['finite_geometry_clear']==(not c['conflicts']),'concealed collision')
  for o in c['objects']:
   req(o['width_mm']==(.6 if o['type']=='via' else .5),'power thinning')
 req(sum(x['net']=='3V3_AON'for x in d['pad_contract'])==39,'AON pads')
 sw={(x['ref'],x['pin'])for x in d['pad_contract']if x['net']=='CAM_3V3_SW'}
 req(sw=={('J301','1'),('JP301','2')},'SW endpoint contract')
 req(not any(x['ref']=='JP301' and x['pin']=='1' and x['net']=='CAM_3V3_SW'for x in d['pad_contract']),'JP bridge')
 for f,h in d['inputs'].items():req(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,'input drift')
validate(data)
req((D/'plan_normal.json').read_bytes()==(D/'plan.json').read_bytes(),'normal optimized mismatch')
neg=[]
for name,mut in [ ('false_qualification',lambda d:d.update(status='READY')),('thinned_power',lambda d:d['bounded_candidates'][0]['objects'][0].update(width_mm=.15)),('hidden_conflict',lambda d:d['bounded_candidates'][0].update(finite_geometry_clear=True)),('dropped_pad',lambda d:d['pad_contract'].pop(next(i for i,x in enumerate(d['pad_contract'])if x['net']=='3V3_AON')) ) ]:
 q=copy.deepcopy(data);mut(q)
 try:validate(q)
 except ValueError:neg.append(name)
 else:raise RuntimeError('negative accepted '+name)
def shape(t,l,margin=0):
 z=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(z,l,margin,50,p.ERROR_OUTSIDE);return z
V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))
def obj(o):
 if o['type']=='via':
  t=p.PCB_VIA(b);t.SetPosition(V(o['start_mm']));t.SetWidth(p.F_Cu,round(o['width_mm']*1e6));t.SetDrill(round(o['drill_mm']*1e6));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH)
 else:
  t=p.PCB_TRACK(b);t.SetStart(V(o['start_mm']));t.SetEnd(V(o['end_mm']));t.SetWidth(round(o['width_mm']*1e6));t.SetLayer(b.GetLayerID(o['layer']))
 t.SetNetCode(b.GetNetcodeFromNetname(o['net']));return t
outline=p.SHAPE_POLY_SET();req(b.GetBoardPolygonOutlines(outline),'outline')
extra=[]
for c in data['bounded_candidates']:
 edges=[];rules=[];via_same_pad=[]
 for i,o in enumerate(c['objects']):
  t=obj(o);l=p.F_Cu if o['type']=='via'else t.GetLayer();q=shape(t,l,250000);q.BooleanSubtract(outline)
  if q.Area()>1:edges.append({'object':i,'outside_mm2':q.Area()/1e12})
  for z in b.Zones():
   if not z.GetIsRuleArea()or not(z.GetDoNotAllowVias()if o['type']=='via'else z.GetDoNotAllowTracks()):continue
   for l in L:
    if t.IsOnLayer(l)and z.IsOnLayer(l):
     q=shape(t,l);q.BooleanIntersection(z.Outline())
     if q.Area()>1:rules.append({'object':i,'zone':z.GetZoneName(),'layer':b.GetLayerName(l)})
  if o['type']=='via':
   for f in b.GetFootprints():
    for pad in f.Pads():
     if pad.GetNetname()!=o['net']:continue
     for l in L:
      if pad.IsOnLayer(l):
       q=shape(t,l);q.BooleanIntersection(shape(pad,l))
       if q.Area()>1:via_same_pad.append({'object':i,'pad':f.GetReference()+'.'+pad.GetNumber(),'layer':b.GetLayerName(l)})
 extra.append({'name':c['name'],'native_edge_025mm_conflicts':edges,'native_rule_conflicts':rules,'same_net_via_annulus_pad_overlap':via_same_pad,'local_clear_with_added_checks':c['finite_geometry_clear']and not edges and not rules and not via_same_pad})
result={'status':'BOUNDED_PARTIAL_GEOMETRY_CHECK_ONLY_NOFAB','baseline_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'negative_rejections':neg,'cases':extra,'clear_count':sum(x['local_clear_with_added_checks']for x in extra),'all_power_restored':False,'native_board_saved':False,'native_full_DRC_run':False,'fresh_fill_run':False,'qualified_current_or_return':False}
print(json.dumps(result,indent=2))
