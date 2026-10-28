#!/usr/bin/env python3
"""2026-10-28 reconstruction, NOT restored original. Editable native KiCad."""
import json,uuid
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def uid(): return str(uuid.uuid4())
def q(s): return json.dumps(str(s))
def eff(n=1): return f'(effects (font (size {n} {n})))'
lib={}; specs={}
def sym(name,pins,kind='box'):
    # pins: number,name,electrical type; split across left/right
    n=len(pins); left=(n+1)//2; rows=left; h=(rows+1)*2.54/2; w=15.24 if n>10 else 7.62
    lines=[f'(symbol {q(name)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',f'(property "Reference" "U" (at 0 {h+3} 0) {eff()})',f'(property "Value" {q(name)} (at 0 {h+1.5} 0) {eff()})',f'(symbol {q(name+"_0_1")} (rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))']
    # replace final close: primitive symbol closed only, parent remains
    # primitive symbol already closed
    coords={}; pp=[]
    for i,(num,pn,typ) in enumerate(pins):
        side=i<left; row=i if side else i-left; x=-w-2.54 if side else w+2.54; y=h-2.54-row*2.54; a=0 if side else 180
        coords[str(num)]=(x,y,a)
        pp.append(f'(pin {typ} line (at {x} {y} {a}) (length 2.54) (name {q(pn)} {eff(.9)}) (number {q(num)} {eff(.9)}))')
    lines.append(f'(symbol {q(name+"_1_1")} '+''.join(pp)+'))')
    lib[name]='\n'.join(lines);specs[name]=coords

power={2,3,20,46,55,56};nc=set(range(30,36))|{53,54};mem={28,38,39,40,41,42}
names={1:'LNA_IN',2:'VDD3P3',3:'VDD3P3',4:'CHIP_PU',20:'VDD3P3_RTC',21:'GPIO15_XTAL32K_P',22:'GPIO16_XTAL32K_N',28:'SPICS1_PSRAM',29:'VDD_SPI',36:'GPIO48_SPICLK_N',37:'GPIO47_SPICLK_P',43:'GPIO38',44:'GPIO39_MTCK',45:'GPIO40_MTDO',46:'VDD3P3_CPU',47:'GPIO41_MTDI',48:'GPIO42_MTMS',49:'GPIO43_U0TXD',50:'GPIO44_U0RXD',51:'GPIO45',52:'GPIO46',55:'VDDA',56:'VDDA',57:'GND'}
for pin in range(5,20):names[pin]='GPIO'+str(pin-5)
for pin in range(23,28):names[pin]='GPIO'+str(pin-6)
for pin in range(38,43):names[pin]='GPIO'+str(pin-5)+'_PSRAM'
for pin in nc:names[pin]='NC'
sym('ESP32-S3-PICO-1-N8R8',[(i,names[i],'power_in' if i in power|{57} else 'power_out' if i==29 else 'no_connect' if i in nc else 'input' if i==4 else 'bidirectional') for i in range(1,58)])
for name in ['R','C','L','SW_NO','TVS_BIDIR'] :sym(name,[(1,'1','passive'),(2,'2','passive')])
for n in [1,2,3,4,6,20]:sym('PORT'+str(n),[(i,str(i),'passive') for i in range(1,n+1)])
sym('TPD4E05U06DQAR',[(i,'GND' if i in [3,8] else 'NC' if i in [6,7,9,10] else 'IO'+str(i),'no_connect' if i in [6,7,9,10] else 'passive') for i in range(1,11)])
usb=['A1','A4','A5','A6','A7','A8','A9','A12','B1','B4','B5','B6','B7','B8','B9','B12','S1']
sym('USB4105-GF-A16P',[(x,'GND' if x in ['A1','A12','B1','B12','S1'] else 'VBUS' if x in ['A4','A9','B4','B9'] else {'A5':'CC1','B5':'CC2','A6':'D+','B6':'D+','A7':'D-','B7':'D-','A8':'SBU1','B8':'SBU2'}[x],'passive') for x in usb])
sym('PWR_FLAG',[(1,'pwr','power_out')])
root=uid(); allparts=[]
class Sheet:
 def __init__(self,name):self.name=name;self.id=uid();self.items=[];self.used=set()
 def text(self,s,x,y):self.items.append(f'(text {q(s)} (at {x} {y} 0) {eff(1.27)} (uuid {uid()}))')
 def part(self,name,ref,value,x,y,nets,foot='',dnp=False):
  x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
  self.used.add(name);i=uid();z=[f'(symbol (lib_id "Pen:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid {i})',f'(property "Reference" {q(ref)} (at {x} {y-((len(specs[name])+2)//2)*1.27-5} 0) {eff()})',f'(property "Value" {q(value)} (at {x} {y-((len(specs[name])+2)//2)*1.27-3} 0) {eff()})',f'(property "Footprint" {q(foot)} (at {x} {y} 0) (effects (font (size 1 1)) hide))']
  for pn,(dx,dy,a) in specs[name].items():
   z.append(f'(pin {q(pn)} (uuid {uid()}))');px=x+dx;py=y-dy;net=nets.get(pn)
   if net is None:self.items.append(f'(no_connect (at {px} {py}) (uuid {uid()}))')
   else:
    ex=px-5.08 if a==0 else px+5.08
    self.items.append(f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type default)) (uuid {uid()}))')
    self.items.append(f'(global_label {q(net)} (shape bidirectional) (at {ex} {py} {180 if a==0 else 0}) {eff(.9)[:-1]+(" (justify right))" if a==0 else " (justify left))")} (uuid {uid()}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {ex} {py} 0) (effects (font (size 1 1)) hide)))')
  z.append(f'(instances (project "mcu_usb" (path "/{root}/{self.id}" (reference {q(ref)}) (unit 1)))) )')
  self.items.append(''.join(z));allparts.append(dict(sheet=self.name,ref=ref,value=value,lib=name,nets=nets,footprint=foot,dnp=dnp))
 def save(self):
  out=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {self.id}) (paper "A3") (title_block (title "2026-10-28 REBUILD / NO FAB") (rev "R0")) (lib_symbols '+''.join(lib[k].replace('(symbol "'+k+'"','(symbol "Pen:'+k+'"',1) for k in self.used)+')'+''.join(self.items)+')'
  (P/(self.name+'.kicad_sch')).write_text(out)
core=Sheet('mcu_core');entry=Sheet('usb_entry')
# Deliberately re-proposed assignment; not claimed byte-identical to lost design.
gpio={1:'PICKUP_INT_N',2:'NIB_CONTACT_N',4:'BATTERY_ADC',5:'AON_I2C_SCL',6:'AON_I2C_SDA',7:'CAM_D0',8:'CAM_D1',9:'CAM_D2',10:'CAM_D3',11:'CAM_D4',12:'CAM_D5',13:'CAM_D6',14:'CAM_D7',15:'CAM_PCLK',16:'CAM_VSYNC',17:'CAM_HREF',18:'USB_EN1',19:'USB_DM_MCU',20:'USB_DP_MCU',21:'USB_EN2',38:'CAM_XCLK',39:'CAM_SCL',40:'CAM_SDA',41:'CAM_PWR_EN',42:'CAM_IO_EN',43:'CAM_RESET_UART_TX',44:'CAM_PWDN_UART_RX',47:'CAM_BUS_EN',48:'ILLUM_STROBE'}
padgpio={i:i-5 for i in range(5,20)}|{21:15,22:16}|{i:i-6 for i in range(23,28)}|{36:48,37:47,43:38,44:39,45:40,47:41,48:42,49:43,50:44,51:45,52:46}
nets={str(i):'3V3_AON' for i in power};nets.update({'1':'RF_SIP','4':'CHIP_EN','5':'BOOT_N','8':'STRAP_GPIO3','51':'STRAP_GPIO45','52':'STRAP_GPIO46','57':'GND'})
for pad,g in padgpio.items():
 if g in gpio:nets[str(pad)]=gpio[g]
core.text('REBUILT 2026-10-28. Camera connector is logical 3V3-side ONLY; isolation NOT implemented.',195,15)
core.part('ESP32-S3-PICO-1-N8R8','U1','ESP32-S3-PICO-1-N8R8',80,80,nets)
def passive(s,name,ref,val,x,y,a,b,dnp=False):s.part(name,ref,val,x,y,{'1':a,'2':b},'Resistor_SMD:R_0603_1608Metric' if name=='R' else 'Capacitor_SMD:C_0603_1608Metric' if name=='C' else '',dnp)
for i,(net,to) in enumerate([('CHIP_EN','3V3_AON'),('BOOT_N','3V3_AON'),('STRAP_GPIO3','3V3_AON'),('STRAP_GPIO45','GND'),('STRAP_GPIO46','GND')]):passive(core,'R','R'+str(i+1),'10k 1%',170+i%3*75,40+i//3*35,net,to)
passive(core,'C','C1','1u',170,110,'CHIP_EN','GND')
passive(core,'SW_NO','SW1','RESET',245,110,'CHIP_EN','GND');passive(core,'SW_NO','SW2','BOOT',320,110,'BOOT_N','GND')
for i,v in enumerate(['22u','100n','100n','100n']):passive(core,'C','C'+str(i+2),v,60+i*75,155,'3V3_AON','GND')
for i,net in enumerate(['CAM_PWR_EN','CAM_IO_EN','CAM_BUS_EN','ILLUM_STROBE']):passive(core,'R','R'+str(i+6),'100k 1%',60+i*75,185,net,'GND')
passive(core,'L','L1','RF_MATCH_TBD',70,220,'RF_SIP','RF_ANT');passive(core,'C','C6','DNP RF_TUNE',170,220,'RF_SIP','GND',True);passive(core,'C','C7','DNP RF_TUNE',270,220,'RF_ANT','GND',True)
core.part('PORT2','AE1','ANTENNA_TBD_NO_FOOTPRINT',355,220,{'1':'RF_ANT','2':'GND'})
core.text('VDD_SPI pad29 intentionally externally NC per PICO reference. PSRAM pins not GPIO.',195,255)
core.text('EN RC, RF matching and bypass BOM need bench/layout qualification. No MCU PCB.',195,262)
entry.text('USB-C sink / native USB recovery. NO FAB. No PD or sustained overvoltage protection.',195,15)
un={x:'GND' if x in ['A1','A12','B1','B12','S1'] else 'VBUS_5V' if x in ['A4','A9','B4','B9'] else {'A5':'USB_CC1','B5':'USB_CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM'}.get(x) for x in usb}
entry.part('USB4105-GF-A16P','J1','USB4105-GF-A16P',65,55,un,'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
entry.part('TPD4E05U06DQAR','U2','TPD4E05U06DQAR',170,50,{'1':'USB_DP','2':'USB_DM','3':'GND','4':'USB_CC1','5':'USB_CC2','8':'GND'},'Package_SON:USON-10_2.5x1.0mm_P0.5mm')
passive(entry,'R','R10','5.1k 1%',270,35,'USB_CC1','GND');passive(entry,'R','R11','5.1k 1%',350,35,'USB_CC2','GND')
passive(entry,'R','R12','22R SI_TBD',270,65,'USB_DP','USB_DP_MCU');passive(entry,'R','R13','22R SI_TBD',350,65,'USB_DM','USB_DM_MCU')
entry.part('TVS_BIDIR','D1','TPD1E10B06DYAR',65,100,{'1':'VBUS_5V','2':'GND'},'Diode_SMD:D_SOD-523')
cam=[f'CAM_D{i}' for i in range(8)]+['CAM_PCLK','CAM_VSYNC','CAM_HREF','CAM_XCLK','CAM_SCL','CAM_SDA','CAM_RESET_UART_TX','CAM_PWDN_UART_RX','CAM_PWR_EN','CAM_IO_EN','CAM_BUS_EN','ILLUM_STROBE']
entry.part('PORT20','J2','LOGICAL_CAMERA_ONLY_NOT_FPC',175,135,{str(i+1):n for i,n in enumerate(cam)})
entry.part('PORT6','J3','PICKUP_INTERNAL',315,120,dict(zip(map(str,range(1,7)),['3V3_AON','GND','AON_I2C_SCL','AON_I2C_SDA','PICKUP_INT_N','NIB_CONTACT_N'])))
entry.part('PORT3','J4','UART_TEST_CAMERA_OFF_ONLY',65,155,{'1':'CAM_RESET_UART_TX','2':'CAM_PWDN_UART_RX','3':'GND'})
entry.part('PORT2','J5','ADC_SAFE_EXTERNAL_ONLY',65,190,{'1':'BATTERY_ADC','2':'GND'})
entry.part('PORT3','J6','POWER_CORE',175,195,{'1':'VBUS_5V','2':'3V3_AON','3':'GND'})
entry.part('PORT3','J7','CHARGER_MODE',315,185,{'1':'USB_EN1','2':'USB_EN2','3':'GND'})
entry.part('PWR_FLAG','#FLG01','PWR_FLAG',65,230,{'1':'3V3_AON'})
entry.part('PWR_FLAG','#FLG02','PWR_FLAG',175,230,{'1':'GND'})
entry.text('Flags represent power supplied by separate power_core. No physical interconnect defined.',195,255)
entry.text('Do not connect BATTERY_ADC directly to pack. Camera IO/rails/isolators remain unresolved.',195,262)
for s in [core,entry]:s.save()
rootitems=''
for i,s in enumerate([core,entry]):rootitems+=f'(sheet (at 70 {65+i*45}) (size 90 25) (stroke (width 0.1524) (type default)) (fill (color 0 0 0 0)) (uuid {s.id}) (property "Sheetname" {q(s.name)} (at 70 {64+i*45} 0) {eff()}) (property "Sheetfile" {q(s.name+".kicad_sch")} (at 70 {92+i*45} 0) {eff()}) (instances (project "mcu_usb" (path "/{root}" (page "{i+2}")))))'
(P/'mcu_usb.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A4") (lib_symbols) {rootitems})')
(P/'Pen.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")'+''.join(lib.values())+')')
(P/'sym-lib-table').write_text('(sym_lib_table (lib (name "Pen") (type "KiCad") (uri "${KIPRJMOD}/Pen.kicad_sym") (options "") (descr "2026-10-28 reconstruction")))')
(P/'mcu_usb.kicad_pro').write_text(json.dumps({'meta':{'filename':'mcu_usb.kicad_pro','version':1}},indent=2))
(P/'connectivity_manifest.json').write_text(json.dumps(allparts,indent=2))
(P/'gpio_assignment.json').write_text(json.dumps({'rebuild_date':'2026-10-28','not_original_restoration':True,'gpio_to_net':gpio,'pad_to_gpio':padgpio},indent=2))
print('Native source generated; NOT YET VALIDATED')
