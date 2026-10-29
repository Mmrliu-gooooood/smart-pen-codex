from pathlib import Path
import pcbnew as p,json,math
D=Path(__file__).resolve().parents[1];fn=D/'power_integrated_study.kicad_pcb';b=p.LoadBoard(str(fn));core=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));protected={t.m_Uuid.AsString() for t in core.GetTracks()};log=[]
padlabels={a.m_Uuid.AsString():f.GetReference()+'.'+a.GetNumber() for f in b.GetFootprints() for a in f.Pads()}
def component(seed):
 con=b.GetConnectivity();q=[seed];seen={};pads=[]
 while q:
  a=q.pop();uid=a.m_Uuid.AsString()
  if uid in seen:continue
  seen[uid]=a
  if isinstance(a,p.PAD):pads.append(padlabels[a.m_Uuid.AsString()])
  q.extend(con.GetConnectedTracks(a));q.extend(con.GetConnectedPads(a))
 return seen,pads

def partitions():
 b.BuildConnectivity();out={};seen=set()
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetNetname()=='GND' or a.m_Uuid.AsString() in seen:continue
   items,pads=component(a);seen.update(items);out.setdefault(a.GetNetname(),[]).append(sorted(pads))
 return {n:sorted(v) for n,v in out.items()}
def remove(t,reason):
 uid=t.m_Uuid.AsString();assert uid not in protected
 log.append({'uuid':uid,'net':t.GetNetname(),'class':t.GetClass(),'start_nm':[t.GetStart().x,t.GetStart().y],'end_nm':[t.GetEnd().x,t.GetEnd().y],'reason':reason});b.Delete(t)
before=partitions();seen=set()
for t in list(b.GetTracks()):
 if t.GetNetname()=='GND' or t.m_Uuid.AsString() in seen:continue
 items,pads=component(t);seen.update(items)
 if not pads:
  assert not (set(items)&protected),'Never discard original core copper'
  for q in items.values():remove(q,'Native physical component contains zero component pads')
b.BuildConnectivity();byid={t.m_Uuid.AsString():t for t in b.GetTracks()}
for v in json.loads((D/'before_cleanup_drc.json').read_text())['violations']:
 if v['type'] not in ['via_dangling','track_dangling']:continue
 for item in v['items']:
  uid=item['uuid']
  if uid in byid and uid not in protected:remove(byid[uid],'Native DRC confirms unused via layer or trace endpoint; pad partitions checked unchanged')
def anchor(q,t):
 net=t.GetNetCode();layer=t.GetLayer()
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetNetCode()==net and a.IsOnLayer(layer) and a.HitTest(q):return True
 for a in b.GetTracks():
  if a.m_Uuid==t.m_Uuid or a.GetNetCode()!=net:continue
  if isinstance(a,p.PCB_VIA):
   if math.hypot(q.x-a.GetPosition().x,q.y-a.GetPosition().y)<=a.GetWidth(layer)/2:return True
  elif a.GetLayer()==layer and a.HitTest(q):return True
 for z in b.Zones():
  if z.GetLayer()==layer and z.GetNetCode()==net and z.GetFilledPolysList(layer).Contains(q):return True
 return False
for repeat in range(1000):
 dead=next((t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() not in protected and (not anchor(t.GetStart(),t) or not anchor(t.GetEnd(),t))),None)
 if dead is None:break
 remove(dead,'New trace leaf endpoint has no same-net pad/track/via/filled-zone anchor')
after=partitions();assert before==after,'Cleanup changed actual native non-GND pad connectivity'
p.SaveBoard(str(fn),b);b=p.LoadBoard(str(fn));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
(D/'cleanup_proof.json').write_text(json.dumps({'removed_new_items':log,'non_GND_pad_partitions_before':before,'non_GND_pad_partitions_after':after,'partitions_equal':before==after,'protected_original_core_items_untouched':True,'GND_final_full_polygon_graph_is_separate_required_check':True},indent=2));print('Cleaned',len(log),'new-only unused items; all non-GND physical pad partitions unchanged')
