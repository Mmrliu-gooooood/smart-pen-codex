from pathlib import Path
import os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/mcu-independent0124'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/mcu_power_ground_clearance_0109';B=R/'hardware/gnd_conservative_recovery_2305';O=R/'hardware/j202_low_speed_reference_candidate';BAD=R/'hardware/mcu_power_ground_candidate_0043'
L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];uid=lambda x:x.m_Uuid.AsString()
def need(c,m):
 if not c:raise RuntimeError(m)
def disk(x,r):
 q=p.SHAPE_POLY_SET();q.NewOutline();v=x.GetPosition()
 for k in range(512):q.Append(round(v.x+r*math.cos(k*math.tau/512)),round(v.y+r*math.sin(k*math.tau/512)))
 return q
def poly(x,l):
 q=p.SHAPE_POLY_SET();x.TransformShapeToPolygon(q,l,0,100,p.ERROR_INSIDE)
 if isinstance(x,p.PCB_VIA):q.BooleanSubtract(disk(x,x.GetDrillValue()/2))
 return q
def graph(b,net):
 nodes=[]
 for f in b.GetFootprints():
  for pad in f.Pads():
   if pad.GetNetname()==net:nodes.append((uid(pad),f.GetReference()+'.'+pad.GetNumber(),{l:poly(pad,l)for l in L if pad.IsOnLayer(l)}))
 for t in b.GetTracks():
  if t.GetNetname()==net:nodes.append((uid(t),None,{l:poly(t,l)for l in L if t.IsOnLayer(l)}))
 for z in b.Zones():
  if z.GetIsRuleArea()or z.GetNetname()!=net:continue
  for l in L:
   if z.IsOnLayer(l):
    q=z.GetFilledPolysList(l)
    for k in range(q.OutlineCount()):nodes.append((uid(z)+':'+str(l)+':'+str(k),None,{l:q.UnitSet(k)}))
 adj={n[0]:set()for n in nodes}
 for i,(u,_,a)in enumerate(nodes):
  for v,_,b in nodes[:i]:
   for l in set(a)&set(b):
    if not a[l].BBox().Intersects(b[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(a[l],b[l])
    if q.Area()>10:adj[u].add(v);adj[v].add(u);break
 return nodes,adj
def reach(adj,start,omit=set()):
 seen={start};todo=[start]
 while todo:
  for q in adj[todo.pop()]-seen-omit:seen.add(q);todo.append(q)
 return seen
b=p.LoadBoard(str(S/'native/mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));old=p.LoadBoard(str(O/'native/mainboard_revD.kicad_pcb'))
m=json.loads((BAD/'materialization.json').read_text());cm=json.loads((S/'materialization.json').read_text());groups=json.loads((R/'docs/electronics/aon_branch_reuse_plan_2318/evaluation.json').read_text())['geometrically_screened_groups']
results={};graphs={}
for net,core,want in [('3V3_AON','J106.2',14),('GND','J106.3',39)]:
 ns,adj=graph(b,net);graphs[net]=(ns,adj);root=next(u for u,n,_ in ns if n==core);rr=reach(adj,root);pads=[{'uuid':u,'name':n}for u,n,_ in ns if n and u in rr];need(len(pads)==want,'physical core count');results[net]={'connected':pads,'total':sum(n is not None for _,n,_ in ns)}
 if net=='3V3_AON':
  negatives=[]
  for g in groups:
   nr=reach(adj,root,set(g['objects']));names={n for u,n,_ in ns if n and u in nr};need(not names&set(g['pads']),'AON group deletion');negatives.append(g['id'])
  results['eight_AON_deletion_negatives']=negatives
 else:
  eps={u for u,n,_ in ns if n=='U101.57'};need(len(eps)==9 and eps<=rr,'nine EP');need(not eps&reach(adj,root,set(m['EP_GND_added'])),'EP deletion');need(not any(x['name']=='C504.2'for x in pads),'C504 unintended ground');results['EP_all_nine_deletion']=True
sig=lambda t:(t.GetClass(),t.GetNetname(),t.GetLayerSet().FmtHex(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
t={uid(x):x for x in b.GetTracks()};bt={uid(x):x for x in base.GetTracks()};ot={uid(x):x for x in old.GetTracks()};added=set(m['AON_added']+m['EP_GND_added']+[cm['added_track_uuid']]);need(len(t)==681 and len(bt)==630 and set(t)-set(bt)==added,'object sets');need(all(sig(t[u])==sig(bt[u])for u in bt),'old copper change')
for u in m['AON_added']+m['EP_GND_added']:
 a=list(sig(ot[u]));z=list(sig(t[u]))
 if u in m['widened_254um']:a[-2]=254000
 if u==cm['moved_via_uuid']:a[3:7]=[4250000,10750000,4250000,10750000]
 need(a==z,'source delta wrong '+u)
results['old_copper_unchanged']=630;results['exact_new_objects']=51;results['widened_tracks']=len(m['widened_254um'])
# All-layer actual same-net AND foreign pad screen; includes drill disk, not just hole-subtracted copper.
clear=[]
for label,path in [('rejected',BAD/'native/mainboard_revD.kicad_pcb'),('successor',S/'native/mainboard_revD.kicad_pcb')]:
 board=p.LoadBoard(str(path));non_ep=[];ep=[]
 for v in board.GetTracks():
  if uid(v)not in m['EP_GND_added']:continue
  for f in board.GetFootprints():
   for q in f.Pads():
    for l in L:
     if not q.IsOnLayer(l):continue
     sh=poly(q,l);ring=poly(v,l);hole=disk(v,v.GetDrillValue()/2);a=p.SHAPE_POLY_SET();a.BooleanIntersection(sh,ring);h=p.SHAPE_POLY_SET();h.BooleanIntersection(sh,hole)
     if a.Area()>10 or h.Area()>10:
      row={'via':uid(v),'pad':f.GetReference()+'.'+q.GetNumber(),'uuid':uid(q),'net':q.GetNetname(),'layer':board.GetLayerName(l),'ring_mm2':a.Area()/1e12,'drill_mm2':h.Area()/1e12}
      (ep if f.GetReference()=='U101'and q.GetNumber()=='57'and q.GetNetname()=='GND' else non_ep).append(row)
 if label=='rejected':need(any(x['pad']=='C504.2'and x['drill_mm2']>0 for x in non_ep),'negative lost')
 else:need(not non_ep,'same/foreign pad hole collision')
 clear.append({'case':label,'non_EP_overlaps':non_ep,'intended_EP_overlaps':ep})
results['all_layer_pad_clearance']=clear
for f in ['mainboard_revD.kicad_pro','mainboard_revD.kicad_dru','mainboard_revD.kicad_sch']:need((S/'native'/f).read_bytes()==(B/'native'/f).read_bytes(),'source/rules')
print(json.dumps(results,indent=2))
