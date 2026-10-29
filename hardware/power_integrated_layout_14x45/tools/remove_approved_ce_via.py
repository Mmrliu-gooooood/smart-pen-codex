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
before=partitions()
via=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='CE_PERMISSION_INTERNAL' and abs(p.ToMM(t.GetPosition().x)-9.1)<1e-6 and abs(p.ToMM(t.GetPosition().y)-17.05)<1e-6]
assert len(via)==1
t=via[0];assert t.m_Uuid.AsString() in protected
record={'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'start':[9.1,17.05],'end':[9.1,17.05],'type':'PCB_VIA','reason':'Parent approved removal of unused former external CE escape via; functional pad partitions unchanged'}
b.Delete(t);after=partitions();assert before==after
p.SaveBoard(str(fn),b);b=p.LoadBoard(str(fn));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
c=json.loads((D/'placement_contract.json').read_text());assert len(c['removed_only_exposed_CE_branch'])==7
c['removed_only_exposed_CE_branch'].append(record);c['outline_mm']=[14,45,.8];c['back_placements']={f.GetReference():[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()] for f in b.GetFootprints() if f.GetLayer()==p.B_Cu};c['stage']='14x45 independent routed comparison, NOFAB; unchanged source circuit; physical validation pending'
(D/'placement_contract.json').write_text(json.dumps(c,indent=2))
(D/'approved_extra_core_delta.json').write_text(json.dumps({'removed':record,'core_retained_items':182,'obsolete_CE_items_removed_total':8,'non_GND_pad_partitions_before':before,'non_GND_pad_partitions_after':after,'partitions_equal':True},indent=2))
print('Removed approved original CE via; pad partitions unchanged; 182 core items retained')
