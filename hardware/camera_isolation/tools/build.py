#!/usr/bin/env python3
"""2026-10-28 camera isolation new design, NO FAB. Editable native KiCad."""
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
  z.append(f'(instances (project "camera_isolation" (path "/{root}/{self.id}" (reference {q(ref)}) (unit 1)))) )')
  self.items.append(''.join(z));allparts.append(dict(sheet=self.name,ref=ref,value=value,lib=name,nets=nets,footprint=foot,dnp=dnp))
 def save(self):
  out=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {self.id}) (paper "A3") (title_block (title "2026-10-28 REBUILD / NO FAB") (rev "R0")) (lib_symbols '+''.join(lib[k].replace('(symbol "'+k+'"','(symbol "Pen:'+k+'"',1) for k in self.used)+')'+''.join(self.items)+')'
  (P/(self.name+'.kicad_sch')).write_text(out)
# Manufacturer pin tables: TI AXC8 RevC PW; AXC4 RevB PW; TCA9517 RevD DGK.
ax8={1:'VCCA',2:'DIR1',3:'A1',4:'A2',5:'A3',6:'A4',7:'A5',8:'A6',9:'A7',10:'A8',11:'DIR2',12:'GND',13:'GND',14:'B8',15:'B7',16:'B6',17:'B5',18:'B4',19:'B3',20:'B2',21:'B1',22:'OE_N',23:'VCCB',24:'VCCB'}
ax4={1:'VCCA',2:'1DIR',3:'2DIR',4:'1A1',5:'1A2',6:'2A1',7:'2A2',8:'GND',9:'GND',10:'2B2',11:'2B1',12:'1B2',13:'1B1',14:'2OE_N',15:'1OE_N',16:'VCCB'}
tca={1:'VCCA',2:'SCLA',3:'SDAA',4:'GND',5:'EN',6:'SDAB',7:'SCLB',8:'VCCB'}
for name,pins in [('SN74AXC8T245PWR',ax8),('SN74AXC4T245PWR',ax4),('TCA9517DGKR',tca)]:
 sym(name,[(i,n,'power_in' if n in ['VCCA','VCCB','GND'] else 'input' if ('DIR' in n or 'OE' in n or n=='EN') else 'bidirectional') for i,n in pins.items()])
for name in ['R','C','OPEN_LINK']:sym(name,[(1,'1','passive'),(2,'2','passive')])
sym('PMV30UN2',[(1,'G','input'),(2,'S','passive'),(3,'D','passive')])
for n in [2,18,20]:sym('PORT'+str(n),[(i,str(i),'passive') for i in range(1,n+1)])
sym('PWR_FLAG',[(1,'pwr','power_out')])
# Use conventional IEC resistor/capacitor graphics without changing electrical endpoints.
for name in ['R','C']:
 body=f'(symbol "{name}_0_1" '
 def line(x1,y1,x2,y2):return f'(polyline (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0.254) (type default)) (fill (type none)))'
 if name=='R':body+='(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))'+line(-7.62,0,-2.54,0)+line(2.54,0,7.62,0)
 else:body+=line(-1.016,-2.54,-1.016,2.54)+line(1.016,-2.54,1.016,2.54)+line(-7.62,0,-1.016,0)+line(1.016,0,7.62,0)
 body+=')'
 start=lib[name].index(f'(symbol "{name}_0_1"');end=lib[name].index(f'(symbol "{name}_1_1"')
 lib[name]=lib[name][:start]+body+lib[name][end:]
 # pin names/numbers hidden for passives; reference/value remain
 lib[name]=lib[name].replace('(pin_names (offset 1.016))','(pin_names hide) (pin_numbers hide)')
a=Sheet('dvp_translation');b=Sheet('controls_sccb');c=Sheet('safe_bias_interfaces')
def part(s,name,ref,value,x,y,nets,fp='',dnp=False):s.part(name,ref,value,x,y,{str(k):v for k,v in nets.items()},fp,dnp)
def rc(s,name,ref,val,x,y,one,two):part(s,name,ref,val,x,y,{1:one,2:two},'Resistor_SMD:R_0603_1608Metric' if name=='R' else 'Capacitor_SMD:C_0603_1608Metric')
a.text('NEW 2026-10-28 / NO FAB. Fixed DVP B(1V8 sensor) -> A(3V3 MCU). NO 30-pin FPC assumed.',205,15)
n={1:'3V3_AON',2:'GND',11:'GND',12:'GND',13:'GND',22:'CAM_ISO_OE_N',23:'SENS_VIO_1V8',24:'SENS_VIO_1V8'}
for i in range(8):n[3+i]=f'CAM_D{i}';n[21-i]=f'SENS_D{i}'
part(a,'SN74AXC8T245PWR','U1','SN74AXC8T245PWR',90,65,n,'Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm')
n={1:'3V3_AON',2:'GND',3:'GND',4:'CAM_PCLK',5:'CAM_VSYNC',6:'CAM_HREF',7:None,8:'GND',9:'GND',10:'UNUSED_B_INPUT',11:'SENS_HREF',12:'SENS_VSYNC',13:'SENS_PCLK',14:'CAM_ISO_OE_N',15:'CAM_ISO_OE_N',16:'SENS_VIO_1V8'}
part(a,'SN74AXC4T245PWR','U2','SN74AXC4T245PWR',285,65,n,'Package_SO:TSSOP-16_4.4x5mm_P0.65mm')
# Power is external: these flags assert the defined source boundary only.
for i,net in enumerate(['3V3_AON','SENS_VIO_1V8','GND']):part(a,'PWR_FLAG',f'#FLG0{i+1}','EXTERNAL_QUALIFIED_SUPPLY',65+i*110,125,{1:net})
for i,(net,x,y) in enumerate([('3V3_AON',65,160),('SENS_VIO_1V8',175,160),('3V3_AON',285,160),('SENS_VIO_1V8',65,195)]):rc(a,'C','C'+str(i+1),'100n X7R',x,y,net,'GND')
rc(a,'R','R6','10k 1%',175,195,'UNUSED_B_INPUT','GND')
rc(a,'R','R7','10k 1%',285,195,'UNUSED_A_INPUT','GND')
a.text('U2 unused B input biased GND; corresponding A output intentionally NC. Route data/PCLK as timing group.',205,235)
a.text('Translator speed rating does NOT qualify ESP32-S3 72MHz capture. Verify setup/hold/skew on actual PCB.',205,245)
b.text('Hardware-default disable: OE_N pull-up + NMOS. JP1/JP2 OPEN/DNP until interface qualification.',205,15)
n={1:'3V3_AON',2:'3V3_AON',3:'3V3_AON',4:'CAM_XCLK',5:'CAM_RESET_UART_TX',6:'CAM_PWDN_UART_RX',7:'UNUSED_A_INPUT',8:'GND',9:'GND',10:None,11:'SENS_TRIG_IN',12:'SENS_XSHUTDN_N',13:'SENS_EXTCLK',14:'CAM_ISO_OE_N',15:'CAM_ISO_OE_N',16:'SENS_VIO_1V8'}
part(b,'SN74AXC4T245PWR','U3','SN74AXC4T245PWR',85,60,n,'Package_SO:TSSOP-16_4.4x5mm_P0.65mm')
part(b,'TCA9517DGKR','U4','TCA9517DGKR',280,60,{1:'SENS_VIO_1V8',2:'SENS_SCL',3:'SENS_SDA',4:'GND',5:'SCCB_EN_SAFE',6:'CAM_SDA',7:'CAM_SCL',8:'3V3_AON'},'Package_SO:VSSOP-8_3x3mm_P0.65mm')
part(b,'OPEN_LINK','JP1','DNP_IO_COMMISSION',65,115,{1:'CAM_IO_EN',2:'IO_ENABLE_LINK'},'',True)
rc(b,'R','R1','1k 1%',175,115,'IO_ENABLE_LINK','ISO_GATE')
part(b,'PMV30UN2','Q1','PMV30UN2',280,115,{1:'ISO_GATE',2:'GND',3:'CAM_ISO_OE_N'},'Package_TO_SOT_SMD:SOT-23')
rc(b,'R','R2','100k 1%',65,145,'ISO_GATE','GND');rc(b,'R','R3','10k 1%',175,145,'CAM_ISO_OE_N','3V3_AON')
part(b,'OPEN_LINK','JP2','DNP_SCCB_COMMISSION',280,145,{1:'CAM_BUS_EN',2:'SCCB_ENABLE_LINK'},'',True)
rc(b,'R','R4','100R 1%',65,175,'SCCB_ENABLE_LINK','SCCB_EN_SAFE');rc(b,'R','R5','4.7k 1%',175,175,'SCCB_EN_SAFE','GND')
for i,(net,x,y) in enumerate([('3V3_AON',280,175),('SENS_VIO_1V8',65,205),('3V3_AON',175,205),('SENS_VIO_1V8',280,205)],5):rc(b,'C','C'+str(i),'100n X7R',x,y,net,'GND')
b.text('SCCB A=1V8/B=3V3. EN has internal pull-up current: external 4.7k down, NOT 100k.',205,240)
b.text('Shared UART must be quiescent before closing links/enabling isolation; no charger controls on UART.',205,250)
c.text('SEMANTIC interfaces ONLY. No connector footprint, no old-module mapping, no permission to attach camera.',205,15)
host=[f'CAM_D{i}' for i in range(8)]+['CAM_PCLK','CAM_VSYNC','CAM_HREF','CAM_XCLK','CAM_RESET_UART_TX','CAM_PWDN_UART_RX','CAM_SCL','CAM_SDA','CAM_IO_EN','CAM_BUS_EN','3V3_AON','GND']
sensor=[f'SENS_D{i}' for i in range(8)]+['SENS_PCLK','SENS_VSYNC','SENS_HREF','SENS_EXTCLK','SENS_XSHUTDN_N','SENS_TRIG_IN','SENS_SCL','SENS_SDA','SENS_VIO_1V8','GND']
part(c,'PORT20','J1','HOST_3V3_SEMANTIC',65,60,dict(enumerate(host,1)))
part(c,'PORT18','J2','SENSOR_1V8_SEMANTIC_NOT_FPC',280,60,dict(enumerate(sensor,1)))
# Bias both sides because input buffers remain active even with outputs disabled.
bias=host[:14]+sensor[:14]
for i,net in enumerate(bias):rc(c,'R','R'+str(i+10),'4.7k 1% RESET_CANDIDATE' if net=='SENS_XSHUTDN_N' else '100k 1%',50+(i%4)*100,115+(i//4)*18,net,'GND')
for i,net in enumerate(['CAM_SCL','CAM_SDA','SENS_SCL','SENS_SDA']):rc(c,'R','R'+str(40+i),'10k 1% INITIAL_100kHz',50+i*100,245,net,'3V3_AON' if i<2 else 'SENS_VIO_1V8')
c.text('SENS_VIO is the SAME verified rail as actual sensor IO, not a separate injected supply. Reset pull must be qualified.',205,270)
for s in [a,b,c]:s.save()
rootitems=''
for i,s in enumerate([a,b,c]):rootitems+=f'(sheet (at 70 {45+i*45}) (size 90 25) (stroke (width 0.1524) (type default)) (fill (color 0 0 0 0)) (uuid {s.id}) (property "Sheetname" {q(s.name)} (at 70 {44+i*45} 0) {eff()}) (property "Sheetfile" {q(s.name+".kicad_sch")} (at 70 {72+i*45} 0) {eff()}) (instances (project "camera_isolation" (path "/{root}" (page "{i+2}")))))'
(P/'camera_isolation.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A4") (lib_symbols) {rootitems})')
(P/'Pen.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")'+''.join(lib.values())+')')
(P/'sym-lib-table').write_text('(sym_lib_table (lib (name "Pen") (type "KiCad") (uri "${KIPRJMOD}/Pen.kicad_sym") (options "") (descr "New camera isolation")))')
(P/'camera_isolation.kicad_pro').write_text(json.dumps({'meta':{'filename':'camera_isolation.kicad_pro','version':1}},indent=2))
(P/'design_manifest.json').write_text(json.dumps(allparts,indent=2))
print('New source generated; run independent verify before reporting pass.')
