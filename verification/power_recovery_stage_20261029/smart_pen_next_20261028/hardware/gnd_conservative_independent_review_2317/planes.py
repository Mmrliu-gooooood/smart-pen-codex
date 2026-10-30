from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/gnd-review-plane2317'
import pcbnew as p
D=Path(__file__).resolve().parent; H=D.parent
boards={k:p.LoadBoard(str(H/v/'native/mainboard_revD.kicad_pcb'))for k,v in [('base','aon_entry_bridge_candidate_2156'),('rejected','gnd_fixed_branch_candidate_2159'),('chosen','gnd_conservative_recovery_2305')]}
polys={};eroded={};out={}
for k,b in boards.items():
 z=next(z for z in b.Zones() if z.GetNetname()=='3V3_AON');q=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In2_Cu));polys[k]=q;e=p.SHAPE_POLY_SET(q);e.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);eroded[k]=e;out[k]={'filled_area_mm2':q.Area()/1e12,'eroded_count':e.OutlineCount()}
if [out[x]['eroded_count'] for x in ['base','rejected','chosen']]!=[7,8,7]:raise RuntimeError('erosion pattern')
maprows=[]
for i in range(eroded['chosen'].OutlineCount()):
 found=[]
 for j in range(eroded['base'].OutlineCount()):
  x=p.SHAPE_POLY_SET();x.BooleanIntersection(eroded['chosen'].UnitSet(i),eroded['base'].UnitSet(j))
  if x.Area()>10:found.append(j)
 if len(found)!=1:raise RuntimeError('not one match')
 maprows.append(found[0])
if sorted(maprows)!=list(range(7)):raise RuntimeError('not bijective')
bs={z.m_Uuid.AsString():z for z in boards['base'].Zones()};ground=[]
for z in boards['chosen'].Zones():
 if z.GetNetname()=='GND' and not z.GetIsRuleArea():
  for layer in z.GetLayerSet().Seq():
   if z.GetFilledPolysList(layer).Format()!=bs[z.m_Uuid.AsString()].GetFilledPolysList(layer).Format():raise RuntimeError('GND fill changed')
   ground.append([z.m_Uuid.AsString(),boards['chosen'].GetLayerName(layer)])
rt={t.m_Uuid.AsString()for t in boards['rejected'].GetTracks()};ct={t.m_Uuid.AsString()for t in boards['chosen'].GetTracks()};removed=rt-ct;plan=json.loads((H/'gnd_fixed_branch_candidate_2159/plan.json').read_text());g37=next(c for c in plan['components']if c['id']==37)
if removed!=set(g37['objects']) or ct-rt:raise RuntimeError('not exact group37 reduction')
out.update({'chosen_to_base_fragment_mapping':maprows,'AON_area_delta_mm2':out['chosen']['filled_area_mm2']-out['base']['filled_area_mm2'],'exact_GND_planes':ground,'exact_rejected_to_chosen_removed_objects':len(removed),'not_ampacity_or_load_path_proof':True});(D/'planes.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
