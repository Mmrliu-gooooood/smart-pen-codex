from pathlib import Path
import pcbnew as p,json
D=Path(__file__).resolve().parents[1];fn=D/'power_integrated_study.kicad_pcb';b=p.LoadBoard(str(fn));core=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));keep={t.m_Uuid.AsString() for t in core.GetTracks()};removed=[]
for t in list(b.GetTracks()):
 if t.GetNetname()!='/thermal/THERM_OK' or t.GetLayer()!=p.B_Cu or isinstance(t,p.PCB_VIA):continue
 a=t.GetStart();z=t.GetEnd();x1=min(a.x,z.x)/1e6;x2=max(a.x,z.x)/1e6;y1=min(a.y,z.y)/1e6;y2=max(a.y,z.y)/1e6
 if x1<12.6 and x2>10.5 and y1<22.1 and y2>16.3:
  assert t.m_Uuid.AsString() not in keep;removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'start_mm':[a.x/1e6,a.y/1e6],'end_mm':[z.x/1e6,z.y/1e6]});b.Delete(t)
p.SaveBoard(str(fn),b);b=p.LoadBoard(str(fn));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b);(D/'ground_corridor_delta.json').write_text(json.dumps({'reason':'Reroute new THERM_OK bus away from local decoupling/GND-return pocket, not hide disconnected GND','removed_only_new_segments':removed},indent=2));print('Removed',len(removed),'new bus segments for genuine ground-return corridor')
