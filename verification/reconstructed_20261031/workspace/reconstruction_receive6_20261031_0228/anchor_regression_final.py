from pathlib import Path
import pcbnew as p,json
from anchor_policy import native_via_layers
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'));b.BuildConnectivity();c=b.GetConnectivity();layers=[p.F_Cu,p.In2_Cu,p.In3_Cu,p.B_Cu];rows=[]
for net in ['CAM_PCLK','CAM_HREF']:
 root=next(q for f in b.GetFootprints()for q in f.Pads()if f.GetReference()=='U101'and q.GetNetname()==net);todo=[root];seen=set();items=[]
 while todo:
  a=todo.pop();u=a.m_Uuid.AsString()
  if u in seen:continue
  seen.add(u);items.append(a);todo.extend(c.GetConnectedTracks(a));todo.extend(c.GetConnectedPads(a))
 for a in items:
  if a.GetClass()!='PCB_VIA':continue
  expected=[l for l in layers if a.IsOnLayer(l)];actual=native_via_layers(a,layers)
  if actual!=expected or len(actual)!=4:raise RuntimeError('native layer seed contract')
  rows.append({'net':net,'uuid':a.m_Uuid.AsString(),'native_class':a.GetClass(),'python_type':type(a).__name__,'old_isinstance_omits_via_branch':not isinstance(a,p.PCB_VIA),'all_native_routing_layers':[b.GetLayerName(l)for l in actual]})
if len(rows)!=9 or not all(q['old_isinstance_omits_via_branch']for q in rows):raise RuntimeError('wrapper negative not exercised')
r={'rows':sorted(rows,key=lambda x:x['uuid']),'scope':'Actual final connected via objects and native layer sets, not Python subclass assumption. Spatial masks still independently restrict usable search seeds; this does not authorize new In2 outside source window. Old instanceof behavior is a negative regression, not old-board invalidation.'};(D/('anchor_regression_optimized.json'if not __debug__ else'anchor_regression.json')).write_text(json.dumps(r,indent=2));print('9 actual wrapped-via fixtures pass')
