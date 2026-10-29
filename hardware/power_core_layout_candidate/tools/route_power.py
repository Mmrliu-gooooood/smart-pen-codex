#!/usr/bin/python3
"""Explicit converter hot loops, power feeds, and ground returns. No automatic rule relaxation."""
from pathlib import Path
import pcbnew as p,shutil,json
D=Path(__file__).resolve().parents[1];fn=D/'power_core_NOFAB.kicad_pcb';shutil.copy2(fn,D/'placement_unrouted.kicad_pcb');b=p.LoadBoard(str(fn));mm=p.FromMM;v=lambda a:p.VECTOR2I(mm(a[0]),mm(a[1]));net={n.GetNetname().lstrip('/'):n for n in b.GetNetsByNetcode().values()};pads={(f.GetReference(),a.GetNumber()):a for f in b.GetFootprints() for a in f.Pads()};log=[]
def xy(ref,num):a=pads[ref,str(num)];return(p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y))
def route(n,pts,width=.3,layer=p.F_Cu):
 for a,z in zip(pts,pts[1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(net[n]);b.Add(t)
 log.append({'net':n,'points':pts,'width':width,'layer':b.GetLayerName(layer)})
def via(n,pt):
 a=p.PCB_VIA(b);a.SetPosition(v(pt));a.SetWidth(p.F_Cu,mm(.6));a.SetDrill(mm(.3));a.SetViaType(p.VIATYPE_THROUGH);a.SetLayerPair(p.F_Cu,p.B_Cu);a.SetNet(net[n]);b.Add(a)
def ground(r,num,pt):route('GND',[xy(r,num),pt],.3);via('GND',pt)
# TPS63802: L pins short to sole inductor; no FB route in the switching-node region.
route('SW_L1',[xy('U2',9),(5.5,21.7),(4.815,21.015),xy('L1',1)],.3)
route('SW_L2',[xy('U2',7),(6.5,21.7),(7.185,21.015),xy('L1',2)],.3)
route('SYS_RAW',[xy('U2',10),(4.65,22.25),(4.3,22.6),xy('C4',1)],.3)
route('SYS_RAW',[xy('U2',10),xy('U2',1)],.15) # distinct quiet EN feed, not a power stage return
route('3V3_AON',[xy('U2',6),(7.35,22.25),(7.7,22.6),xy('C5',1)],.3)
route('GND',[xy('U2',8),xy('U2',3),xy('U2',2)],.3);via('GND',(6,23.3))
route('GND',[xy('R8',2),(5.5,25.175),xy('U2',2)],.2)
route('REG_FB',[xy('U2',4),(6.5,24.6),xy('R7',2)],.15)
route('REG_FB',[(6.5,24.6),(6.5,26.825),xy('R8',1)],.15)
route('3V3_AON',[xy('C5',1),(8.5,23.15),(8.5,25),xy('C6',1)],.5)
route('3V3_AON',[xy('C6',1),(8.5,25.55),(8.5,26.825),xy('R7',1)],.3)
route('3V3_AON',[(8.5,25.55),(8.5,27.8),(6.15,27.8),xy('J3',1)],.6)
# Input/output ground nodes get dedicated vias; AGND joins at IC GND, not switch traces.
for r,num,pt in [('C4',2,(1.05,23.8)),('C5',2,(10.95,23.8)),('C6',2,(10.95,26.2)),('J3',2,(7.25,31))]:ground(r,num,pt)
# Charger short capacitor paths and protected battery feed.
route('VBUS_5V',[xy('J2',1),(7.25,4.3),xy('C1',1)],.5)
route('VBUS_5V',[xy('C1',1),(7.75,5.6),xy('U1',13)],.3)
route('PACK_PLUS_PROTECTED',[xy('U1',2),xy('U1',3)],.3)
route('PACK_PLUS_PROTECTED',[xy('U1',2),(4.1,8),xy('C2',1)],.3)
route('SYS_RAW',[xy('U1',10),xy('U1',11)],.3)
route('SYS_RAW',[xy('U1',10),(7.9,8),xy('C3',1)],.3)
for pt in [(5.6,7.6),(6.4,7.6),(5.6,8.4),(6.4,8.4)]:via('GND',pt)
route('GND',[xy('U1',8),(6.75,8.75),(6.4,8.4)],.3)
for r,num,pt in [('C1',2,(10.5,5.8)),('C2',2,(1.05,9.3)),('C3',2,(10.95,9.3)),('J2',2,(10.9,3)),('J4',2,(4.25,15.7)),('J1',2,(11,15.7)),('J5',4,(10.9,31.5)),('R1',2,(3.1,6)),('R3',2,(5.5,5.7)),('R2',2,(10.825,12.2)),('R4',2,(7.125,12.2)),('R5',2,(4.025,12.2))]:ground(r,num,pt)
route('PACK_PLUS_PROTECTED',[xy('C2',1),(3.3,8.35),(3.3,10)],.5)
for pt in [(3.3,9.2),(3.3,10),(2,12.3),(1.2,12.3)]:via('PACK_PLUS_PROTECTED',pt)
route('PACK_PLUS_PROTECTED',[(3.3,9.2),(3.3,10),(2,11.3),(2,12.3),(1.2,12.3)],.6,p.B_Cu)
route('PACK_PLUS_PROTECTED',[(2,12.3),xy('J4',1)],.6)
route('PACK_PLUS_PROTECTED',[(1.2,12.3),(1.2,13),xy('J4',1)],.4)
route('SYS_RAW',[xy('C3',1),(9.05,9.2),(9.85,9.2)],.5)
for pt in [(9.05,9.2),(9.85,9.2),(3,24),(3.8,24)]:via('SYS_RAW',pt)
route('SYS_RAW',[xy('C4',1),(3,22.65),(3,24),(3.8,24)],.5)
# Explicit slow control routes. No connection bridges the OPEN commissioning jumper.
route('CHG_TMR',[xy('U1',14),(6.25,5.8)],.15);via('CHG_TMR',(6.25,5.8));via('CHG_TMR',(4.375,3.6))
route('CHG_TMR',[(6.25,5.8),(6.25,3.6),(4.375,3.6)],.15,p.B_Cu);route('CHG_TMR',[(4.375,3.6),xy('R3',1)],.15)
route('CHG_ISET',[xy('U1',16),(4.3,6.2)],.15);via('CHG_ISET',(4.3,6.2));via('CHG_ISET',(1.375,6.8))
route('CHG_ISET',[(4.3,6.2),(4.3,6.55),(1.375,6.55),(1.375,6.8)],.15,p.B_Cu);route('CHG_ISET',[(1.375,6.8),xy('R1',1)],.15)
via('VBUS_5V',(7.25,3));via('VBUS_5V',(1.375,2.2));route('VBUS_5V',[(7.25,3),(7.25,1.0),(1.375,1.0),(1.375,2.2)],.2,p.B_Cu);route('VBUS_5V',[(1.375,2.2),xy('R6',1)],.2)
via('CHARGE_DISABLE',(3.025,2.2));route('CHARGE_DISABLE',[xy('R6',2),(3.025,2.2)],.15)
via('CHARGE_DISABLE',(4.3,10));route('CHARGE_DISABLE',[(3.025,2.2),(2.3,2.9),(2.3,10.8),(4.3,10.8),(4.3,10)],.15,p.In2_Cu)
route('CHARGE_DISABLE',[xy('U1',4),(4.6,9.2),(4.3,9.5),(4.3,10)],.15)
via('CHARGE_DISABLE',(11.2,19.2));route('CHARGE_DISABLE',[xy('JP1',1),(11.2,19.2)],.15)
route('CHARGE_DISABLE',[(4.3,10),(4.3,9.3),(6.5,9.3),(6.5,17.5),(11.2,19.2)],.15,p.B_Cu)
via('CE_PERMISSION_EXTERNAL',(9.1,17.05));route('CE_PERMISSION_EXTERNAL',[xy('JP1',2),(9.1,17.05)],.15)
via('CE_PERMISSION_EXTERNAL',(6.3,31.5));route('CE_PERMISSION_EXTERNAL',[(9.1,17.05),(9.1,20.4),(9.5,20.8),(9.5,30),(6.3,30),(6.3,31.5)],.15,p.In2_Cu)
route('CE_PERMISSION_EXTERNAL',[(6.3,31.5),xy('J5',3)],.15)
via('CHG_ILIM',(8.6,6.2));via('CHG_ILIM',(8.6,10.2));route('CHG_ILIM',[xy('U1',12),(8.6,6.2)],.15)
route('CHG_ILIM',[(8.6,6.2),(8.1,6.7),(8.1,10.2),(8.6,10.2)],.15,p.B_Cu);route('CHG_ILIM',[(8.6,10.2),xy('R2',1)],.15)
via('PACK_NTC',(4.6,7));via('PACK_NTC',(8.3,12.2));route('PACK_NTC',[xy('U1',1),(4.6,7)],.15)
route('PACK_NTC',[(4.6,7),(4.9,7.3),(4.9,8.9),(5.8,9.8),(5.8,11),(8.3,11),(8.3,12.2)],.15,p.In2_Cu);route('PACK_NTC',[(8.3,12.2),xy('J1',1)],.15)
route('USB_EN1',[xy('U1',6),(5.75,10.925),xy('R4',1)],.15);via('USB_EN1',(5.7,12.2));route('USB_EN1',[xy('R4',1),(5.7,12.2)],.15)
via('USB_EN1',(2.25,31.5));route('USB_EN1',[(5.7,12.2),(5.7,16),(4.5,17.2),(4.5,28),(2.25,30.25),(2.25,31.5)],.15,p.B_Cu);route('USB_EN1',[(2.25,31.5),xy('J5',1)],.15)
via('USB_EN2',(5.1,10.1));route('USB_EN2',[xy('U1',5),(5.1,10.1)],.15);via('USB_EN2',(4.8,12.1));route('USB_EN2',[(5.1,10.1),(4.8,10.7),(4.8,12.1)],.15,p.B_Cu)
via('USB_EN2',(1.2,10.5));route('USB_EN2',[(4.8,12.1),(4.8,11.5),(1.2,11.5),(1.2,10.5)],.15,p.In2_Cu);route('USB_EN2',[(1.2,10.5),xy('R5',1)],.15)
via('USB_EN2',(4.75,31.5));route('USB_EN2',[(1.2,10.5),(.6,10.5),(.6,14),(1.8,15.2),(1.8,30),(4.75,31.5)],.15,p.In2_Cu);route('USB_EN2',[(4.75,31.5),xy('J5',2)],.15)
# Ground plane continuous on In1; B layer ground supplementary. SYS rail uses a separate In2 polygon.
def zone(n,layer,pts):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(net[n]);z.SetLocalClearance(mm(.15));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.15));z.SetThermalReliefGap(mm(.25));z.SetThermalReliefSpokeWidth(mm(.3));o=z.Outline();o.NewOutline()
 for a in pts:o.Append(int(mm(a[0])),int(mm(a[1])))
 b.Add(z)
for l in [p.In1_Cu,p.B_Cu]:zone('GND',l,[(.5,.5),(11.5,.5),(11.5,34.5),(.5,34.5)])
zone('SYS_RAW',p.In2_Cu,[(8,7),(11.5,7),(11.5,18.2),(4.1,18.2),(4.1,24.5),(2.5,24.5),(2.5,17),(8,17)])
p.SaveBoard(str(fn),b);b=p.LoadBoard(str(fn));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
(D/'power_routes.json').write_text(json.dumps(log,indent=2));print('Routed',len(log),'explicit paths; filled planes; fresh DRC still required')
