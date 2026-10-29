from pathlib import Path
import pcbnew as p,json
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'power_integrated_study.kicad_pcb'));core=p.LoadBoard(str(D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pcb'));ids={t.m_Uuid.AsString() for t in core.GetTracks()};removed=[]
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA) or t.GetLayer()!=p.B_Cu or t.GetNetname()!='/thermal/THERM_OK':continue
 a,z=t.GetStart(),t.GetEnd();xs=[p.ToMM(a.x),p.ToMM(z.x)];ys=[p.ToMM(a.y),p.ToMM(z.y)]
 if max(xs)>=11.1 and min(xs)<=12.6 and max(ys)>=15.8 and min(ys)<=18.6:
  assert t.m_Uuid.AsString() not in ids;removed.append(t.m_Uuid.AsString());b.Delete(t)
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
t=p.PCB_TRACK(b);t.SetStart(pt(11.7,17.1));t.SetEnd(pt(11.7,18.2));t.SetWidth(p.FromMM(.15));t.SetLayer(p.B_Cu);t.SetNet(b.FindNet('GND'));b.Add(t)
v=p.PCB_VIA(b);v.SetPosition(pt(11.7,18.2));v.SetWidth(p.F_Cu,p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('GND'));b.Add(v)
p.SaveBoard(str(D/'power_integrated_study.kicad_pcb'),b);b=p.LoadBoard(str(D/'power_integrated_study.kicad_pcb'));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'power_integrated_study.kicad_pcb'),b);(D/'ground_escape_u104_delta.json').write_text(json.dumps({'only_new_THERM_OK_segments_removed':removed,'ground_escape_mm':[[11.7,17.1],[11.7,18.2]],'via_mm':[11.7,18.2],'native_DRC_required':True},indent=2))
