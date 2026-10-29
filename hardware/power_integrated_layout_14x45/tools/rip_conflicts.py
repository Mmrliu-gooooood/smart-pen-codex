from pathlib import Path
import pcbnew as p,json
D=Path(__file__).resolve().parents[1];fn=D/'power_integrated_study.kicad_pcb';b=p.LoadBoard(str(fn));core=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));protected={t.m_Uuid.AsString() for t in core.GetTracks()};tracks={t.m_Uuid.AsString():t for t in b.GetTracks()};remove=set();log=[]
for violation in json.loads((D/'collisions.json').read_text())['violations']:
 if violation['type'] in ['via_dangling','track_dangling']:continue
 choices=[i['uuid'] for i in violation['items'] if i['uuid'] in tracks and i['uuid'] not in protected]
 assert choices,('must reposition instead of altering core copper',violation)
 remove.update(choices)
for uid in remove:
 t=tracks[uid];log.append({'uuid':uid,'net':t.GetNetname(),'class':t.GetClass(),'start_nm':[t.GetStart().x,t.GetStart().y],'end_nm':[t.GetEnd().x,t.GetEnd().y]});b.Delete(t)
p.SaveBoard(str(fn),b);(D/'ripped_only_new_copper.json').write_text(json.dumps(log,indent=2));print('Removed only',len(remove),'new items colliding with moved thermal IC; core untouched')
