from pathlib import Path
import pcbnew as p
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'illumination_NOFAB.kicad_pcb'));mm=p.FromMM;v=lambda x,y:p.VECTOR2I(mm(x),mm(y))
def route(net,pts,width=.25):
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(width));t.SetLayer(p.F_Cu);t.SetNet(b.FindNet('/'+net));b.Add(t)
def via(x,y):
 a=p.PCB_VIA(b);a.SetPosition(v(x,y));a.SetWidth(p.F_Cu,mm(.6));a.SetDrill(mm(.3));a.SetViaType(p.VIATYPE_THROUGH);a.SetLayerPair(p.F_Cu,p.B_Cu);a.SetNet(b.FindNet('/GND'));b.Add(a)
route('3V3_AON',[(1.5,1.5),(1.5,3.55),(1.8,3.85)])
route('LED_COMMISSIONED',[(1.8,5.15),(.9,6.05),(.9,8.275),(1.8,9.175)])
route('LED_A',[(1.8,10.825),(1.8,12.55),(2.75,13.5)])
route('LED_K',[(5.9375,8),(6.7,8.7625),(6.7,12.05),(5.25,13.5)])
route('LED_GATE',[(4.675,4.5),(4.675,6.4375),(4.0625,7.05)],.2)
route('LED_GATE',[(3.375,11.2),(3.375,9.8),(2.8,9.425),(2.8,7.7),(3.45,7.05),(4.0625,7.05)],.2)
route('ILLUM_STROBE',[(6.5,1.5),(6.5,4.325),(6.325,4.5)],.2)
route('GND',[(4.0625,8.95),(4.0625,9.4),(5.025,10.3625),(5.025,11.2)])
route('GND',[(4,1.5),(4,3)])
via(5.025,10.3625);via(4,3)
z=p.ZONE(b);z.SetLayer(p.B_Cu);z.SetNet(b.FindNet('/GND'));z.SetLocalClearance(mm(.15));z.SetThermalReliefGap(mm(.2));z.SetThermalReliefSpokeWidth(mm(.25));z.SetPadConnection(p.ZONE_CONNECTION_FULL);o=z.Outline();o.NewOutline()
for x,y in [(.5,.5),(7.5,.5),(7.5,14.5),(.5,14.5)]:o.Append(int(mm(x)),int(mm(y)))
b.Add(z);p.SaveBoard(str(D/'illumination_NOFAB.kicad_pcb'),b);b=p.LoadBoard(str(D/'illumination_NOFAB.kicad_pcb'));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'illumination_NOFAB.kicad_pcb'),b)
