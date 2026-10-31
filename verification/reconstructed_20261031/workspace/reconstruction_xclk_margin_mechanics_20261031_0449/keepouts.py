from pathlib import Path
import json,hashlib,os
os.makedirs('/tmp/keepout0153',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/keepout0153';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;P=O;q=P/'selected_native.kicad_pcb';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
need(sha(q)=='6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08','selected native')
b=p.LoadBoard(str(q));base=p.LoadBoard(str(W/'reconstruction_vsync_refined_mechanics_20261031_0358/selected_native.kicad_pcb'));layers=list(b.GetEnabledLayers().CuStack());need(layers==[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu],'actual six-layer native stack')
def rules(board):
 out=[]
 for owner,z in [('BOARD',z)for z in board.Zones()]+[(f.GetReference(),z)for f in board.GetFootprints()for z in f.Zones()]:
  if not z.GetIsRuleArea():continue
  poly=z.Outline();geometry=[]
  for i in range(poly.OutlineCount()):
   c=poly.Outline(i);geometry.append({'outer':[(c.CPoint(k).x,c.CPoint(k).y)for k in range(c.PointCount())],'holes':[]})
   for h in range(poly.HoleCount(i)):
    c=poly.Hole(i,h);geometry[-1]['holes'].append([(c.CPoint(k).x,c.CPoint(k).y)for k in range(c.PointCount())])
  out.append(({'owner':owner,'name':z.GetZoneName(),'uuid':z.m_Uuid.AsString(),'layers':[board.GetLayerName(l)for l in layers if z.IsOnLayer(l)],'no_tracks':z.GetDoNotAllowTracks(),'no_vias':z.GetDoNotAllowVias(),'no_pads':z.GetDoNotAllowPads(),'no_footprints':z.GetDoNotAllowFootprints(),'no_pour':z.GetDoNotAllowCopperPour(),'geometry_nm':geometry},z))
 return out
R=rules(b);oldR=rules(base);need(sorted([r for r,z in R],key=str)==sorted([r for r,z in oldR],key=str),'native rule areas changed')
ids=set(json.load(open(P/'native_derived_delta.json'))['added']);hits=[];tested=0
for t in b.GetTracks():
 if t.m_Uuid.AsString()not in ids:continue
 via=isinstance(t,p.PCB_VIA)
 for info,z in R:
  if not(info['no_vias']if via else info['no_tracks']):continue
  for layer in layers:
   if not z.IsOnLayer(layer)or not t.IsOnLayer(layer):continue
   s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,layer,0,50,p.ERROR_OUTSIDE);common=p.SHAPE_POLY_SET();common.BooleanIntersection(s,z.Outline());v=common.Area()/1e12;tested+=1
   if v>1e-8:hits.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'layer':b.GetLayerName(layer),'rule_owner':info['owner'],'rule':info['name'],'area_mm2':v})
need(not hits,'forbidden copper/rule-area intersection')
# Deliberate LIS2DW12-body via tests explicit native no-via area; U101 embedded areas are pour-only.
neg_zone=next(z for info,z in R if info['name']=='LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA');c=neg_zone.Outline().Outline(0);xs=[c.CPoint(i).x for i in range(c.PointCount())];ys=[c.CPoint(i).y for i in range(c.PointCount())];center=((min(xs)+max(xs))//2,(min(ys)+max(ys))//2)
v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(*center));v.SetWidth(p.F_Cu,450000);v.SetWidth(p.B_Cu,450000);v.SetDrill(200000);negative=[]
for info,z in R:
 if not info['no_vias']or not z.IsOnLayer(p.F_Cu):continue
 s=p.SHAPE_POLY_SET();v.TransformShapeToPolygon(s,p.F_Cu,0,50,p.ERROR_OUTSIDE);c=p.SHAPE_POLY_SET();c.BooleanIntersection(s,z.Outline());a=c.Area()/1e12
 if a>1e-8:negative.append({'rule':info['name'],'owner':info['owner'],'area_mm2':a})
need(negative,'explicit keepout negative missed')
(O/'keepout_results.json').write_text(json.dumps({'selected_sha256':sha(q),'baseline_sha256':sha(W/'reconstruction_vsync_refined_mechanics_20261031_0358/selected_native.kicad_pcb'),'board_and_footprint_rule_areas': [r for r,z in R],'rule_areas_unchanged_from_5f':True,'all_native_copper_layers':[b.GetLayerName(l)for l in layers],'new_objects_checked':len(ids),'applicable_object_rule_layer_tests':tested,'forbidden_intersections':hits,'negative_native_zone_center_mm':[center[0]/1e6,center[1]/1e6],'negative_LIS2DW12_center_via_hits':negative,'scope':'explicit native no-track/no-via areas; not manufacturer service/tool/tenting qualification'},indent=2)+'\n')
print('PASS',len(R),'ruleareas',tested,'tests; negative',negative)
