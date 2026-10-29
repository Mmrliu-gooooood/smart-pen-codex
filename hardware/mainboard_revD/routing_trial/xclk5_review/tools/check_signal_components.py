from pathlib import Path
import pcbnew as p,json,re,sys
D=Path(__file__).resolve().parents[1];name=sys.argv[1];b=p.LoadBoard(str(D/(name+'.kicad_pcb')));b.BuildConnectivity();c=b.GetConnectivity();groups={};pad_labels={}
for f in b.GetFootprints():
 for a in f.Pads():
  pad_labels[a.m_Uuid.AsString()]=f.GetReference()+'.'+a.GetNumber();groups.setdefault(a.GetNetname(),[]).append(a)
rows=[]
for net,pads in groups.items():
 if net in ['GND','3V3_AON','SENS_VIO_1V8'] or len(pads)<2:continue
 unseen={a.m_Uuid.AsString():a for a in pads};parts=[]
 while unseen:
  a=next(iter(unseen.values()));q=[a];seen=set();labels=[]
  while q:
   o=q.pop();uid=o.m_Uuid.AsString()
   if uid in seen:continue
   seen.add(uid)
   if uid in unseen:labels.append(pad_labels[uid]);del unseen[uid]
   q.extend(c.GetConnectedTracks(o));q.extend(c.GetConnectedPads(o))
  parts.append(sorted(labels))
 rows.append({'net':net,'physical_components':parts,'missing_connections':len(parts)-1})
report=(D/'drc.rpt').read_text();native={re.search(r'\[([^]]+)\]',next(l for l in block.splitlines() if l.strip().startswith('@')))[1] for block in report.split('[unconnected_items]:')[1:]};observed={r['net'] for r in rows if r['missing_connections']};unexpected=sorted(observed-native);missed=sorted(native-observed);r={'board':name,'method':'Actual pcbnew physical track/via/pad graph, no routing-success log. Power/ground uses separate filled-zone endpoint checks. Includesallpresentpassive/DNPpadswithoutassumingopenjumpersshorted.','native_unconnected_nets':sorted(native),'graph_unconnected_nets':sorted(observed),'unexpected_graph_failures':unexpected,'native_missing_not_seen_by_graph':missed,'per_signal_net':rows};(D/(name+'_signal_components.json')).write_text(json.dumps(r,indent=2));print(len(rows),'multi-pad signal nets; disconnected',sorted(observed));assert not unexpected and not missed
