from pathlib import Path
import pcbnew as p,json,shutil
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));rows=[]
def pt(xy):return p.VECTOR2I(*(round(v*1e6)for v in xy))
def route(net,ps,w):
 for a,z in zip(ps,ps[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(a));t.SetEnd(pt(z));t.SetWidth(round(w*1e6));t.SetLayer(p.F_Cu);t.SetNet(b.FindNet(net));b.Add(t);rows.append({'uuid':t.m_Uuid.AsString(),'net':net,'type':'track','a':a,'z':z,'width':w})
def via(net,xy,diam=.6,hole=.3):
 v=p.PCB_VIA(b);v.SetPosition(pt(xy));v.SetWidth(round(diam*1e6));v.SetDrill(round(hole*1e6));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));b.Add(v);rows.append({'uuid':v.m_Uuid.AsString(),'net':net,'type':'via','xy':xy,'diameter':diam,'drill':hole})
route('3V3_AON',[(5.72,80.7),(5.17,81.25),(4.7625,81.25)],.2)
route('3V3_AON',[(5.72,82),(5.47,81.75),(4.7625,81.75)],.2)
route('3V3_AON',[(5.72,80.7),(5.72,82),(5.72,82.8)],.3);via('3V3_AON',(5.72,82.8))
route('GND',[(6.68,80.7),(6.68,81.35),(6.68,82)],.25)
route('GND',[(6.55,81.35),(6.68,81.35)],.25);via('GND',(6.55,81.35),.45,.2)
route('GND',[(4.7625,82.25),(5.1,82.25)],.15)
route('GND',[(5.1,82.25),(5.1,83.2),(5.5,83.6),(5.7,83.6)],.25);via('GND',(5.7,83.6))
route('GND',[(3.75,82.7625),(4.25,82.7625),(4.7625,82.75),(5.1,82.75)],.2)
route('GND',[(6.25,84.5),(5.7,83.95),(5.7,83.6)],.25)
route('3V3_AON',[(4.35,84.5),(4.35,85.6)],.3);via('3V3_AON',(4.35,85.6))
route('3V3_AON',[(3.2375,81.75),(2.7,81.75),(2.7,82.25),(3.2375,82.25)],.15)
route('3V3_AON',[(2.7,81.75),(2.3,82.15)],.2);via('3V3_AON',(2.3,82.15))
route('3V3_AON',[(1.775,86.5),(.875,86.5)],.2);via('3V3_AON',(.875,86.5))
route('3V3_AON',[(4.825,86.65),(4.35,86.175),(4.35,85.6)],.2)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'mainboard_revD.kicad_pcb'),b);(D/'new_local_routes.json').write_text(json.dumps(rows,indent=2))
