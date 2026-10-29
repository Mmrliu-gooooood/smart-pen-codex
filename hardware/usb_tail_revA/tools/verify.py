#!/usr/bin/python3
from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,hashlib,re,csv
D=Path(__file__).resolve().parents[1];x=E.parse(D/'usb_tail_revA.xml');b=p.LoadBoard(str(D/'usb_tail_revA.kicad_pcb'));parts={c.attrib['ref']:c for c in x.findall('./components/comp')};nodes={(q.attrib['ref'],q.attrib['pin']):n.attrib['name'] for n in x.findall('./nets/net') for q in n};checks=[]
def check(ok,msg):checks.append({'check':msg,'pass':bool(ok)});assert ok,msg
check(len(parts)==9,'nine real components');check(len(nodes)==37,'37 source pins including2SBU NC');check(parts['J101'].findtext('value')=='USB4105-GF-A-120','real GCT ordering code not A16P')
expected={('D101','1'):'VBUS_5V',('D101','2'):'GND',('R110','1'):'USB_CC1',('R110','2'):'GND',('R111','1'):'USB_CC2',('R111','2'):'GND'}
for n,net in {1:'USB_DP',2:'USB_DM',3:'GND',4:'USB_CC1',5:'USB_CC2',6:'USB_CC2',7:'USB_CC1',8:'GND',9:'USB_DM',10:'USB_DP'}.items():expected['U102',str(n)]=net
for k,v in expected.items():check(nodes[k]==v,'.'.join(k)+' exact TI-derived net')
for r in ['R110','R111']:check(parts[r].findtext('value')=='5.1k 1%',r+' Rd value')
fps={f.GetReference():f for f in b.GetFootprints()};check(set(fps)==set(parts),'all9 PCB footprints present');count=0
for ref,fp in fps.items():
 check(fp.GetValue()==parts[ref].findtext('value'),ref+' value parity');check(not fp.IsDNP(),ref+' populated interface/part')
 for a in fp.Pads():
  pin=a.GetNumber()
  if pin:check(a.GetNetname()==nodes[ref,pin],ref+'.'+pin+' actual PCB net');count+=1
check(count==40,'40 electrical copper pads including4same-net shield stakes')
sh=[a for a in fps['J101'].Pads() if a.GetNumber()=='S1'];check(len(sh)==4 and all(a.GetNetname()=='GND' for a in sh),'four GCT shell stakes sharedS1 GND')
# GCT B4 component-side recommended pattern, translated to KiCad library origin.
g=p.FootprintLoad('/usr/share/kicad/footprints/Connector_USB.pretty','USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
gpads=list(g.Pads());gx={'A1':-3.2,'B12':-3.2,'A4':-2.4,'B9':-2.4,'B8':-1.75,'A5':-1.25,'B7':-.75,'A6':-.25,'A7':.25,'B6':.75,'A8':1.25,'B5':1.75,'A9':2.4,'B4':2.4,'A12':3.2,'B1':3.2}
for a in gpads:
 n=a.GetNumber();xx=p.ToMM(a.GetPosition().x);yy=p.ToMM(a.GetPosition().y)
 if n in gx:
  check(abs(xx-gx[n])<1e-6 and abs(yy+3.68)<1e-6,'GCT '+n+' component-side position')
  check(abs(p.ToMM(a.GetSize().x)-(.6 if abs(gx[n])>=2.4 else .3))<1e-6 and abs(p.ToMM(a.GetSize().y)-1.15)<1e-6,'GCT '+n+' land size')
 elif n=='S1':
  check(abs(abs(xx)-4.32)<1e-6 and yy in [-3.105,1.075],'GCT S1 slot position')
  check(abs(p.ToMM(a.GetDrillSize().x)-.6)<1e-6 and abs(p.ToMM(a.GetDrillSize().y)-(1.7 if yy<0 else 1.4))<1e-6,'GCT S1 official slot drill')
 else:check(abs(abs(xx)-2.89)<1e-6 and abs(yy+2.605)<1e-6 and abs(p.ToMM(a.GetDrillSize().x)-.65)<1e-6,'GCT locator hole')
# Independently inspect unrotated manufacturer-derived land geometry.
f=p.FootprintLoad(str(D/'SmartPen.pretty'),'TI_DQA0010A_USON10_OfficialLandpattern')
for a in f.Pads():
 n=int(a.GetNumber());check(abs(p.ToMM(a.GetPosition().y)-((n-3)*.5 if n<=5 else (8-n)*.5))<1e-6,'DQA pin'+str(n)+' official pitch/order');check(abs(p.ToMM(a.GetPosition().x)-(-.4175 if n<=5 else .4175))<1e-6,'DQA pin'+str(n)+' row spacing')
 check(abs(p.ToMM(a.GetSize().x)-.565)<1e-6 and abs(p.ToMM(a.GetSize().y)-(.4 if n in [3,8] else .2))<1e-6,'DQA pin'+str(n)+' official pad dimensions')
check(len(list(f.Pads()))==10,'DQA10 pins')
f=p.FootprintLoad(str(D/'SmartPen.pretty'),'TI_DYA0002A_SOD523_OfficialLandpattern');check(len(list(f.Pads()))==2,'DYA two pads')
for a in f.Pads():
 check(abs(p.ToMM(a.GetPosition().x)-(-.74 if a.GetNumber()=='1' else .74))<1e-6,'DYA pin'+a.GetNumber()+' source position')
 check(abs(p.ToMM(a.GetSize().x)-.67)<1e-6 and abs(p.ToMM(a.GetSize().y)-.4)<1e-6,'DYA pin'+a.GetNumber()+' source land size')
check(p.ToMM(b.GetDesignSettings().GetBoardThickness())==.8,'candidate .8mm PCB');check(b.GetCopperLayerCount()==4,'candidate4layers')
pro=json.loads((D/'usb_tail_revA.kicad_pro').read_text());check(not pro['board']['design_settings']['drc_exclusions'],'no DRC exclusions')
rpt=(D/'drc.rpt').read_text();check('** Found 0 unconnected pads **' in rpt,'native0unconnected');check('** Found 0 Footprint errors **' in rpt,'native0schematic parity')
viol=re.findall(r'^\[([^]]+)\]',rpt,re.M);check(viol==['hole_clearance']*4,'four known GCT hole-clearance violations retained; NO FAB')
check('Errors 0  Warnings 0' in (D/'erc.rpt').read_text(),'newERC0/0')
res={'status':'ROUTED CANDIDATE / FOUR REAL DRC ERRORS RETAINED / NO FAB','checks':checks,'electrical_pad_shapes':count,'unconnected':0,'schematic_parity':0,'drc_violations':4,'known_issue':'GCT recommended NPTH locator to shared ground lands .1944mm vs project .25mm hole rule; needs actual fabrication DFM, not suppressed'};(D/'verification.json').write_text(json.dumps(res,indent=2));print('PASS',len(checks),'electrical/geometric checks; DRC4 retained,unconnected0,parity0; NO FAB')
with (D/'bom_candidates.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['ref','value','footprint','assembly_status'])
 for ref,c in parts.items():w.writerow([ref,c.findtext('value'),c.findtext('footprint'),'wire interface requires harness/strain relief' if ref.startswith('TP') else 'candidate no procurement'])
