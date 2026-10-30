from pathlib import Path
import os,json,math,hashlib,shutil,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/gnd-independent2317'
import pcbnew as p
D=Path(__file__).resolve().parent; R=D.parents[1]; S=R/'hardware/gnd_conservative_recovery_2305'; B=R/'hardware/aon_entry_bridge_candidate_2156'; O=R/'hardware/j202_low_speed_reference_candidate'
b=p.LoadBoard(str(S/'native/mainboard_revD.kicad_pcb')); base=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb')); old=p.LoadBoard(str(O/'native/mainboard_revD.kicad_pcb'))
L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
def need(c,s):
 if not c: raise RuntimeError(s)
def poly(o,l):
 q=p.SHAPE_POLY_SET();o.TransformShapeToPolygon(q,l,0,100,p.ERROR_INSIDE)
 if isinstance(o,p.PCB_VIA):
  h=p.SHAPE_POLY_SET();h.NewOutline();v=o.GetPosition();rad=o.GetDrillValue()/2
  for k in range(512):h.Append(round(v.x+rad*math.cos(k*math.tau/512)),round(v.y+rad*math.sin(k*math.tau/512)))
  q.BooleanSubtract(h)
 return q
def graph(board,net):
 nodes=[]
 for fp in board.GetFootprints():
  for pad in fp.Pads():
   if pad.GetNetname()==net:nodes.append((pad.m_Uuid.AsString(),fp.GetReference()+'.'+pad.GetNumber(),{l:poly(pad,l) for l in L if pad.IsOnLayer(l)}))
 for t in board.GetTracks():
  if t.GetNetname()==net:nodes.append((t.m_Uuid.AsString(),None,{l:poly(t,l) for l in L if t.IsOnLayer(l)}))
 for z in board.Zones():
  if z.GetIsRuleArea() or z.GetNetname()!=net:continue
  for l in L:
   if z.IsOnLayer(l):
    q=z.GetFilledPolysList(l)
    for i in range(q.OutlineCount()):nodes.append((z.m_Uuid.AsString()+':'+str(l)+':'+str(i),None,{l:q.UnitSet(i)}))
 adj={n[0]:set() for n in nodes}
 for i,(u,_,si) in enumerate(nodes):
  for v,_,sj in nodes[:i]:
   for l in set(si)&set(sj):
    if not si[l].BBox().Intersects(sj[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(si[l],sj[l])
    if q.Area()>10:adj[u].add(v);adj[v].add(u);break
 return nodes,adj
def reach(adj,start,omit=set()):
 seen={start};todo=[start]
 while todo:
  for n in adj[todo.pop()]-seen-omit:seen.add(n);todo.append(n)
 return seen
plan=json.loads((S/'plan.json').read_text()); groups=[c for c in plan['components'] if c['accepted_preflight']];need(len(groups)==17,'group count');ids={u for c in groups for u in c['objects']};need(len(ids)==96,'object count');need(not any(c['id']==37 for c in groups),'37 included')
results={}
for net,core,want in [('GND','J106.3',30),('3V3_AON','J106.2',1)]:
 nodes,adj=graph(b,net);root=next(u for u,n,_ in nodes if n==core);rr=reach(adj,root);connected=[n for u,n,_ in nodes if n and u in rr];need(len(connected)==want,'core pads');results[net]={'total_physical_pads':sum(n is not None for _,n,_ in nodes),'connected':sorted(connected),'region_nodes_at_core':len([u for u,n,_ in nodes if ':' in u and u in rr])}
 if net=='GND':
  negatives=[]
  for c in groups:
   padids={u for u,n,_ in nodes if n in c['pads']};need(padids<=rr,'group not core');nr=reach(adj,root,set(c['objects']));need(not padids&nr,'group deletion not isolating');negatives.append(c['id'])
  results['whole_group_negatives']=negatives
# geometry/width/drill/UUID comparisons, using actual all-layer set
sig=lambda t:(t.GetNetname(),t.GetLayerSet().FmtHex(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetDrillValue() if isinstance(t,p.PCB_VIA) else None)
t={x.m_Uuid.AsString():x for x in b.GetTracks()};bt={x.m_Uuid.AsString():x for x in base.GetTracks()};ot={x.m_Uuid.AsString():x for x in old.GetTracks()};need(set(t)-set(bt)==ids,'added UUID delta');need(all(sig(t[u])==sig(bt[u]) for u in bt),'old changed');need(all(sig(t[u])==sig(ot[u]) for u in ids),'added differs original');results['base_objects_preserved']=len(bt);results['added_original_objects']=len(ids)
# Exact unmodified source/project/rules and actual pad/courtyard data held by untouched FP text.
for f in ['mainboard_revD.kicad_pro','mainboard_revD.kicad_dru','mainboard_revD.kicad_sch']:
 need((S/'native'/f).read_bytes()==(B/'native'/f).read_bytes(),'source binding changed '+f)
results['source_project_rules_unchanged']=True
(D/'independent.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
