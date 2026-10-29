#!/usr/bin/python3
from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json
D=Path(__file__).resolve().parents[1];x=E.parse(D/'usb_tail_revA.xml');b=p.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(p.FromMM(.8));nets={};mapping={}
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for n in x.findall('./nets/net'):
 name=n.attrib['name'];ni=p.NETINFO_ITEM(b,name);b.Add(ni);nets[name]=ni
 for q in n:mapping[q.attrib['ref'],q.attrib['pin']]=name
pos={'J101':(6,3.675,180),'U102':(6,10.5,90),'D101':(3,10,90),'R110':(8.75,14.8,0),'R111':(8.75,12.2,0),'TP101':(4.5,18,0),'TP102':(6.5,18,0),'TP103':(2,18,0),'TP104':(10,18,0)};fps={}
root=__import__('re').search(r'\(uuid ([0-9a-f-]+)\)',(D/'usb_tail_revA.kicad_sch').read_text())[1]
for c in x.findall('./components/comp'):
 ref=c.attrib['ref'];fpname=c.findtext('footprint');lib,name=fpname.split(':');path=D/'SmartPen.pretty' if lib=='SmartPen' else Path('/usr/share/kicad/footprints')/(lib+'.pretty');f=p.FootprintLoad(str(path),name);assert f
 f.SetReference(ref);f.SetValue(c.findtext('value'));f.SetPosition(pt(*pos[ref][:2]));f.SetOrientationDegrees(pos[ref][2]);f.SetFPID(p.LIB_ID(lib,name));f.SetPath(p.KIID_PATH('/'+root+c.find('sheetpath').attrib['tstamps']+c.findtext('tstamps')));b.Add(f);fps[ref]=f
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 for a in f.Pads():
  if a.GetNumber():a.SetNet(nets[mapping[ref,a.GetNumber()]])
for a,z in [((0,0),(12,0)),((12,0),(12,20)),((12,20),(0,20)),((0,20),(0,0))]:
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*z));s.SetWidth(p.FromMM(.05));s.SetLayer(p.Edge_Cuts);b.Add(s)
def loc(r,pin):a=next(a for a in fps[r].Pads() if a.GetNumber()==str(pin));v=a.GetPosition();return(p.ToMM(v.x),p.ToMM(v.y))
def trace(n,points,layer=p.F_Cu,w=.15):
 for a,z in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(*a));t.SetEnd(pt(*z));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t)
def via(n,x,y,d=.45,h=.2):
 v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(p.F_Cu,p.FromMM(d));v.SetDrill(p.FromMM(h));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[n]);b.Add(v)
# Type-C USB2 duplicate D+/D- tails joined before the ESD device.
trace('USB_DP',[loc('J101','B6'),(5.25,9),(6.25,9),loc('J101','A6')])
trace('USB_DP',[(5.25,9),(4.75,9.5),(4.75,9.865),loc('U102',10)])
for pin,xx in [('A7',5.75),('B7',6.75)]:trace('USB_DM',[loc('J101',pin),(xx,8.3)]);via('USB_DM',xx,8.3)
trace('USB_DM',[(5.75,8.3),(6.75,8.3)],p.In2_Cu);trace('USB_DM',[(5.75,8.3),(5.5,8.55),(5.5,9.6)],p.In2_Cu);via('USB_DM',5.5,9.6);trace('USB_DM',[(5.5,9.6),loc('U102',9)])
# CC passive Rd; no advertisement measurement or PD controller.
trace('USB_CC1',[loc('J101','A5'),(7.25,8.2),(7.5,8.45),(7.5,8.6)]);via('USB_CC1',7.5,8.6);trace('USB_CC1',[(7.5,8.6),(6.5,9.45)],p.B_Cu);via('USB_CC1',6.5,9.45);trace('USB_CC1',[(6.5,9.45),loc('U102',7)])
trace('USB_CC2',[loc('J101','B5'),(4.25,8.3)]);via('USB_CC2',4.25,8.3);trace('USB_CC2',[(4.25,8.3),(4.25,12.3),(7.9,12.3),(7.9,10),(7.4,9.5)],p.B_Cu);via('USB_CC2',7.4,9.5);trace('USB_CC2',[(7.4,9.5),(7.4,9.715),loc('U102',6)])
# Actual copper directly joins optional NC routing pads to respective diode pads.
for net,a,z in [('USB_DP',10,1),('USB_DM',9,2),('USB_CC1',7,4),('USB_CC2',6,5),('GND',8,3)]:trace(net,[loc('U102',a),loc('U102',z)])
trace('USB_DP',[loc('U102',1),(4.9,10.985),(4.9,16.5),(4.5,16.9),loc('TP101',1)])
trace('USB_DM',[loc('U102',2),(5.4,10.985),(5.4,16.5),(6.5,17.6),loc('TP102',1)])
trace('USB_CC1',[loc('U102',4),(6.5,11.45),(6.65,11.6),(6.65,13.525),loc('R110',1)])
trace('USB_CC2',[loc('U102',5),(7,11.275),loc('R111',1)])
# Ground returns to continuous In1 and B zones; solder wire ground is a real external interface.
for r,pin,xx,yy in [('U102',3,6,11.7),('D101',2,2,9.26),('R110',2,10.5,14.8),('R111',2,10.5,12.2),('TP104',1,10,16.5),('J101','A1',9.2,8.5),('J101','A12',2.8,8.5)]:trace('GND',[loc(r,pin),(xx,yy)],w=.25);via('GND',xx,yy,.6,.3)
# Both USB VBUS groups feed a real TVS and output land, not a hidden supply flag.
for pin,xx in [('A4',8.4),('A9',3.6)]:trace('VBUS_5V',[loc('J101',pin),(xx,8.5)],w=.3);via('VBUS_5V',xx,8.5,.6,.3)
trace('VBUS_5V',[(3.6,8.5),(3.6,7),(4,6.6),(4,5),(8,5),(8,6.6),(8.4,7),(8.4,8.5)],p.In2_Cu,.3)
trace('VBUS_5V',[(3.6,8.5),(4,8.9),(4,10.74),loc('D101',1)],w=.3)
trace('VBUS_5V',[loc('D101',1),(2,11.74),loc('TP103',1)],w=.35)
for label,xx in [('5V',2),('DP',4.5),('DM',6.5),('G',10)]:
 t=p.PCB_TEXT(b);t.SetText(label);t.SetPosition(pt(xx,16.2));t.SetTextSize(pt(.8,.8));t.SetTextThickness(p.FromMM(.12));t.SetLayer(p.F_SilkS);b.Add(t)
for layer in [p.In1_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets['GND']);z.SetLocalClearance(p.FromMM(.15));z.SetMinThickness(p.FromMM(.15));z.SetPadConnection(p.ZONE_CONNECTION_FULL);o=z.Outline();o.NewOutline()
 for a,y in [(.3,.3),(11.7,.3),(11.7,19.7),(.3,19.7)]:o.Append(p.FromMM(a),p.FromMM(y))
 b.Add(z)
file=D/'usb_tail_revA.kicad_pcb';p.SaveBoard(str(file),b);b=p.LoadBoard(str(file));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(file),b)
pro=D/'usb_tail_revA.kicad_pro';j=json.loads(pro.read_text());j['net_settings']['classes'][0]['clearance']=.15;j['board']['design_settings']['rules']['min_via_diameter']=.45;j['board']['design_settings']['rules']['min_through_hole_diameter']=.2;j['board']['design_settings']['rules']['min_via_annular_width']=.125;j['board']['design_settings']['drc_exclusions']=[];pro.write_text(json.dumps(j,indent=2));print('Native PCB9footprints. Run DRC/real-pad check; no impedance release.')
