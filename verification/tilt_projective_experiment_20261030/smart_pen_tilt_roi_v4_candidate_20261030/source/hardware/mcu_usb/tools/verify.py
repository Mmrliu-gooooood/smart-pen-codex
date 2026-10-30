#!/usr/bin/env python3
"""Independent handwritten electrical contract, not imported generator data.
Runs fresh KiCad ERC/XML export; rejects empty/partial hierarchy.
"""
import json,os,subprocess,xml.etree.ElementTree as ET,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parents[1]
env=os.environ.copy()
for key,tail in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:env[key]='/tmp/rebuild-kicad/'+tail
for args in [['sch','erc','--exit-code-violations','-o',str(P/'erc.rpt'),str(P/'mcu_usb.kicad_sch')],['sch','export','netlist','--format','kicadxml','-o',str(P/'mcu_usb.xml'),str(P/'mcu_usb.kicad_sch')]]:subprocess.run(['kicad-cli']+args,env=env,check=True)
r=ET.parse(P/'mcu_usb.xml').getroot();actual={}
for net in r.findall('./nets/net'):
 for n in net.findall('node'):actual[(n.get('ref'),n.get('pin'))]=net.get('name')
expected={}
def part(ref,seq):
 for pin,net in (seq.items() if isinstance(seq,dict) else enumerate(seq,1)):expected[(ref,str(pin))]=net
part('U1',{1:'RF_SIP',2:'3V3_AON',3:'3V3_AON',4:'CHIP_EN',5:'BOOT_N',6:'PICKUP_INT_N',7:'NIB_CONTACT_N',8:'STRAP_GPIO3',9:'BATTERY_ADC',10:'AON_I2C_SCL',11:'AON_I2C_SDA',12:'CAM_D0',13:'CAM_D1',14:'CAM_D2',15:'CAM_D3',16:'CAM_D4',17:'CAM_D5',18:'CAM_D6',19:'CAM_D7',20:'3V3_AON',21:'CAM_PCLK',22:'CAM_VSYNC',23:'CAM_HREF',24:'USB_EN1',25:'USB_DM_MCU',26:'USB_DP_MCU',27:'USB_EN2',28:None,29:None,30:None,31:None,32:None,33:None,34:None,35:None,36:'ILLUM_STROBE',37:'CAM_BUS_EN',38:None,39:None,40:None,41:None,42:None,43:'CAM_XCLK',44:'CAM_SCL',45:'CAM_SDA',46:'3V3_AON',47:'CAM_PWR_EN',48:'CAM_IO_EN',49:'CAM_RESET_UART_TX',50:'CAM_PWDN_UART_RX',51:'STRAP_GPIO45',52:'STRAP_GPIO46',53:None,54:None,55:'3V3_AON',56:'3V3_AON',57:'GND'})
for i,(a,b) in enumerate([('CHIP_EN','3V3_AON'),('BOOT_N','3V3_AON'),('STRAP_GPIO3','3V3_AON'),('STRAP_GPIO45','GND'),('STRAP_GPIO46','GND'),('CAM_PWR_EN','GND'),('CAM_IO_EN','GND'),('CAM_BUS_EN','GND'),('ILLUM_STROBE','GND'),('USB_CC1','GND'),('USB_CC2','GND'),('USB_DP','USB_DP_MCU'),('USB_DM','USB_DM_MCU')],1):part('R'+str(i),[a,b])
part('C1',['CHIP_EN','GND'])
for i in range(2,6):part('C'+str(i),['3V3_AON','GND'])
part('C6',['RF_SIP','GND']);part('C7',['RF_ANT','GND']);part('L1',['RF_SIP','RF_ANT']);part('AE1',['RF_ANT','GND']);part('SW1',['CHIP_EN','GND']);part('SW2',['BOOT_N','GND'])
part('U2',['USB_DP','USB_DM','GND','USB_CC1','USB_CC2',None,None,'GND',None,None]);part('D1',['VBUS_5V','GND'])
part('J1',{'A1':'GND','A4':'VBUS_5V','A5':'USB_CC1','A6':'USB_DP','A7':'USB_DM','A8':None,'A9':'VBUS_5V','A12':'GND','B1':'GND','B4':'VBUS_5V','B5':'USB_CC2','B6':'USB_DP','B7':'USB_DM','B8':None,'B9':'VBUS_5V','B12':'GND','S1':'GND'})
part('J2',['CAM_D0','CAM_D1','CAM_D2','CAM_D3','CAM_D4','CAM_D5','CAM_D6','CAM_D7','CAM_PCLK','CAM_VSYNC','CAM_HREF','CAM_XCLK','CAM_SCL','CAM_SDA','CAM_RESET_UART_TX','CAM_PWDN_UART_RX','CAM_PWR_EN','CAM_IO_EN','CAM_BUS_EN','ILLUM_STROBE'])
part('J3',['3V3_AON','GND','AON_I2C_SCL','AON_I2C_SDA','PICKUP_INT_N','NIB_CONTACT_N']);part('J4',['CAM_RESET_UART_TX','CAM_PWDN_UART_RX','GND']);part('J5',['BATTERY_ADC','GND']);part('J6',['VBUS_5V','3V3_AON','GND']);part('J7',['USB_EN1','USB_EN2','GND'])
errors=[]
for k,v in expected.items():
 got=actual.get(k)
 if v is None:
  if got is not None and not got.startswith('unconnected-'):errors.append([k,v,got])
 elif got!=v:errors.append([k,v,got])
refs={c.get('ref') for c in r.findall('./components/comp')}
assert refs=={k[0] for k in expected},(refs,{k[0] for k in expected})
# Every symbol pin must be covered, even intentional NCs.
for c in r.findall('./components/comp'):
 lp=c.find('libsource'); symbol=r.find(f'./libparts/libpart[@lib="{lp.get("lib")}"][@part="{lp.get("part")}"]')
 for pin in symbol.findall('./pins/pin'):
  assert (c.get('ref'),pin.get('num')) in expected
# Check assigned footprint electrical pin numbers (repeated shield S1 is intentional).
fp_checks={}
for c in r.findall('./components/comp'):
 fp=c.findtext('footprint')
 if not fp:continue
 lib,name=fp.split(':');path=Path('/usr/share/kicad/footprints')/(lib+'.pretty')/(name+'.kicad_mod')
 assert path.exists(),str(path)
 pads=set(re.findall(r'\(pad "([^"\n]+)"',path.read_text()))
 pins={k[1] for k in expected if k[0]==c.get('ref')}
 fp_checks[c.get('ref')]=pads==pins
 assert pads==pins,(c.get('ref'),pads,pins)
report={'date_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS' if not errors else 'FAIL','reconstruction_not_restoration':True,'component_count':len(refs),'pin_checks':len(expected),'mismatches':errors,'footprint_number_sets':fp_checks,'pcb_exists':False,'manufacturing_release':False,'sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.glob('*.kicad_sch')}}
(P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not errors
