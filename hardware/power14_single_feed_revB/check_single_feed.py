from pathlib import Path
import pcbnew as k,json,hashlib,math
D=Path(__file__).resolve().parent;S=D.parent/'power_integrated_layout_14x45';src=S/'power_integrated_study.kicad_pcb';pcb=D/'power_integrated_study.kicad_pcb'
b=k.LoadBoard(str(pcb));old=k.LoadBoard(str(src));delta=json.loads((D/'REVB_EXPECTED_DELTA.json').read_text())
def req(x,msg):
 if not x:raise RuntimeError(msg)
def geo(t):return [t.GetClass(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(k.F_Cu) if isinstance(t,k.PCB_VIA) else t.GetWidth(),t.GetLayer(),t.GetDrillValue() if isinstance(t,k.PCB_VIA) else None,t.GetNetname()]
a={t.m_Uuid.AsString():geo(t) for t in old.GetTracks()};n={t.m_Uuid.AsString():geo(t) for t in b.GetTracks()};removed=set(a)-set(n);added=set(n)-set(a)
req({u:a[u] for u in removed}==delta['removed'],'Exact removed geometry whitelist')
req({u:n[u] for u in added}==delta['added'],'Exact new geometry whitelist')
req(not delta['changed_common'],'No altered existing geometry')
req(all(n[u]==v for u,v in a.items() if u not in removed),'All nonwhitelisted tracks/vias unchanged')
core=k.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'))
core_ids={t.m_Uuid.AsString() for t in core.GetTracks()};req(not removed&core_ids,'No original core track or via removed')
physical=json.loads((D/'physical_contacts.json').read_text());req(physical['pcb_sha256']==hashlib.sha256(pcb.read_bytes()).hexdigest(),'Fresh physical contact evidence')
req(physical['all_core_added_contacts_confined_to_C1_pad'] and all(x['connected'] for x in physical['nets']),'Actual finite-width single-C1 contact isolation')
def fp(b):
 return {f.GetReference():[f.GetValue(),f.IsDNP(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer(),sorted((p.GetNumber(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y,p.GetNetname(),p.GetLayerSet().FmtBin()) for p in f.Pads())] for f in b.GetFootprints()}
req(fp(b)==fp(old),'All footprints/pads/value/net/DNP unchanged')
req(next(f for f in b.GetFootprints() if f.GetReference()=='JP1').IsDNP(),'JP1 OPEN DNP')
for name in ['power_integrated_study.kicad_sch','core.kicad_sch','thermal.kicad_sch','power_integrated_study.kicad_pro','fp-lib-table','sym-lib-table']:
 req((D/name).read_bytes()==(S/name).read_bytes(),'Source/rules immutable '+name)
c=json.loads((D/'copper_graph.json').read_text());req(c['status']=='PASS' and len(c['actual_copper_graph'])==25 and all(x['connected'] for x in c['actual_copper_graph']),'25nets actual copper')
r=json.loads((D/'network_result.json').read_text());req(r['pcb_sha256']==hashlib.sha256(pcb.read_bytes()).hexdigest(),'Fresh resistor evidence');req(r['scenarios'][0]['max_added_current_A']<1e-10,'BQ current excluded from added thermal tracks')
for f,h in json.loads((S/'manifest.json').read_text())['files'].items():req(hashlib.sha256((S/f).read_bytes()).hexdigest()==h,'Frozen file changed '+f)
result={'status':'PASS candidate delta/source/DC branch checks; NOFAB','pcb_sha256':hashlib.sha256(pcb.read_bytes()).hexdigest(),'removed_track_via':sorted(removed),'added_tracks':{u:n[u] for u in sorted(added)},'unchanged_track_via_count':len(a)-len(removed),'footprints_unchanged':len(fp(b)),'frozen104hashes_unchanged':True,'remaining':'Finite-width topology verified, but DC model excludes finite-element pad spreading/return/dynamic/assembly qualification; downstream .15mm routes not all widened; branch not globally tree-routed.'}
(D/'single_feed_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
